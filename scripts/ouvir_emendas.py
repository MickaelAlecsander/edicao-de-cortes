# -*- coding: utf-8 -*-
"""Ouve cada EMENDA do áudio montado com o Whisper local e confere no envelope e no alinhador. Substitui o ouvir_corte.py.

    python ouvir_emendas.py cortes/<slug> [assets/raul_bruto.wav] [--lado 2.5] [--modelo large-v3] [--cpu]

Roda LOGO DEPOIS do cortar.py e do pos_cortar.py, no áudio montado, antes de qualquer render (o render leva minutos; isto,
segundos por emenda). Achado real = mexer na ponta, cortar de novo, ouvir de novo e só depois renderizar.

Por emenda (a entrada de cada bloco no assets/tempos.json):
  1. janela de ±--lado s em volta da emenda, presa numa pausa de verdade (150 ms abaixo de −45 dB) quando houver: com a
     janela cortando palavra na ponta, o ouvido acusava a palavra que o ARQUIVO cortou, não a emenda (C26, C27);
  2. o Whisper local transcreve a janela, e o texto ouvido perto da emenda é comparado com as palavras esperadas (as do
     tempos.json, que o pos_cortar.py tirou do roteiro). Número vai por extenso dos dois lados ("71%" = "setenta e um por
     cento"), para não acusar só a escrita;
  3. 2ª conferência, a que decide: o silêncio na emenda (envelope de 10 ms abaixo de −40 dB) e o alinhador MMS_FA com o
     texto esperado: palavra com letra antes E depois da emenda = palavra que ATRAVESSA = comida de um lado.
Como ler:
  ✅ ouvido igual ao esperado, silêncio na emenda, nada atravessa;
  ⚠ … REAL: «x» atravessa a emenda → mexer na ponta (a pausa de verdade, antes da palavra SEGUINTE);
  ⚠ … voz na emenda (menos de 60 ms abaixo de −40 dB) → conferir no envelope (pausas.py <arquivo> <t> --perfil);
  ⚠ … provável FALSO ALARME → o Whisper ouviu diferente, mas há silêncio e nada atravessa: segue;
  · emenda seca (menos de 200 ms de silêncio entre frases) → soa colado (C29: "Família | Cara" com 60 ms): início no
    meio da pausa ou "respiro" no bloco de antes.
O Whisper COMPLETA palavra comida (no C26 "confirmou" o "inves|tir" que tinha ido ao ar comido) e inventa conectivo
("Então", "Mas", "E") no começo de trecho: o ✅ dele só vale junto com as travas do cortar.py e o alinhador. Um ⚠ se
descarta com o envelope, nunca "porque o vale é fundo" (C26: o "minús|culo" foi cortado num vale de −49 dB).
Sai com código 1 se houver REAL ou se uma emenda não pôde ser ouvida.
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcrever_local import norm, ouvir  # noqa: E402

try:
    import alinhar as AL  # noqa: E402
except (ImportError, OSError):   # sem torch/torchaudio: fica só o Whisper e o envelope
    AL = None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Confere as emendas do áudio montado (ver o topo do arquivo).")
    ap.add_argument("pasta")
    ap.add_argument("audio", nargs="?", default="assets/raul_bruto.wav")
    ap.add_argument("--lado", type=float, default=2.5, help="segundos de cada lado da emenda")
    ap.add_argument("--modelo", default="large-v3")
    ap.add_argument("--cpu", action="store_true")
    arg = ap.parse_args()
    pasta = os.path.abspath(arg.pasta)
    final = os.path.join(pasta, arg.audio)
    blocos = json.load(open(os.path.join(pasta, "assets", "tempos.json"), encoding="utf-8"))["blocos"]
    palavras = [w for b in blocos for w in b["palavras"]]
    extenso = AL.por_extenso if AL else (lambda x: x)

    def db10(a, b):
        """dB a cada 10 ms entre a e b no áudio montado."""
        a = max(0.0, a)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % a, "-t", "%.3f" % (b - a), "-i", final, "-ac", "1",
                              "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        x = x[:len(x) // 160 * 160].reshape(-1, 160)
        return 20 * np.log10(np.sqrt((x ** 2).mean(axis=1)) + 1e-9)

    def pausa(a, b, primeira):
        """Meio da primeira (ou última) pausa de 150 ms ou mais abaixo de −45 dB entre a e b; sem pausa, None."""
        d, runs, ini = list(db10(a, b)) + [0.0], [], None
        for k, v in enumerate(d):
            if v < -45 and ini is None:
                ini = k
            elif v >= -45 and ini is not None:
                if k - ini >= 15:
                    runs.append((ini, k))
                ini = None
        if not runs:
            return None
        r = runs[0] if primeira else runs[-1]
        return max(0.0, a) + (r[0] + r[1]) / 2 * 0.01

    def toks(ws):
        """[(palavra normalizada, índice da palavra)]: cada palavra pode virar várias por extenso."""
        # letra dobrada vira uma: "Lemann" e "Leman" são a mesma palavra ouvida
        return [(n, i) for i, w in enumerate(ws) for n in (re.sub(r"([a-z])\1+", r"\1", norm(x)) for x in extenso(w["w"]).split()) if n]

    print("OUVINDO %d emendas de %s (Whisper local %s, %.1f s de cada lado)" % (len(blocos) - 1, arg.audio, arg.modelo, arg.lado))
    reais, mudos, alertas = 0, 0, 0
    for A, B in zip(blocos, blocos[1:]):
        t = B["inicio"]
        cab = "%s | %s em %.2f s" % (A["id"], B["id"], t)
        ji = pausa(t - arg.lado - 1.5, t - 1.0, primeira=False)
        jf = pausa(t + 1.0, t + arg.lado + 1.5, primeira=True)
        ji, jf = (ji if ji is not None else max(0.0, t - arg.lado)), (jf if jf is not None else t + arg.lado)
        try:
            ouvido = ouvir(final, ji, jf, arg.modelo, arg.cpu)
        except Exception as e:   # nunca verde sem ter ouvido
            mudos += 1
            print("🔇 %s · NÃO OUVIU: %s" % (cab, str(e)[:90]))
            continue
        esper = [w for w in palavras if ji <= (w["s"] + w["e"]) / 2 < jf]
        txt_ouv = " ".join(w["w"] for w in ouvido)

        # 1) o que o Whisper ouviu × o esperado, só nas duas palavras da emenda (a última de A e a primeira de B)
        te, to = toks(esper), toks(ouvido)
        junta = {i for i, w in enumerate(esper) if w["s"] < t}
        junta = ({max(junta)} if junta else set()) | ({min(set(range(len(esper))) - junta)} if len(junta) < len(esper) else set())
        pos = {k for k, (_, i) in enumerate(te) if i in junta}
        difere = []
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [x[0] for x in te], [x[0] for x in to], autojunk=False).get_opcodes():
            if op == "equal" or not (pos & set(range(i1, max(i2, i1 + 1)))):
                continue
            e_ = " ".join(dict.fromkeys(esper[te[k][1]]["w"] for k in range(i1, i2))) or "∅"
            o_ = " ".join(dict.fromkeys(ouvido[to[k][1]]["w"] for k in range(j1, j2))) or "∅"
            difere.append("esperado «%s» · ouvido «%s»" % (e_, o_))

        # 2) silêncio na emenda (contínuo, abaixo de −40 dB, em volta de t)
        d = db10(t - 0.3, t + 0.3)
        c = min(30, len(d) - 1)
        esq = next((i for i in range(c, -1, -1) if d[i] >= -40), -1)
        dir_ = next((i for i in range(c, len(d)) if d[i] >= -40), len(d))
        silencio = max(0, dir_ - esq - 1) * 10
        s_ini, s_fim = t - 0.3 + (esq + 1) * 0.01, t - 0.3 + dir_ * 0.01   # o silêncio contínuo em volta da emenda

        # 3) alinhador: palavra esperada com som dos dois lados do silêncio da emenda = atravessa (comida de um lado).
        #    Letra que cai DENTRO do silêncio não conta (o pico da última letra às vezes escorrega para a pausa), nem
        #    palavra que o modelo não achou (score < 0,1: ele a espreme em qualquer canto; no C84, o "Quando" engolido
        #    do bloco brasil): essa vira "??", re-ouvir.
        atravessa, fracas = [], []
        if AL and esper:
            ws = AL.alinhar(final, ji, jf, "* %s *" % " ".join(w["w"] for w in esper))
            for w in ws:
                if w["w"] == "*":
                    continue
                picos = [l[1] for l in w["letras"]]
                if w["score"] < AL.FRACA:
                    if abs((w["s"] + w["e"]) / 2 - t) < 0.6:
                        fracas.append("%s %.2f" % (w["w"], w["score"]))
                elif min(picos) < s_ini - 0.02 and max(picos) > s_fim + 0.02:
                    atravessa.append(w["w"])

        seca = "  · emenda seca (%d ms de silêncio): início no meio da pausa ou \"respiro\"" % silencio if 60 <= silencio < 200 else ""
        if atravessa:
            reais += 1
            veredito = "REAL: «%s» atravessa a emenda (alinhador): mexer na ponta" % " ".join(atravessa)
        elif silencio < 60:
            veredito = "voz na emenda (só %d ms abaixo de −40 dB): conferir no envelope" % silencio
        elif difere:
            veredito = "provável FALSO ALARME (%d ms de silêncio na emenda, nenhuma palavra atravessa)" % silencio
        else:
            veredito = None
        if fracas:
            veredito = (veredito + "  " if veredito else "") + "?? o alinhador não achou: %s (re-ouvir)" % ", ".join(fracas)
        if veredito is None:
            print("✅ %s · «%s»%s" % (cab, txt_ouv[-110:], seca))
            continue
        alertas += 1
        print("⚠ %s · «%s»" % (cab, txt_ouv[-110:]))
        if difere:
            print("    Whisper: " + " | ".join(difere))
        print("    2ª conferência: %s%s" % (veredito, seca))
    if mudos:
        print("🔇 %d emenda(s) NÃO ouvidas: relatório INCOMPLETO" % mudos)
    print("⚠ %d emenda(s) com ressalva (%d REAL): conferir no envelope" % (alertas, reais) if alertas else "✅ nenhuma emenda com ressalva")
    return 1 if reais or mudos else 0


if __name__ == "__main__":
    sys.exit(main())
