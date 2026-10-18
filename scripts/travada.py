# -*- coding: utf-8 -*-
"""Procura imagem travada: trecho em que o quadro não muda enquanto o áudio segue.

    python travada.py <video.mp4> [--raul]

`--raul` olha só a metade de baixo do vertical final (o rosto do Raul, sem a legenda e sem a marca). Sai com erro se achar
um trecho parado de 0,35 s ou mais.

Nasceu em 10/10/2026: o dono do canal viu o Raul "travado por alguns segundos, e o áudio continuou". Nos 12 últimos posts, as
travadas eram todas quadro parado de propósito: o `PARADO` do C44 (2,2 s, a fonte mostrava o Vilela ouvindo) e os congelados
curtos do C37, do C38 e do C42 (0,5–0,7 s). "Isso não pode acontecer em
hipótese alguma." O `cortar.py` chama esta conferência sobre o `raul.mp4`, e o `finalizar.py` sobre o vídeo final (os dois importam
`RAUL` e `travadas` daqui: não renomear).
O respiro (`tpad`, até 0,2 s em silêncio) fica abaixo do mínimo.
Limiar de −70 dB, medido em 10/10: no `raul.mp4` (CRF 14) o congelado do C44 tem diferença entre quadros de 0,000–0,01 e
é pego inteiro (2,17 s); o plano aberto da mesa do C46, com gente quase parada, tem 0,02–0,12 e passa. A −60 dB a mesa
virava "travada" (1,08 s). No vídeo final o congelado do C44 também cai (0,5 s, partido pelo ruído do render).
"""
import re
import subprocess
import sys

MINIMO = 0.35
RAUL = "600:700:300:1150"   # x 300–900, y 1150–1850 do 1080×1920: o rosto, sem a legenda (divisória) e sem a marca


def travadas(video, crop=None, minimo=MINIMO):
    """[(início, fim), ...] dos trechos com o quadro parado (freezedetect a -70 dB)."""
    vf = ("crop=%s," % crop if crop else "") + "freezedetect=n=-70dB:d=%.2f" % minimo
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-an", "-vf", vf, "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    ini = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", err)]
    fim = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", err)]
    if len(fim) < len(ini):   # parado até o fim do vídeo: o freezedetect não fecha o trecho
        fim.append(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                                        capture_output=True, text=True).stdout))
    t = []
    for a, z in zip(ini, fim):   # o freezedetect pode partir um trecho só em vários colados
        if t and a - t[-1][1] < 0.05:
            t[-1] = (t[-1][0], z)
        else:
            t.append((a, z))
    return t


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    v = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    t = travadas(v, RAUL if "--raul" in sys.argv else None)
    for a, z in t:
        print("⛔ imagem parada de %.2f a %.2f s (%.2f s)" % (a, z, z - a))
    print("✓ nenhuma imagem parada" if not t else "⛔ %d trecho(s) parado(s)" % len(t))
    sys.exit(1 if t else 0)
