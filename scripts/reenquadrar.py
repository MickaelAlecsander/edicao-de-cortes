# -*- coding: utf-8 -*-
"""Rosto do Raul sempre inteiro e do mesmo tamanho na janela: desfaz os zooms que o editor da fonte faz (e o Raul chegando
perto da câmera), afastando a imagem quando o rosto cresce, e segue a cabeça (do cabelo ao queixo, nunca cortada). Quando é
preciso mais largura do que a fonte tem, as laterais viram a própria imagem desfocada e escurecida (como o modo "cheio" do
cortar.py). A legenda que a fonte grava na imagem fica desfocada só onde estão as letras.

    python reenquadrar.py cortes/<slug> <alto.mp4> [--alvo 600] [--max 1470] [--base 1310]
                                      [--legenda 1300-1440] [--fixo a-b:y[:largura] ...]

<alto.mp4>: o mesmo corte do cortar.py, mas com a fonte inteira na vertical (janela 1080x1920, recorte [0, 1080, 0], SEM o
"tapar"), para haver imagem acima da cabeça quando a janela afasta. Escreve assets/raul.mp4 (1080x960, o áudio vem do
raul.mp4 de antes, guardado em assets/raul_antes_reenquadrar.mp4).

Pedido do dono do canal (14/10/2026, no C72): "ainda tô achando os zooms grande demais… tá ficando colado no rosto dele, tá saindo
tudo… quero tirar isso de zoom ou resolva isso"; "não deixa o rosto dele ficar cortado… se tiver legenda a gente desfoca só a
região da legenda do vídeo original… mas não fica com cabeça recortada". Medido na fonte do C72: o rosto (detector do
OpenCV) ia de ~550 px no plano normal a ~880 px nos zooms do editor, quase sempre zoom lento de 1–2 s, às vezes corte seco.

  --alvo:    largura do rosto (px da fonte) do plano normal; rosto maior afasta a janela na mesma proporção
  --max:     largura máxima de fonte mostrada (1470 = laterais desfocadas de ~13% de cada lado no pior caso)
  --base:    linha da fonte que a base da janela não precisa passar (no C72, logo acima da legenda gravada): a janela só
             desce além dela quando o queixo pede, e aí a legenda entra desfocada
  --legenda: faixa de linhas da fonte onde ela grava a legenda (letras claras): desfocada quadro a quadro
  --fixo a-b:y[:largura]: trecho (s do corte) com janela fixa a partir da linha y (o mapa, a foto da fila)
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
W, H = 1080, 960
SALTO = 42.0        # o mesmo do enquadrar.py: diferença média entre quadros (imagem de 270 px) que é corte
CABELO, QUEIXO = 0.42, 0.93   # topo do cabelo e queixo em relação à caixa do detector (topo - 0,42·w; topo + 0,93·w)
FOLGA = 0.05        # respiro acima do cabelo e abaixo do queixo (fração da altura da janela)


def suave(v, sig):
    """média gaussiana que não atravessa as pontas do trecho"""
    if len(v) < 3:
        return v
    k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
    p = np.pad(v, 3 * sig, mode="edge")
    return np.convolve(p, k / k.sum(), mode="valid")


def desfoca_legenda(f, y0, y1):
    """letras claras da legenda gravada (top-hat) → caixa centrada nelas → letras apagadas e a caixa desfocada, borda suave"""
    b = f[y0:y1]
    L = cv2.cvtColor(b, cv2.COLOR_BGR2LAB)[:, :, 0]
    th = cv2.morphologyEx(L, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    m = ((th > 28) & (L > 120)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    # letra: 6–90 px de altura, no meio da faixa (a legenda é centrada no quadro)
    ok = [i for i in range(1, n) if 6 <= st[i, 3] <= 90 and st[i, 4] >= 12 and 100 <= cen[i][0] <= 980
          and 0.15 * (y1 - y0) <= cen[i][1] <= 0.85 * (y1 - y0)]
    if len(ok) < 2:
        return
    xs = np.array([[st[i, 0], st[i, 0] + st[i, 2]] for i in ok])
    ys = np.array([[st[i, 1], st[i, 1] + st[i, 3]] for i in ok])
    meia = max(540 - xs[:, 0].min(), xs[:, 1].max() - 540) + 18
    xa, xb = int(max(0, 540 - meia)), int(min(f.shape[1], 540 + meia))
    ya, yb = int(max(0, ys[:, 0].min() - 10)), int(min(y1 - y0, ys[:, 1].max() + 10))
    letras = cv2.dilate(np.isin(lab, ok).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    limpo = cv2.inpaint(b, letras, 5, cv2.INPAINT_TELEA)
    borrado = cv2.GaussianBlur(limpo, (0, 0), 11)
    a = np.zeros(b.shape[:2], np.float32)
    a[ya:yb, xa:xb] = 1
    a = cv2.GaussianBlur(a, (0, 0), 7)[:, :, None]
    f[y0:y1] = (b * (1 - a) + borrado * a).astype(np.uint8)


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    pasta, alto = sys.argv[1], sys.argv[2]
    arg = lambda nome, d: [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == nome] or d
    alvo, wmax, base = float(arg("--alvo", ["600"])[0]), float(arg("--max", ["1470"])[0]), float(arg("--base", ["1310"])[0])
    leg = [tuple(map(int, x.split("-"))) for x in arg("--legenda", [])]
    fixos = []
    for x in arg("--fixo", []):
        p = x.split(":")
        fixos.append((float(p[0].split("-")[0]), float(p[0].split("-")[1]), float(p[1]), float(p[2]) if len(p) > 2 else W))
    tempos = json.load(open(os.path.join(pasta, "assets", "tempos.json"), encoding="utf-8"))
    cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # 1ª passada: rosto (largura e topo da caixa) e cortes
    cap = cv2.VideoCapture(alto)
    fps, VW, VH = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    assert (VW, VH) == (1080, 1920), "o alto.mp4 tem de ser a fonte inteira (1080x1920)"
    larg, topo, cortes, ant = [], [], {0}, None
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(f, (270, 480)), cv2.COLOR_BGR2GRAY).astype(np.int16)
        if ant is not None and np.abs(g - ant).mean() > SALTO:
            cortes.add(len(larg))
        ant = g
        r = cas.detectMultiScale(cv2.cvtColor(cv2.resize(f, (540, 960)), cv2.COLOR_BGR2GRAY), 1.1, 6, minSize=(90, 90))
        q = max(r, key=lambda q: q[2]) if len(r) else None
        larg.append(2.0 * q[2] if q is not None else np.nan)
        topo.append(2.0 * q[1] if q is not None else np.nan)
    cap.release()
    n = len(larg)
    larg, topo = np.array(larg), np.array(topo)
    cortes |= {int(round(b["inicio"] * fps)) for b in tempos["blocos"]}
    # o corte de "volta do zoom" da fonte é no mesmo plano (diferença entre quadros abaixo do SALTO): aparece como um pulo
    # no tamanho do rosto (mediana dos 5 quadros depois × 5 antes, acima de 15%), contra ~1%/quadro do zoom lento
    ok = ~np.isnan(larg)
    cheio = np.interp(np.arange(n), np.flatnonzero(ok), larg[ok])
    pulo = np.array([abs(np.log(np.median(cheio[i:i + 5]) / np.median(cheio[max(0, i - 5):i]))) if 5 <= i <= n - 5 else 0 for i in range(n)])
    cortes |= {i for i in range(1, n - 1) if pulo[i] > np.log(1.15) and pulo[i] >= pulo[i - 1] and pulo[i] >= pulo[i + 1]}
    cortes = sorted(c for c in cortes if c < n) + [n]

    # por trecho entre cortes: buracos interpolados, mediana (tira o erro do detector) e média gaussiana (os zooms da fonte
    # são lentos; a janela acompanha sem tremer). Num corte seco a janela troca junto, escondida pelo próprio corte
    ww, y0 = np.full(n, float(W)), np.full(n, base - H)
    for a, z in zip(cortes, cortes[1:]):
        ok = ~np.isnan(larg[a:z])
        if ok.sum() < 3:
            continue
        lis = []
        for v in (larg[a:z], topo[a:z]):
            v = np.interp(np.arange(z - a), np.flatnonzero(ok), v[ok])
            v = np.array([np.median(v[max(0, i - 4):i + 5]) for i in range(len(v))])
            lis.append(suave(v, 6))
        w, t = lis
        cabelo, queixo = t - CABELO * w, t + QUEIXO * w
        # largura: a do tamanho do rosto, ou mais, se a cabeça inteira (com respiro) não couber na altura
        largura = np.clip(np.maximum(w * W / alvo, (queixo - cabelo) / (1 - 2 * FOLGA) * W / H), W, wmax)
        alt = largura * H / W
        # altura: base acima da legenda gravada, a não ser que o queixo peça mais; e o cabelo sempre com respiro
        fim = np.maximum(base, queixo + FOLGA * alt)
        ini = np.minimum(fim - alt, cabelo - FOLGA * alt)
        ww[a:z], y0[a:z] = largura, ini
    for a, z, y, lw in fixos:
        i, j = int(round(a * fps)), int(round(z * fps))
        ww[i:j], y0[i:j] = lw, y
    y0 = np.clip(y0, 0, VH - ww * H / W)

    # 2ª passada: compõe e grava (o áudio é o do raul.mp4 de antes, que é o mesmo corte)
    mp4 = os.path.join(pasta, "assets", "raul.mp4")
    velho = os.path.join(pasta, "assets", "raul_antes_reenquadrar.mp4")
    if not os.path.exists(velho):
        os.replace(mp4, velho)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H), "-r", str(round(fps)),
                            "-i", "-", "-i", velho, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
                            "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", mp4], stdin=subprocess.PIPE)
    cap = cv2.VideoCapture(alto)
    for i in range(n):
        ok, f = cap.read()
        hh = ww[i] * H / W
        for la, lb in leg:
            if la < y0[i] + hh and lb > y0[i]:          # só se a legenda entra na janela
                desfoca_legenda(f, la, lb)
        k = W / ww[i]                                   # escala fonte → janela
        x0 = (VW - ww[i]) / 2                           # negativo quando afasta além da largura da fonte
        if k == 1:                                      # sem afastar: recorte puro, sem reamostrar (fica nítido)
            yi = int(round(y0[i]))
            enc.stdin.write(np.ascontiguousarray(f[yi:yi + H]).tobytes())
            continue
        fg = cv2.warpAffine(f, np.float32([[k, 0, -x0 * k], [0, k, -y0[i] * k]]), (W, H), flags=cv2.INTER_LINEAR)
        if ww[i] > W + 0.5:
            # laterais: a mesma imagem na largura da fonte, desfocada e escurecida
            yb = y0[i] + (hh - H) / 2
            bg = f[int(yb):int(yb) + H, :W]
            bg = cv2.resize(cv2.GaussianBlur(cv2.resize(bg, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 7), (W, H))
            bg = (bg * 0.86).astype(np.uint8)
            xa, xb = -x0 * k, (VW - x0) * k
            m = np.clip(np.minimum(np.arange(W) - xa, xb - np.arange(W)) + 0.5, 0, 1)[None, :, None]   # 1 px de transição
            fg = (fg * m + bg * (1 - m)).astype(np.uint8)
        enc.stdin.write(fg.tobytes())
    enc.stdin.close()
    enc.wait()
    cap.release()
    fundo = y0 + ww * H / W
    print("%d quadros: janela de %d a %d px da fonte (%.0f%% do tempo afastada); base passa de %d em %.0f%% do tempo (legenda desfocada)" %
          (n, ww.min(), ww.max(), 100 * (ww > W + 0.5).mean(), base, 100 * (fundo > base + 8).mean()))
    json.dump({"ww": [round(v, 1) for v in ww], "y0": [round(v, 1) for v in y0]}, open(os.path.join(pasta, "assets", "reenquadra.json"), "w"))


if __name__ == "__main__":
    main()
