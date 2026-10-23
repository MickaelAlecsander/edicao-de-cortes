# -*- coding: utf-8 -*-
"""Confere as pontas de corte ANTES de cortar: pausa real no áudio + alinhador forçado (MMS_FA) sobre o texto conhecido.

    python pausas.py <fonte> --palavras <palavras.json> <t1>[:antes:depois] [<t2>...] [--perfil]
        # t = instante aproximado da ponta (s, na FONTE); antes/depois = última e primeira palavra esperadas
        # palavras.json = a transcrição do trecho (transcrever_local.py), a mesma do roteiro, de preferência com o
        #   texto já conferido (transcrever_local.py --texto)

Nasceu em 07/10/2026, no C29: os erros de ponta vinham do tempo de palavra do Whisper. Para cada t:
  · acha as pausas de verdade (envelope de 10 ms a cada 5 ms, abaixo de −40 dB, 30 ms ou mais) a até 0,8 s de t. A
    ponta de corte é sempre um desses vales, nunca o fim de palavra que o alinhador ou o Whisper dão;
  · pega o texto de 2,5 s antes a 2,5 s depois no palavras.json e o alinhador forçado (`alinhar.py`, MMS_FA, desde
    12/10/2026) acha cada letra desse texto no áudio. Ele não transcreve, só marca tempo.
    Sem --palavras, o texto vem do Whisper local na própria janela (~6 s): o Whisper de trecho curto pula frase e
    completa palavra cortada (C67: "Tô pouco interessada." sumiu numa janela de 20 palavras; o "Já fica..." só a
    transcrição longa pegou). Use sempre o palavras.json. Cada pausa sai com:
      ✗ DENTRO de X = a pausa é o fechamento de uma consoante no meio da palavra ("ami|go" no C67): cortar ali come X;
      "cortar antes" = o começo da palavra seguinte (f, s, x fracos, oclusão de p/t/k) já está dentro do vale: a janela
        termina antes dele;
      "??" = palavra que o modelo não achou no áudio (não foi dita, foi dita diferente, outra voz): re-ouvir o trecho
        antes de confiar no rótulo;
  · mostra a última palavra antes e a primeira depois, para conferir com o roteiro;
  · --perfil: o envelope a cada 20 ms de t − 0,5 a t + 0,5 (para quando o alinhador se perde: no C84, em 777,8, 794,6
    e 606,8, a ponta saiu do perfil, com o vale entre a queda da última palavra e o ataque da seguinte).
Antes de 12/10 o juiz era o Whisper (palavra que ATRAVESSA a pausa), que estica palavra sobre pausa e completa palavra
cortada (no C67 errou 100–300 ms: "empréstimo", "as", "Só"). Ele volta sozinho se faltar o torch/torchaudio, e avisa.
A janela de corte do cortes.json vem da pausa marcada com ✓: a que não cai dentro de palavra e em que a última palavra
antes e a primeira depois são as do roteiro. Sem as palavras esperadas, fica a mais perto de t. "A mais funda" NÃO serve:
no C29 ela escolheu o vale entre "te" e "pagar".
Duas vozes: o alinhador é fraco no apresentador (C67), então o rótulo perto da troca de voz vale menos.
Meça no MESMO arquivo que o cortar.py corta (C20: o AAC do .mp4 vinha 35,3 ms atrasado em relação ao áudio separado).
"""
import json
import re
import unicodedata
import os
import subprocess
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcrever_local import ouvir  # noqa: E402

try:
    import alinhar as AL  # noqa: E402
except (ImportError, OSError):  # sem torch/torchaudio: o juiz volta a ser o Whisper (pior)
    AL = None

LIMITE, MINIMO, JANELA, LADO = -40.0, 0.03, 0.8, 2.5


def envelope(src, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % a, "-t", "%.3f" % (b - a), "-i", src, "-vn", "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    # janela de 10 ms a cada 5 ms: com passo de 10 ms, o vale de 30 ms do "O Gabriel" (C67) sumia ou aparecia
    # conforme o t pedido (a grade começa em t − 0,8)
    return [(a + i / 200, 20 * np.log10(np.sqrt(np.mean(x[i * 80:i * 80 + 160] ** 2)) + 1e-9)) for i in range(len(x) // 80 - 1)]


def pausas(env):
    runs, cur = [], None
    for t, v in env:
        if v < LIMITE:
            cur = cur or [t, t, v]
            cur[1], cur[2] = t + 0.01, min(cur[2], v)
        elif cur:
            runs.append(cur)
            cur = None
    if cur:
        runs.append(cur)
    return [r for r in runs if r[1] - r[0] >= MINIMO]


def nz(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def esperada(w, ultima):
    """Palavra do roteiro como o juiz a escreve: com o alinhador, número por extenso ("4" → "quatro")."""
    if AL and w:
        p = AL.por_extenso(w).split()
        w = p[-1] if ultima else p[0]
    return nz(w)


def ponta(src, t, quer_antes="", quer_depois="", palavras=None):
    """Imprime as pausas a até JANELA de t e devolve a janela ✓ (a, b), ou None. palavras = lista do palavras.json."""
    quer_antes, quer_depois = esperada(quer_antes, True), esperada(quer_depois, False)
    cand = pausas(envelope(src, t - JANELA, t + JANELA))
    print("\n== %.2f ==" % t)
    if not cand:
        print("  ✗ nenhuma pausa abaixo de %.0f dB a até %.1f s: palavras emendadas, escolha outra ponta" % (LIMITE, JANELA))
        return None
    a, b = t - JANELA - LADO, t + JANELA + LADO
    if AL and palavras:  # 0,3 s de folga nas pontas: o tempo do palavras.json é o do Whisper; o "*" cobre a sobra
        texto = " ".join(w["w"] for w in palavras if w["s"] >= a + 0.3 and w["e"] <= b - 0.3)
    else:
        w1 = ouvir(src, a, b)
        texto = " ".join(w["w"] for w in w1)
    if AL:
        print("  texto (%s): %s" % ("palavras.json" if palavras else "Whisper local na janela, sem --palavras", texto))
        ws = AL.alinhar(src, a, b, "* %s *" % texto)  # "*" = fala fora do texto nas pontas da janela
    else:
        print("  (sem torchaudio: juiz é o Whisper, que estica palavra sobre pausa e completa palavra cortada)")
        ws = w1
    melhor = None
    for p0, p1, fundo in cand:
        j0, j1, fracas = p0 + 0.01, p1 - 0.01, []
        if AL:
            r = AL.rotulo(p0, p1, ws)
            antes, depois, fracas = r["antes"], r["depois"], r["fracas"]
            if r["ate"]:  # o silencio() do cortar.py corta no centro de 10 ms: ao menos 5 ms antes da letra
                j1 = min(j1, r["ate"])
            ok = not r["dentro"] and round(j1 - j0, 3) >= 0.01  # 10 ms: a janela do silencio() do cortar.py
            nota = r["txt"] if r["dentro"] else "antes: …%s | depois: %s…%s" % (" ".join(antes), " ".join(depois), r["avisos"])
            if not r["dentro"] and not ok:
                nota += "  (sem folga antes dela)"
        else:
            c = (p0 + p1) / 2
            atravessa = [w["w"] for w in ws if w["s"] < c - 0.03 and w["e"] > c + 0.03]
            antes = [w["w"] for w in ws if w["e"] <= c + 0.03][-2:]
            depois = [w["w"] for w in ws if w["s"] >= c - 0.03][:2]
            ok = not atravessa
            nota = "antes: …%s | depois: %s…%s" % (" ".join(antes), " ".join(depois),
                                                  "  ATRAVESSA: " + " ".join(atravessa) if atravessa else "")
        bate = (not quer_antes or (antes and nz(antes[-1]) == quer_antes)) and \
               (not quer_depois or (depois and nz(depois[0]) == quer_depois))
        chave = (0 if bate else 1, abs((p0 + p1) / 2 - t))
        if ok and (melhor is None or chave < melhor[3]):
            melhor = (j0, j1, fundo, chave, fracas)
        print("  %s%s %.2f–%.2f (%3.0f dB, %3.0f ms) | %s" % (
            "·" if ok else "✗", "=" if ok and bate and (quer_antes or quer_depois) else " ", p0, p1, fundo, (p1 - p0) * 1000, nota))
    if not melhor:
        print("  ✗ nenhuma janela: todo vale cai dentro de palavra. Com \"??\" por perto o alinhador se perdeu (palavra "
              "engolida ou fora do texto): decida pelo --perfil e escreva o motivo em \"fala_ok\"; sem pausa, a frase sai")
        return None
    aviso = "" if melhor[3][0] == 0 or not (quer_antes or quer_depois) else "  ⚠ nenhuma pausa bate com as palavras esperadas"
    if melhor[4]:
        aviso += "  ?? re-ouvir: o alinhador não achou %s" % ", ".join(melhor[4])
    print("  ✓ janela sugerida: [%.3f, %.3f] (%.0f dB)%s" % (melhor[0], melhor[1], melhor[2], aviso))
    return melhor[0], melhor[1]


def perfil(src, t):
    """Envelope (10 ms a cada 5 ms), impresso a cada 20 ms de t − 0,5 a t + 0,5: «tempo:dB»."""
    env = envelope(src, t - 0.5, t + 0.5)
    print("  perfil a cada 20 ms: " + " ".join("%.2f:%.0f" % (x, v) for x, v in env[::4]))


def main():
    global LIMITE
    args, palavras = sys.argv[1:], None
    if len(args) < 2 or "-h" in args or "--help" in args:
        print(__doc__)
        sys.exit(0)
    com_perfil = "--perfil" in args
    args = [x for x in args if x != "--perfil"]
    if "--limite" in args:   # fonte com ruído de fundo constante: pausa = abaixo de DB (padrão −40), ~1 dB acima do piso (C95)
        i = args.index("--limite")
        LIMITE = float(args[i + 1])
        del args[i:i + 2]
    if "--palavras" in args:
        i = args.index("--palavras")
        palavras = json.load(open(args[i + 1], encoding="utf-8"))
        del args[i:i + 2]
    for arg in args[1:]:
        partes = arg.split(":") + ["", ""]
        ponta(args[0], float(partes[0]), partes[1], partes[2], palavras)
        if com_perfil:
            perfil(args[0], float(partes[0]))


if __name__ == "__main__":
    main()
