# -*- coding: utf-8 -*-
"""Acha as trocas de câmera e de layout de um trecho de vídeo, com o pts EXATO do primeiro quadro novo.

    python trocas.py <video> [--de 468] [--ate 489] [--regiao x,y,w,h] [--salto 30] [--nivel 25] [--tempos assets/tempos.json]

Para que serve: as `trocas` do cortes.json caem no quadro exato da troca da fonte, sem arredondar (C21: arredondada, a
troca mostrava 1 ou 2 quadros da outra câmera com o recorte errado). O número que vai no cortes.json é o pts do PRIMEIRO
quadro do plano novo, no tempo da fonte (o mesmo do -ss do ffmpeg).

Como acha (o mesmo que se fez à mão no C84):
  · salto: a diferença média entre um quadro e o anterior (cinza, 160 px de largura, 0–255). Corte seco = um pico
    isolado acima de --salto (padrão 30) e pelo menos o dobro dos vizinhos (gesto de mão fica abaixo; ver enquadrar.py
    do projeto: ~27–35 em 270 px, por isso o pico precisa ser isolado);
  · --regiao x,y,w,h (pixels do vídeo original): o brilho médio de uma região que muda de nível entre os dois planos.
    Escolha uma área em que só o layout muda, nunca onde a mão do Raul passa (a mão dá falso alarme: no C84, 508,04 e
    508,13). No C84, a área à esquerda é o slide escuro na tela dividida e a estante clara no plano aberto: um salto de nível
    ≥ --nivel (padrão 25) entre dois quadros marca a troca mesmo quando a diferença geral é pequena; uma mudança de
    nível que leva vários quadros (≥ --nivel em 0,5 s, sem salto) sai como "gradual": é dissolve ou foto entrando por
    cima, e o quadro exato se confere à mão (o C55 tinha trocas em dissolve que a detecção de cena não pegava).
  · --tempos: rodando no assets/raul.mp4 (a montagem), diz em que bloco cai cada troca, se é a emenda de um bloco, e o
    tempo correspondente na FONTE (fonte = início do bloco na fonte + tempo dentro do bloco). Assim se confere, depois
    do cortar.py, que a troca de recorte entrou no quadro certo.
Também aparecem os cortes secos de zoom do editor da fonte (o mesmo plano, mais perto ou mais longe; no C84, em 14,29
e 18,88 da fonte): não pedem recorte novo se o Raul continua inteiro, mas se conferem na folha de contato.
Saída: uma linha por troca e, no fim, a lista pronta para colar em "trocas" (o recorte de cada plano se escolhe olhando
a folha de contato; o "?" é para preencher).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile

import numpy as np

LARG = 160


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Trocas de câmera/layout com o pts do 1º quadro novo (ver o topo do arquivo).")
    ap.add_argument("video")
    ap.add_argument("--de", type=float, default=0.0)
    ap.add_argument("--ate", type=float)
    ap.add_argument("--regiao", help="x,y,w,h em pixels do vídeo: região cujo brilho muda entre os planos")
    ap.add_argument("--salto", type=float, default=30.0)
    ap.add_argument("--nivel", type=float, default=25.0)
    ap.add_argument("--tempos", help="assets/tempos.json, quando o vídeo é o raul.mp4 da montagem")
    arg = ap.parse_args()

    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                           "-show_entries", "format=duration", "-of", "json", arg.video], capture_output=True, text=True, check=True).stdout
    info = json.loads(info)
    W, H = info["streams"][0]["width"], info["streams"][0]["height"]
    num, den = info["streams"][0]["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    ate = arg.ate if arg.ate is not None else float(info["format"]["duration"])
    w, h = LARG, int(round(LARG * H / W / 2)) * 2
    reg = None
    if arg.regiao:
        x, y, rw, rh = (int(v) for v in arg.regiao.split(","))
        k = w / W
        reg = (int(x * k), int(y * k), max(1, int(rw * k)), max(1, int(rh * k)))

    # -copyts: o showinfo dá o pts da FONTE (o mesmo tempo do -ss do cortar.py), e não o tempo desde o começo do trecho
    with tempfile.TemporaryFile() as log:
        p = subprocess.Popen(["ffmpeg", "-v", "info", "-hide_banner", "-ss", "%.3f" % max(0.0, arg.de - 0.2), "-t",
                              "%.3f" % (ate - arg.de + 0.2), "-copyts", "-i", arg.video, "-an", "-vf",
                              "scale=%d:%d,format=gray,showinfo" % (w, h), "-f", "rawvideo", "-"],
                             stdout=subprocess.PIPE, stderr=log)
        dif, niv, ant = [], [], None
        while True:
            b = p.stdout.read(w * h)
            if len(b) < w * h:
                break
            g = np.frombuffer(b, np.uint8).reshape(h, w).astype(np.int16)
            dif.append(float(np.abs(g - ant).mean()) if ant is not None else 0.0)
            niv.append(float(g[reg[1]:reg[1] + reg[3], reg[0]:reg[0] + reg[2]].mean()) if reg else 0.0)
            ant = g
        p.wait()
        log.seek(0)
        pts = [float(x) for x in re.findall(rb"pts_time:\s*([-\d.]+)", log.read())]
    n = min(len(pts), len(dif))
    pts, dif, niv = pts[:n], np.array(dif[:n]), np.array(niv[:n])
    if n < 3:
        sys.exit("✗ não li quadros de %s entre %.2f e %.2f" % (arg.video, arg.de, ate))

    blocos = json.load(open(arg.tempos, encoding="utf-8"))["blocos"] if arg.tempos else []

    def onde(t):
        if not blocos:
            return ""
        b = next((b for b in blocos if b["inicio"] - 1e-3 <= t < b["inicio"] + b["dur"] - 1e-3), blocos[-1])
        emenda = abs(t - b["inicio"]) < 0.5 / fps
        return "  · %s %s (fonte %.3f)" % ("EMENDA, início do bloco" if emenda else "dentro do bloco", b["id"],
                                          b["fonte"][0] + t - b["inicio"])

    achou, k, grad = [], max(2, int(round(0.5 * fps))), -10 ** 9
    for i in range(1, n):
        if pts[i] < arg.de - 1e-6:
            continue
        viz = max(dif[i - 1], dif[i + 1] if i + 1 < n else 0.0, 1.0)
        seco = dif[i] >= arg.salto and dif[i] >= 2 * viz
        nivel = reg and abs(niv[i] - niv[i - 1]) >= arg.nivel
        if seco or nivel:
            achou.append(i)
            print("%9.3f  (anterior %.3f)  salto %5.1f%s%s" % (pts[i], pts[i - 1], dif[i],
                  "  região %3.0f → %3.0f" % (niv[i - 1], niv[i]) if reg else "", onde(pts[i])))
        elif reg and i > k and i - grad > 2 * k and abs(niv[i] - niv[i - k]) >= arg.nivel \
                and not any(i - k <= j <= i for j in achou):
            grad = i
            print("%9.3f  gradual: região %3.0f → %3.0f em %.2f s (dissolve ou foto por cima: conferir quadro a quadro)%s"
                  % (pts[i - k], niv[i - k], niv[i], pts[i] - pts[i - k], onde(pts[i - k])))
    print("%d troca(s) em %d quadros (%.3f–%.3f s, %.3f qps)" % (len(achou), n, pts[0], pts[-1], fps))
    if achou:
        print('"trocas": [%s]' % ", ".join("[%.3f, ?]" % pts[i] for i in achou))


if __name__ == "__main__":
    main()
