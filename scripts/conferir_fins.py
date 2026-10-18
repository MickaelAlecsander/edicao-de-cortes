# -*- coding: utf-8 -*-
"""Confere a PONTA de cada bloco de um corte: nenhum bloco pode começar ou terminar no meio de uma palavra.

    python conferir_fins.py cortes/<slug>      (Whisper local; MODELO=medium para ir mais rápido)

Rode depois do cortar.py, antes de mostrar a etapa 2 (pedido do dono do canal, 02/10/2026: no C05 vários blocos
terminaram no meio da palavra e a conferência pela transcrição da montagem inteira não pegou).

Para cada bloco, na FONTE:
  · energia dos 20 ms antes do corte de áudio do fim e dos 20 ms depois do de início (tem que ser silêncio);
  · transcreve SÓ o trecho que termina no corte (os 3 s finais) e SÓ o que começa nele (os 2,5 s iniciais):
    a última/primeira palavra ouvida tem que ser a esperada. Isolado, o Whisper não tem o bloco seguinte
    para "completar" a palavra pelo contexto, então uma sílaba cortada aparece como palavra errada ou some.
Sai com código 1 se algum bloco reprovar.

AVISO (⚠, não reprova): corte num vale curto (menos de 80 ms abaixo de −40 dB) com fala forte logo do outro lado (até
60 ms). Pode ser palavra emendada na seguinte (normal) ou o fechamento de uma consoante NO MEIO da palavra ("cam|panha",
"tribu|tárias", "vol|tar": em 04/10 o "voltar" saiu sem o "tar"). Todo ⚠ se confere no espectro antes de mostrar.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

import numpy as np
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
SR = 16000
LIMIAR = -33.0     # dB: acima disso, ainda tem fala no instante do corte


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", w)


def audio(src, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", src, "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x * x)) + 1e-9)


def vale_curto(src, t, lado):
    """(duração do vale em ms, ms até a fala forte) se o corte em t cai num vale curto com fala logo do outro lado."""
    x = audio(src, t - 0.12, t + 0.12)
    n = SR // 100
    r = [db(x[i:i + n]) for i in range(0, len(x) - n + 1, n)]
    c = 12                                   # quadro do corte
    a = c
    while a > 0 and r[a - 1] < -40:
        a -= 1
    z = c
    while z < len(r) - 1 and r[z] < -40:
        z += 1
    lado_fala = r[c:c + 7] if lado == "fim" else r[max(0, c - 6):c + 1][::-1]
    forte = next((k for k, v in enumerate(lado_fala) if v > -26), None)
    return ((z - a) * 10, forte * 10) if (z - a) < 8 and forte is not None else None


def ouvir(modelo, src, a, b):
    wav = os.path.join(tempfile.gettempdir(), "conferir_fins.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", src, "-ac", "1", "-ar", str(SR),
                    "-af", "adelay=1000,apad=pad_dur=1.5", wav], check=True)
    segs, _ = modelo.transcribe(wav, language="pt", word_timestamps=True)
    return [w.word.strip() for s in segs for w in (s.words or [])]


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    pasta = os.path.abspath(sys.argv[1])
    cfg = json.load(open(os.path.join(pasta, "cortes.json"), encoding="utf-8"))
    src = os.path.normpath(os.path.join(pasta, cfg["fonte"]))
    tempos = json.load(open(os.path.join(pasta, "assets", "tempos.json"), encoding="utf-8"))
    modelo = WhisperModel(os.environ.get("MODELO", "large-v3"), device="cpu", compute_type="int8")
    ruins = 0
    for b in tempos["blocos"]:
        src = b.get("arquivo", src)   # o cortar.py grava a fonte de cada bloco (corte com duas fontes, C17)
        t0, t1 = b["fonte"]
        s0, s1 = b.get("audio", b["fonte"])   # o ponto exato onde o áudio corta (cortar.py novo)
        ws = [p["w"] for p in b["palavras"] if norm(p["w"])]
        e_fim, e_ini = db(audio(src, s1 - 0.02, s1)), db(audio(src, s0, s0 + 0.02))
        fim = ouvir(modelo, src, max(s0, s1 - 3.0), s1)
        ini = ouvir(modelo, src, s0, min(s1, s0 + 2.5))
        ok_fim = bool(fim) and norm(fim[-1]) == norm(ws[-1])
        ok_ini = bool(ini) and norm(ini[0]) == norm(ws[0])
        problemas = []
        if e_fim > LIMIAR:
            problemas.append(f"fala no fim ({e_fim:.0f} dB)")
        if not ok_fim:
            problemas.append(f"termina em «{fim[-1] if fim else '∅'}», esperado «{ws[-1]}»")
        if e_ini > LIMIAR:
            problemas.append(f"fala no início ({e_ini:.0f} dB)")
        if not ok_ini:
            problemas.append(f"começa em «{ini[0] if ini else '∅'}», esperado «{ws[0]}»")
        avisos = []
        for t, lado in ((s1, "fim"), (s0, "início")):
            v = vale_curto(src, t, "fim" if lado == "fim" else "ini")
            if v:
                avisos.append(f"⚠ vale curto no {lado} ({v[0]} ms; fala forte a {v[1]} ms): consoante no meio da palavra?")
        ruins += bool(problemas)
        print(f"{'✗' if problemas else '✓'} {b['id']:10s} …{' '.join(fim[-3:])}  |  " + ("; ".join(problemas) or "ok")
              + ("  " + " ".join(avisos) if avisos else ""), flush=True)
    print(f"\n{len(tempos['blocos']) - ruins}/{len(tempos['blocos'])} blocos ok")
    sys.exit(1 if ruins else 0)


if __name__ == "__main__":
    main()
