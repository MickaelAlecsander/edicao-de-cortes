# -*- coding: utf-8 -*-
"""Folha de contato de um vídeo (ou de um trecho): um quadro a cada N s, com o tempo escrito, em folhas que dá para ler.

    python folha_contato.py <video> [--cada 2] [--de 0] [--ate fim] [--largura 320] [--colunas 5] [-o folha.jpg]

Onde usar (o que olhar está em references/corte-e-fala.md, "Folha de contato"):
  · assets/raul.mp4, a cada 2 s, logo depois do cortar.py e antes da animação: Raul inteiro em todos os quadros (C28) e
    quem está em cada quadro (C44: 2,2 s do apresentador ouvindo passaram por "Raul");
  · o vídeo pronto (renders/etapa3.mp4), a cada 3 s, antes de mandar a prévia;
  · um trecho da fonte (--de/--ate), a cada 2 a 4 s, para escolher o recorte de cada plano e, num podcast, ver quem fala.
Cada quadro sai com 320 px de largura (o bastante para ver cabeça cortada, borda preta, texto na tela e quem é quem) e
as folhas param em ~2400 px de altura: acima disso a imagem chega reduzida demais para se ler. Mais quadros = mais
folhas (folha_1.jpg, folha_2.jpg...). O tempo escrito é o do vídeo (o da fonte, quando --de é usado na fonte).
"""
import argparse
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np

FAIXA = 26   # altura da faixa do tempo, em px


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Folha de contato com o tempo de cada quadro (ver o topo do arquivo).")
    ap.add_argument("video")
    ap.add_argument("--cada", type=float, default=2.0, help="segundos entre quadros")
    ap.add_argument("--de", type=float, default=0.0)
    ap.add_argument("--ate", type=float)
    ap.add_argument("--largura", type=int, default=320)
    ap.add_argument("--colunas", type=int, default=5)
    ap.add_argument("-o", "--saida", help="padrão: folha_<nome do vídeo>.jpg na pasta atual")
    arg = ap.parse_args()

    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                      "-show_entries", "format=duration", "-of", "json", arg.video],
                                     capture_output=True, text=True, check=True).stdout)
    W, H = info["streams"][0]["width"], info["streams"][0]["height"]
    ate = arg.ate if arg.ate is not None else float(info["format"]["duration"])
    w = arg.largura
    h = int(round(w * H / W / 2)) * 2
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % arg.de, "-t", "%.3f" % (ate - arg.de), "-i", arg.video,
                          "-an", "-vf", "fps=1/%g,scale=%d:%d" % (arg.cada, w, h), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True, check=True).stdout
    q = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    if not len(q):
        sys.exit("✗ nenhum quadro entre %.2f e %.2f" % (arg.de, ate))

    cel_h = h + FAIXA
    por_folha = arg.colunas * max(1, 2400 // cel_h)
    base = arg.saida or "folha_%s.jpg" % os.path.splitext(os.path.basename(arg.video))[0]
    nfolhas = math.ceil(len(q) / por_folha)
    for f in range(nfolhas):
        lote = q[f * por_folha:(f + 1) * por_folha]
        linhas = math.ceil(len(lote) / arg.colunas)
        folha = np.full((linhas * cel_h, arg.colunas * w, 3), 255, np.uint8)
        for k, img in enumerate(lote):
            i = f * por_folha + k
            t = arg.de + i * arg.cada
            y, x = (k // arg.colunas) * cel_h, (k % arg.colunas) * w
            folha[y + FAIXA:y + cel_h, x:x + w] = img
            cv2.putText(folha, "%d:%05.2f  (%.2f s)" % (t // 60, t % 60, t), (x + 6, y + 19), cv2.FONT_HERSHEY_SIMPLEX,
                        0.55, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.rectangle(folha, (x, y + FAIXA), (x + w - 1, y + cel_h - 1), (200, 200, 200), 1)
        nome = base if nfolhas == 1 else "%s_%d%s" % (os.path.splitext(base)[0], f + 1, os.path.splitext(base)[1])
        cv2.imwrite(nome, folha, [cv2.IMWRITE_JPEG_QUALITY, 88])
        print("%s: %d quadros (%.2f–%.2f s)" % (nome, len(lote), arg.de + f * por_folha * arg.cada,
                                                 arg.de + (f * por_folha + len(lote) - 1) * arg.cada))


if __name__ == "__main__":
    main()
