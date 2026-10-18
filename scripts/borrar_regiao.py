# -*- coding: utf-8 -*-
"""Desfoca uma ou mais regiões de um vídeo num intervalo, com a borda esfumada, sem passar duas vezes.

    python borrar_regiao.py <video> --regiao x,y,w,h,t0,t1 [--regiao ...] [--borda 45] [--forca 26]

    # de dentro da pasta do corte, entre o corte e o pos_cortar.py:
    python <skill>/scripts/cortar.py . && python <skill>/scripts/borrar_regiao.py assets/raul.mp4 \
        --regiao 0,670,520,220,8.8,13.0 && python pos_cortar.py

Para o texto ou overlay do canal do Raul que aparece na janela dele: no C84, o "Deixe o like na CONFIANÇA" (x 0–520,
y 670–890 da janela de 1080×960, de 8,8 a 13,0 s). É texto do canal dele, não do nosso. Também serve para a faixa de
propaganda (a da AUVP com o QR code, no C81: y 688–960 da janela, de 56,5 a 65,8 s).
  · Roda no assets/raul.mp4 DEPOIS do cortar.py (tempos e pixels da montagem) e antes do pos_cortar.py. O cortar.py
    regrava o raul.mp4 sem o borrão: rode de novo depois de cada corte.
  · Sem passar duas vezes: o arquivo guarda a marca "borrado:<regiões>" nos metadados; com as mesmas regiões, sai sem
    mexer ("já borrado").
  · Borda esfumada de --borda px (padrão 45) para dentro da caixa; o lado que encosta na borda do quadro não esfuma (a
    borda ali é a da tela). Força do desfoque: --forca (raio do boxblur, padrão 26).
  · Áudio copiado; vídeo em CRF 14 (arquivo intermediário, o render final recomprime).
Não serve para texto que a fonte escreve POR CIMA do Raul ao longo de vários blocos (aí é o "tapar" do cortes.json, com
máscara e removelogo, ou o desfoque numa cópia da fonte antes do cortar.py) nem para a legenda gravada do short vertical
(reenquadrar.py --legenda, que desfoca só a caixa das letras).
"""
import argparse
import os
import subprocess
import sys


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Desfoca regiões num intervalo, com borda esfumada (ver o topo do arquivo).")
    ap.add_argument("video")
    ap.add_argument("--regiao", action="append", required=True, help="x,y,w,h,t0,t1 (pixels do vídeo, segundos do vídeo)")
    ap.add_argument("--borda", type=int, default=45)
    ap.add_argument("--forca", type=int, default=26)
    arg = ap.parse_args()

    VW, VH = (int(v) for v in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                              "stream=width,height", "-of", "csv=p=0", arg.video],
                                             capture_output=True, text=True, check=True).stdout.strip().split(","))
    marca = "borrado:%s;b%d;f%d" % ("|".join(arg.regiao), arg.borda, arg.forca)
    tag = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format_tags=comment", "-of", "csv=p=0", arg.video],
                         capture_output=True, text=True).stdout
    if marca in tag:   # sai com 0: numa cadeia "cortar && borrar && pos_cortar", rodar de novo não pode parar o resto
        print("já borrado (%s)" % marca)
        return

    fc, ant, F = [], "0:v", arg.borda
    for i, r in enumerate(arg.regiao):
        x, y, w, h = (int(float(v)) for v in r.split(",")[:4])
        t0, t1 = (float(v) for v in r.split(",")[4:6])
        x, y = max(0, x), max(0, y)
        w, h = min(w, VW - x), min(h, VH - y)
        w, h = w - w % 2, h - h % 2
        # distância a cada lado da caixa; o lado que encosta na borda do quadro ganha F (não esfuma)
        dl, dr = "X+%d" % (F if x == 0 else 0), "W-X+%d" % (F if x + w >= VW else 0)
        dt, db = "Y+%d" % (F if y == 0 else 0), "H-Y+%d" % (F if y + h >= VH else 0)
        fc.append("[%s]split[a%d][b%d];[b%d]crop=%d:%d:%d:%d,boxblur=%d:3,format=yuva420p,"
                  "geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='255*min(1,min(min(%s,%s),min(%s,%s))/%d)'[d%d];"
                  "[a%d][d%d]overlay=%d:%d:enable='between(t,%.3f,%.3f)'[v%d]"
                  % (ant, i, i, i, w, h, x, y, arg.forca, dl, dr, dt, db, F, i, i, i, x, y, t0, t1, i))
        ant = "v%d" % i
    tmp = os.path.splitext(arg.video)[0] + "_borrando.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", arg.video, "-filter_complex", ";".join(fc), "-map", "[%s]" % ant,
                    "-map", "0:a?", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", "-metadata", "comment=" + marca, "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, arg.video)
    for r in arg.regiao:
        print("✓ desfocado: %s" % r)


if __name__ == "__main__":
    main()
