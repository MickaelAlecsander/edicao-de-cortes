# -*- coding: utf-8 -*-
"""Transcreve trechos da fonte com o Whisper LOCAL (faster-whisper), palavra a palavra, em tempo ABSOLUTO na fonte.

    python transcrever_local.py <fonte> <saida.json> 00:00-00:20 1:25:00-1:31:30 ... [--modelo large-v3] [--cpu]
                                [--texto texto_conferido.txt]

Substitui o antigo transcrever.py (que usava a API). A saída é a mesma: uma lista [{"w", "s", "e"}] em segundos da
FONTE, nunca do clipe cortado. É ela que o pausas.py (--palavras), o cortar.py e o legendas.py leem.

O Whisper dá o TEXTO, não a prova de tempo. No C29 o large-v3 pôs o "Mas" 1,4 s antes do real, o "Família" antes de ser
dito e escreveu "Já ganhei" no lugar de "Joga aí": cada erro de tempo virou uma ponta de corte errada. Por isso:
  · a ponta de corte sai do vale de energia e do alinhador forçado MMS_FA (pausas.py, alinhar.py), nunca daqui;
  · o texto é conferido no ouvido e corrigido (nomes, números, siglas) no TEXTO do pos_cortar.py de cada corte;
  · --texto <arquivo>: o texto já conferido (o do roteiro) passa por cima da escrita do Whisper, palavra a palavra
    (difflib, função alinhar): a escrita vem do arquivo, o tempo do Whisper. Use antes do pausas.py quando o Whisper
    errou nomes ("Marcos Queber" → "Mark Zuckerberg"), para o alinhador não receber palavra que não foi dita.
Sem arquivo temporário: o áudio vai do ffmpeg direto para a memória, então dá para rodar dois ao mesmo tempo (o antigo
usava um wav de nome fixo, e dois em paralelo misturaram o C77 com o C78).
--cpu força a CPU (int8); sem ele, usa a GPU se houver. --modelo: large-v3 (padrão), medium para uma 1ª leitura rápida.
Em CPU o large-v3 leva da ordem de 1 a 2× o tempo do áudio: transcreva só os trechos candidatos, não a live inteira.
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
import unicodedata

import numpy as np

SR = 16000
FOLGA = (0.5, 1.5)   # silêncio posto antes e depois do trecho: sem folga no fim, o Whisper inventa a última palavra (C01)
_modelos = {}


def seg(s):
    """"1:25" → 85; "1:25:00" → 5100; "12.5" → 12.5"""
    p = [float(x) for x in s.split(":")]
    return p[0] if len(p) == 1 else p[0] * 60 + p[1] if len(p) == 2 else p[0] * 3600 + p[1] * 60 + p[2]


def audio(src, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % a, "-t", "%.3f" % (b - a), "-i", src, "-vn", "-ac", "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def modelo(nome="large-v3", cpu=False):
    if (nome, cpu) not in _modelos:
        import ctranslate2
        from faster_whisper import WhisperModel
        gpu = not cpu and ctranslate2.get_cuda_device_count() > 0
        _modelos[(nome, cpu)] = WhisperModel(nome, device="cuda" if gpu else "cpu", compute_type="float16" if gpu else "int8")
    return _modelos[(nome, cpu)]


def ouvir(src, a, b, nome="large-v3", cpu=False):
    """[{w, s, e}] do trecho [a, b] de src, em segundos absolutos de src."""
    x = audio(src, a, b)
    x = np.concatenate([np.zeros(int(FOLGA[0] * SR), np.float32), x, np.zeros(int(FOLGA[1] * SR), np.float32)])
    segs, _ = modelo(nome, cpu).transcribe(x, language="pt", word_timestamps=True, condition_on_previous_text=False)
    out = []
    for s in segs:
        for w in s.words or []:
            t0 = min(max(a, a + w.start - FOLGA[0]), b)
            t1 = min(max(t0, a + w.end - FOLGA[0]), b)
            if w.word.strip():
                out.append({"w": w.word.strip(), "s": round(t0, 3), "e": round(t1, 3)})
    return out


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def alinhar(tempos, texto, fim):
    """tempos: [{w, s, e}] com tempo (Whisper); texto: o texto certo. Devolve [{w, s, e}] com a escrita do texto.

    Mesma função do antigo transcrever.py (lá o texto era o do gpt-4o): palavra igual leva o tempo dela; palavra que só o
    texto tem ganha o espaço entre as vizinhas; 1 ou 2 palavras soltas que só o Whisper "ouviu" saem (alucinação), mas 3
    ou mais ficam (o texto pode ter pulado uma frase)."""
    gw = [w for w in texto.split() if norm(w)]
    a, g = [norm(t["w"]) for t in tempos], [norm(w) for w in gw]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, g, autojunk=False).get_opcodes():
        if op == "equal":
            out += [{"w": gw[j1 + k], "s": tempos[i1 + k]["s"], "e": tempos[i1 + k]["e"]} for k in range(i2 - i1)]
        elif op == "delete":
            if i2 - i1 >= 3:
                out += [{"w": tempos[k]["w"].strip(), "s": tempos[k]["s"], "e": tempos[k]["e"]} for k in range(i1, i2)]
            continue
        elif op == "replace" and (i2 - i1) >= (j2 - j1) + 3:
            out += [{"w": tempos[k]["w"].strip(), "s": tempos[k]["s"], "e": tempos[k]["e"]} for k in range(i1, i2)]
        else:   # replace: o vão das palavras trocadas é dividido pelas letras; insert: o vão entre as vizinhas
            if op == "replace":
                s0, e0 = tempos[i1]["s"], tempos[i2 - 1]["e"]
            else:
                s0 = out[-1]["e"] if out else (tempos[0]["s"] - 0.3 if tempos else 0)
                e0 = tempos[i1]["s"] if i1 < len(tempos) else fim
                if e0 - s0 < 0.08 * (j2 - j1) and out:   # sem espaço: divide a palavra anterior
                    s0 = (out[-1]["s"] + out[-1]["e"]) / 2
                    out[-1]["e"] = s0
            letras = [max(1, len(g[j])) for j in range(j1, j2)]
            t = s0
            for j, n in zip(range(j1, j2), letras):
                d = (e0 - s0) * n / sum(letras)
                out.append({"w": gw[j], "s": t, "e": t + d})
                t += d
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Whisper local palavra a palavra, tempo absoluto na fonte (ver o topo do arquivo).")
    ap.add_argument("fonte")
    ap.add_argument("saida", help="palavras.json: [{w, s, e}]")
    ap.add_argument("trechos", nargs="+", help="ini-fim na fonte: 00:00-00:20 1:25:00-1:31:30 (ou segundos)")
    ap.add_argument("--modelo", default="large-v3")
    ap.add_argument("--cpu", action="store_true", help="força a CPU (int8)")
    ap.add_argument("--texto", help="arquivo com o texto conferido: a escrita vem dele, o tempo do Whisper")
    arg = ap.parse_args()
    palavras = []
    for f in arg.trechos:
        a, b = (seg(x) for x in f.split("-"))
        ws = ouvir(arg.fonte, a, b, arg.modelo, arg.cpu)
        palavras += ws
        print("ok %.1f–%.1f: %d palavras" % (a, b, len(ws)), flush=True)
    if arg.texto and palavras:
        palavras = [{"w": w["w"], "s": round(w["s"], 3), "e": round(w["e"], 3)}
                    for w in alinhar(palavras, open(arg.texto, encoding="utf-8").read(), palavras[-1]["e"])]
    json.dump(palavras, open(arg.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("%d palavras → %s" % (len(palavras), arg.saida))


def _teste():
    t = [{"w": "ja", "s": 0.0, "e": 0.2}, {"w": "ganhei", "s": 0.2, "e": 0.6}, {"w": "quatro", "s": 0.7, "e": 1.0}, {"w": "vezes", "s": 1.0, "e": 1.3}]
    r = alinhar(t, "Joga aí quatro vezes, tarará", 2.0)
    assert [x["w"] for x in r] == ["Joga", "aí", "quatro", "vezes,", "tarará"], r
    assert abs(r[2]["s"] - 0.7) < 1e-9 and r[4]["s"] >= 1.3
    t2 = [{"w": x, "s": i, "e": i + 0.5} for i, x in enumerate("todas as politicas publicas sao estupidas se voce".split())]
    r2 = alinhar(t2, "Se você", 9.0)
    assert [x["w"] for x in r2][:2] == ["todas", "as"] and r2[-1]["w"] == "você", r2
    t3 = [{"w": x, "s": i, "e": i + 0.5} for i, x in enumerate("1700 voce ganha um salario pronto ele emprega".split())]
    r3 = alinhar(t3, "1.700. Ele empresta", 9.0)
    assert "salario" in [x["w"] for x in r3], r3
    assert seg("1:25") == 85 and seg("1:25:00") == 5100 and seg("12.5") == 12.5


_teste()

if __name__ == "__main__":
    main()
