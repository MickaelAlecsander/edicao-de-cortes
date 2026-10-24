# -*- coding: utf-8 -*-
"""Sonoplastia do corte: a trilha de efeitos sonoros feita como um editor de som profissional faz.

    python <skill>/scripts/sonoplastia.py cortes/<slug>          # gera a trilha de efeitos e o relatório
    python <skill>/scripts/sonoplastia.py cortes/<slug> --mux    # e troca o áudio do renders/etapa3_bruto.mp4 (sem novo render)
    python <skill>/scripts/sonoplastia.py --catalogo <pasta>     # um .wav de cada som do banco, para ouvir e conferir

Precisa de: numpy, scipy, soundfile, ffmpeg/ffprobe no PATH e, para a checagem do fim, node + playwright-core + Chrome.
Os sons gravados ficam em <skill>/assets/foley (achados a partir do caminho deste arquivo). Nenhuma API.

Lê `som.json` (a folha de deixas), `assets/tempos.json` (as palavras) e `assets/raul.wav` (a voz, 48 kHz). Escreve:
  · assets/sfx_mix.wav   a trilha de efeitos pronta (uma faixa só), que o index.html toca por baixo da voz;
  · renders/som_mix.wav  voz + efeitos, para o --mux;
  · som_relatorio.txt    níveis, mascaramento por palavra e densidade.
No fim (sem --mux), confere o erro de JavaScript (erros_js.mjs) e a área de segurança da animação (zona_segura.mjs, desde
17/10/2026): só renderiza com os dois ✓.

Pedido do Mickael (14/10/2026, depois do C77): "estamos usando muito pouco efeito sonoro… os efeitos sonoros acrescentam
muito à imersão… ainda com a regra de não sobrepor o áudio da fala… cria uma lógica profissional, entenda como
profissionais trabalham". Até aqui eram 13 arquivos repetidos (pop, whoosh, clique…), 28 dB abaixo da voz, e o papel.wav
estava mudo (pico de −61 dBFS). A lógica nova:

1. A VOZ É A RAINHA. Ela nunca é processada aqui; tudo se ajusta em volta dela.
2. PONTO DE SINCRONIA. Cada som tem o instante que importa (o contato do carimbo, o pico do whoosh, o "ching" da caixa), e
   esse instante cai no quadro do movimento: no fim do `bate()`, no meio do `entra()`, em cada quique do `bounce.out`.
   Sequências seguem a curva da animação (`ease`): o contador que desacelera faz os tiques desacelerarem junto.
3. CAMADAS COM NÍVEL-ALVO (gain staging). Todo som é medido em loudness (filtro K da BS.1770, janela de 50 ms) e colocado
   num nível relativo à voz conforme a camada: destaque, ação, transição, miúdo, música, textura. Nunca é um "volume no
   olho": o mesmo papel do C24 que estava mudo não acontece mais.
4. DUCKING (sidechain). A camada abaixa sozinha enquanto o Raul fala (de 1 dB no destaque a 4 dB na textura) e volta nos
   respiros. O efeito "respira" com a fala.
5. FAIXA DA INTELIGIBILIDADE. 300 Hz–4,5 kHz é onde as consoantes moram; durante a fala, os efeitos perdem mais 2 dB só
   nessa faixa (EQ dinâmico). O grave da batida e o brilho da moeda continuam.
6. VARIAÇÃO (round robin). Nenhum som sai igual duas vezes: cada deixa tem a própria semente, afinação (±1 semitom) e ganho
   (±1 dB). Repetição idêntica é o que denuncia efeito barato.
7. ESPAÇO. Pan pela posição na tela (até ±0,6, para o celular em mono não perder nada) e uma sala curta e única para colar
   tudo no mesmo lugar. A voz fica no centro, seca.
8. PALETA DO ESTILO. Gibi/caderno pedem foley físico (papel, madeira, moeda, carimbo de borracha) e os recursos clássicos
   do desenho animado (apito de queda, boing, pop, pizzicato). Nada eletrônico (glitch, riser) fora do que existe na cena
   (o bipe da maquininha, a notificação do celular).
9. CONFERÊNCIA. O relatório mostra o nível dos efeitos contra a voz e acusa toda palavra em que os efeitos chegam a menos
   de 10 dB da voz na faixa da fala.

A base é foley GRAVADO (assets/foley: quatro pacotes CC0 do Kenney e a biblioteca do HyperFrames). A síntese (modal para
metal, madeira e vidro; ruído filtrado para papel e ar; Karplus-Strong para corda) entra só no que é desenho animado e para
engrossar o gravado. Tudo sai igual a cada execução (cada deixa tem a sua semente).
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from math import gcd

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, lfilter, resample_poly, sosfilt, sosfiltfilt

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
SR = 48000

# ─────────────────────────────── camadas: nível-alvo (dB contra a voz), ducking (dB) e envio para a sala ───────────────
# Nível: pico de loudness do som (janela de 50 ms, filtro K) contra o percentil 95 da voz na mesma medida.
CAMADA = {
    "destaque":  {"nivel": -4.0,  "duck": 1.0, "sala": 0.16},   # carimbo, BUM, PLAFT, o ka-ching do TCHAN
    "acao":      {"nivel": -6.0,  "duck": 3.0, "sala": 0.12},   # foley do que acontece: corte, moeda, porta, prensa
    "transicao": {"nivel": -9.0,  "duck": 4.0, "sala": 0.06},   # página virando, quadro entrando, whoosh
    "miudo":     {"nivel": -10.0, "duck": 2.0, "sala": 0.10},   # pop de onomatopeia, bipe, gota
    "musica":    {"nivel": -11.0, "duck": 4.0, "sala": 0.20},   # pizzicato, brilho
    "textura":   {"nivel": -16.0, "duck": 4.0, "sala": 0.06},   # passos, tiques, caneta, rolagem
}
# 23/10/2026: os efeitos tinham ficado baixos demais (as folhas de deixas foram baixando vídeo a vídeo, destaque de −4 para −15 dB
# contra a voz). O REALCE sobe todas as camadas menos a transição; o TETO e a FOLGA continuam garantindo a voz por cima.
REALCE = {"destaque": 6.0, "acao": 5.0, "miudo": 5.0, "musica": 4.0, "textura": 3.0, "transicao": 0.0}
CARVE = 2.0          # dB a mais na faixa 300 Hz–4,5 kHz enquanto há fala
FOLGA = 7.0          # a voz fica pelo menos isso acima dos efeitos na faixa da fala, a cada 10 ms
FOLGA_DESTAQUE = 3.0 # a pancada combinada com a palavra (carimbo no "delírio", BUM no "buraco"): folga menor, grave livre
TETO = -3.0          # nenhum efeito passa da voz: loudness de 50 ms no máximo TETO dB contra o percentil 95 da voz
PICO = -9.0          # dBFS: teto de pico da trilha de efeitos (a voz chega a −1,5)
PAN_MAX = 0.6


# ═══════════════════════════════════════ primitivas ═══════════════════════════════════════
def tt(d):
    return np.arange(int(round(d * SR))) / SR


def dec(t, tau):
    return np.exp(-t / tau)


def atq(t, a):
    return np.minimum(1.0, t / a)


def _f(x, tipo, f, o=2):
    if np.ndim(f):
        f = [max(20.0, f[0]), min(f[1], SR * 0.47)]
    else:
        f = min(max(20.0, f), SR * 0.47)
    return sosfilt(butter(o, f, tipo, fs=SR, output="sos"), x)


def lp(x, f, o=2):
    return _f(x, "lowpass", f, o)


def hp(x, f, o=2):
    return _f(x, "highpass", f, o)


def bp(x, lo, hi, o=2):
    return _f(x, "bandpass", [lo, hi], o)


def ruido(r, d):
    return r.standard_normal(int(round(d * SR)))


def seno(f, d=None, fase=0.0):
    """f constante ou curva (array): a fase é a integral da frequência, então o glissando sai sem estalo."""
    if np.ndim(f) == 0:
        f = np.full(len(tt(d)), float(f))
    return np.sin(fase + 2 * np.pi * np.cumsum(f) / SR)


def modal(r, fs, taus, amps, d):
    """Soma de modos amortecidos: metal, madeira, vidro e sino são isso (cada material tem as suas razões e decaimentos)."""
    t = tt(d)
    y = np.zeros_like(t)
    for f, tau, a in zip(fs, taus, amps):
        if f < SR * 0.45:
            y += a * dec(t, tau) * np.sin(2 * np.pi * f * t + r.uniform(0, 2 * np.pi))
    return y


def graos(r, d, taxa, tau, lo, hi):
    """Estalos esparsos (fibra de papel cedendo, migalha de casca, cascalho): impulsos aleatórios num filtro."""
    n = int(round(d * SR))
    imp = (r.random(n) < taxa / SR) * r.uniform(0.2, 1.0, n) * r.choice([-1.0, 1.0], n)
    k = dec(tt(tau * 6), tau)
    return bp(fftconvolve(imp, k)[:n], lo, hi)


def movel(x, fcs, q=1.5, bloco=128):
    """Passa-banda com a frequência central mudando no tempo (o ar do whoosh, o papel da página): biquad por blocos."""
    y = np.zeros_like(x)
    zi = np.zeros((1, 2))
    for i in range(0, len(x), bloco):
        fc = float(np.clip(fcs[min(i, len(fcs) - 1)], 60, SR * 0.4))
        bw = fc / q
        s = butter(1, [max(30, fc - bw / 2), min(SR * 0.45, fc + bw / 2)], "bandpass", fs=SR, output="sos")
        y[i:i + bloco], zi = sosfilt(s, x[i:i + bloco], zi=zi)
    return y


def ks(r, f, d, brilho=0.5, perda=0.996):
    """Karplus-Strong: a corda dedilhada (pizzicato)."""
    n, per = int(round(d * SR)), max(2, int(round(SR / f)))
    buf = lp(r.uniform(-1, 1, per * 4), 1500 + 9000 * brilho)[-per:]
    y = np.zeros(n)
    for i in range(n):
        y[i] = buf[i % per]
        buf[i % per] = perda * 0.5 * (buf[i % per] + buf[(i + 1) % per])
    return y


def soma(n, *partes):
    """Soma partes (array, instante em s) num vetor de n amostras."""
    y = np.zeros(n)
    for x, t0 in partes:
        i = int(round(t0 * SR))
        if i < n:
            m = min(len(x), n - i)
            y[i:i + m] += x[:m]
    return y


def mix(*xs):
    """Soma sons de durações diferentes, todos começando juntos."""
    return soma(max(len(x) for x in xs), *[(x, 0) for x in xs])


def clique(r, f=3000, tau=0.006):
    m = modal(r, [f, f * 1.93, f * 3.07], [tau, tau * 0.6, tau * 0.4], [1, 0.5, 0.25], tau * 8)
    return soma(len(m), (m, 0), (hp(ruido(r, 0.003), 2500) * dec(tt(0.003), 0.0008) * 0.6, 0))


# ═══════════════════════════════════════ banco de sons ═══════════════════════════════════════
# A base é foley GRAVADO (assets/foley da skill: os pacotes CC0 do Kenney e a biblioteca do HyperFrames); a síntese entra no
# que é desenho animado (apito de queda, mola, motor, vapor, bipe, pizzicato) e para engrossar o gravado (subgrave, migalha de
# casca). No teste às cegas de 14/10/2026 a síntese pura de objeto (moeda, papel, carrinho) soou artificial.
# Cada som: f(r, p, **args) → (sinal mono ou (n, 2), instante de sincronia em s). p = afinação (1 = original).
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # a pasta da skill (scripts/..)
FOLEY = os.path.join(RAIZ, "assets", "foley")
_K = {"i": "kenney-impact-sounds/", "r": "kenney-rpg-audio/", "c": "kenney-casino-audio/", "u": "kenney-interface-sounds/", "h": "hyperframes/"}


def _g(pref, nomes):
    return [_K[pref] + n for n in nomes]


GRUPO = {
    "folhear": _g("r", ["bookFlip1.ogg", "bookFlip2.ogg", "bookFlip3.ogg"]),
    "pousa": _g("c", ["card-place-%d.ogg" % i for i in range(1, 5)]),
    "desliza": _g("c", ["card-slide-%d.ogg" % i for i in range(1, 9)]),
    "empurra": _g("c", ["card-shove-%d.ogg" % i for i in range(1, 5)]),
    "amasso": _g("c", ["cards-pack-open-1.ogg", "cards-pack-open-2.ogg"]),
    "livro": _g("r", ["bookPlace1.ogg", "bookPlace2.ogg", "bookPlace3.ogg"]),
    "ficha": _g("c", ["chips-stack-%d.ogg" % i for i in range(1, 7)]),
    "moedas_mao": _g("r", ["handleCoins.ogg", "handleCoins2.ogg"]),
    "couro": _g("r", ["dropLeather.ogg", "handleSmallLeather.ogg", "handleSmallLeather2.ogg"]),
    "porta_abre": _g("r", ["doorOpen_1.ogg", "doorOpen_2.ogg"]),
    "porta_fecha": _g("r", ["doorClose_%d.ogg" % i for i in range(1, 5)]),
    "faca": _g("r", ["drawKnife1.ogg", "drawKnife2.ogg", "drawKnife3.ogg"]),
    "fatia": _g("r", ["knifeSlice.ogg", "knifeSlice2.ogg"]),
    "rangido": _g("r", ["creak1.ogg", "creak2.ogg", "creak3.ogg"]),
    "tecido": _g("r", ["cloth1.ogg", "cloth2.ogg", "cloth3.ogg", "cloth4.ogg"]),
    "trava": _g("r", ["metalClick.ogg", "metalLatch.ogg"]),
    "panela": _g("r", ["metalPot1.ogg", "metalPot2.ogg", "metalPot3.ogg"]),
    "madeira": _g("i", ["impactWood_light_%03d.ogg" % i for i in range(5)]),
    "madeira_media": _g("i", ["impactWood_medium_%03d.ogg" % i for i in range(5)]),
    "madeira_forte": _g("i", ["impactWood_heavy_%03d.ogg" % i for i in range(5)] + ["impactPlank_medium_%03d.ogg" % i for i in range(5)]),
    "metal_leve": _g("i", ["impactMetal_light_%03d.ogg" % i for i in range(5)]),
    "metal_medio": _g("i", ["impactMetal_medium_%03d.ogg" % i for i in range(5)]),
    "metal_pesado": _g("i", ["impactMetal_heavy_%03d.ogg" % i for i in range(5)]),
    "vidro": _g("i", ["impactGlass_light_%03d.ogg" % i for i in range(5)] + ["impactGlass_medium_%03d.ogg" % i for i in range(5)]),
    "soco": _g("i", ["impactPunch_medium_%03d.ogg" % i for i in range(5)]),
    "soco_forte": _g("i", ["impactPunch_heavy_%03d.ogg" % i for i in range(5)]),
    "macio": _g("i", ["impactSoft_medium_%03d.ogg" % i for i in range(5)]),
    "macio_forte": _g("i", ["impactSoft_heavy_%03d.ogg" % i for i in range(5)]),
    "pedra": _g("i", ["impactMining_%03d.ogg" % i for i in range(5)]),
    "prato": _g("i", ["impactPlate_light_%03d.ogg" % i for i in range(5)]),
    "sino": _g("i", ["impactBell_heavy_%03d.ogg" % i for i in range(5)]),
    "passo": _g("i", ["footstep_wood_%03d.ogg" % i for i in range(5)]),
    "passo_leve": _g("i", ["footstep_carpet_%03d.ogg" % i for i in range(5)]),
    "tique": _g("u", ["tick_001.ogg", "tick_002.ogg", "tick_004.ogg"]),
    "clique": _g("u", ["click_002.ogg", "click_003.ogg", "click_004.ogg", "click_005.ogg"]),
    "tecla": _g("u", ["select_001.ogg", "select_002.ogg", "select_007.ogg", "select_008.ogg"]),
    "chave": _g("u", ["switch_%03d.ogg" % i for i in range(1, 8)]),
    "rolagem": _g("u", ["scroll_%03d.ogg" % i for i in range(1, 6)]),
    "risco": _g("u", ["scratch_%03d.ogg" % i for i in range(1, 6)]),
    "pergunta": _g("u", ["question_%03d.ogg" % i for i in range(1, 5)]),
    "gota": _g("u", ["drop_%03d.ogg" % i for i in range(1, 5)]),
    "cristal": _g("u", ["glass_%03d.ogg" % i for i in range(1, 7)]),
    "some": _g("u", ["minimize_%03d.ogg" % i for i in range(1, 4)]),
    "surge": _g("u", ["maximize_%03d.ogg" % i for i in range(1, 4)]),
    "pop": _g("h", ["pop.wav"]) + _g("u", ["drop_002.ogg", "drop_003.ogg"]),
    "whoosh": _g("h", ["whoosh-short.wav", "whoosh.wav"]),
    "notificacao": _g("h", ["notification.wav"]),
    "brilho": _g("h", ["sparkle.wav"]),
    "sininho": _g("h", ["chime.wav"]),
    "grave": _g("h", ["impact-bass-1.wav", "impact-bass-2.wav"]),
}
_CACHE = {}


def ler(arq):
    if arq not in _CACHE:
        x, sr = sf.read(os.path.join(FOLEY, arq), always_2d=True)
        x = x.mean(1)                                   # mono: o lugar no estéreo e a sala são da mixagem
        if sr != SR:
            g = gcd(SR, sr)
            x = resample_poly(x, SR // g, sr // g)
        _CACHE[arq] = x
    return _CACHE[arq]


def amostra(r, grupo, p=1.0, pico=False, ini=None, dur=None):
    """Um arquivo do grupo (sorteado pela semente da deixa), na afinação p (varispeed), sem o silêncio do começo.
    A sincronia é o ataque (impacto) ou, com pico=True, o ponto de mais energia (ar, página virando)."""
    lista = GRUPO[grupo]
    x = ler(lista[int(r.integers(len(lista)))])
    if ini is not None:
        x = x[int(ini * SR):]
    if dur is not None:
        m = min(len(x), int(dur * SR))
        x = x[:m] * np.interp(np.arange(m), [m * 0.7, m], [1, 0])
    if p != 1.0:
        x = np.interp(np.arange(0, len(x) - 1, p), np.arange(len(x)), x)
    env = np.convolve(np.abs(x), np.ones(240) / 240, "same")
    a = max(0, int(np.argmax(env > env.max() * 0.12)) - int(0.004 * SR))
    x = x[a:]
    if pico:
        return x, float(np.argmax(np.convolve(x ** 2, np.ones(960), "same"))) / SR
    return x, 0.004


def _simples(grupo, pico=False):
    return lambda r, p=1.0, **k: amostra(r, grupo, p, pico, **k)


def em(n, *partes):
    """Como soma(), mas aceita instante negativo (corta o começo)."""
    out = []
    for x, t0 in partes:
        if t0 < 0:
            x, t0 = x[int(-t0 * SR):], 0.0
        out.append((x, t0))
    return soma(n, *out)


def sub(p=1.0, f0=110, f1=45, tau=0.07, d=0.35):
    t = tt(d)
    return seno(np.interp(t, [0, 0.12], [f0 * p, f1 * p]), d) * dec(t, tau) * atq(t, 0.002)


def igual(a, b, g=1.0):
    """b no nível de pico de a (vezes g): para somar síntese a gravado sem um engolir o outro."""
    return b * np.abs(a).max() / (np.abs(b).max() + 1e-9) * g


# ── composições (gravado + síntese) ──
def s_quadro(r, p=1.0):
    """Quadro do gibi entrando: o ar (pico em 0,10 s) e o papel assentando na página (0,27 s)."""
    w, sw = amostra(r, "whoosh", p * r.uniform(0.9, 1.2), True)
    l, _ = amostra(r, "pousa", p)
    return em(int(0.9 * SR), (w, 0.10 - sw), (igual(w, l, 0.35), 0.27)), 0.0


def s_carimbo(r, p=1.0):
    """Carimbo de borracha: o tapa na mesa (livro), o baque da borracha e um subgrave curto."""
    a, _ = amostra(r, "livro", p)
    b, _ = amostra(r, "macio", p * 0.9)
    return mix(a, igual(a, b, 0.6), igual(a, sub(p), 0.5)), 0.004


def s_soco(r, p=1.0, forte=False):
    a, _ = amostra(r, "soco_forte" if forte else "soco", p)
    return mix(a, igual(a, sub(p, 90, 40, 0.1), 0.6)), 0.004


def s_bum(r, p=1.0):
    """BUM: o soco pesado, o grave cinematográfico, o ronco e as pedras caindo depois."""
    d = 1.4
    t = tt(d)
    a, _ = amostra(r, "soco_forte", p * 0.85)
    g, _ = amostra(r, "grave", p)
    pd, _ = amostra(r, "pedra", p * 1.1)
    ronco = lp(ruido(r, d), 220) * dec(t, 0.3)
    return em(len(t), (a, 0), (igual(a, g, 0.6), 0), (igual(a, ronco, 0.5), 0), (igual(a, pd, 0.45), 0.08)), 0.004


def s_plaft(r, p=1.0):
    """PLAFT: o peso caindo em cima (metal pesado + corpo macio esmagado + subgrave)."""
    a, _ = amostra(r, "macio_forte", p * 0.85)
    b, _ = amostra(r, "metal_pesado", p * 0.8)
    return mix(a, igual(a, b, 0.55), igual(a, sub(p, 80, 35, 0.12, 0.5), 0.8)), 0.004


def s_corte(r, p=1.0):
    """A carretilha atravessando a casca: a lâmina gravada e as migalhas crocantes sintetizadas por cima."""
    a, _ = amostra(r, "fatia", p * 1.1, dur=0.35)
    d = 0.2
    t = tt(d)
    croc = graos(r, d, 2500, 0.0012, 1200 * p, 5500) * np.interp(t, [0, 0.02, 0.12, d], [0, 1, 0.7, 0])
    return mix(a, igual(a, croc, 0.5)), 0.004


def s_mordida(r, p=1.0):
    """NHAC: duas quebradas de casca (a mordida e o pedaço soltando) e o 'chomp' abafado."""
    d = 0.3
    t = tt(d)
    croc = graos(r, d, 3000, 0.0012, 800 * p, 4500) * np.interp(t, [0, 0.01, 0.05, 0.07, 0.1, 0.16], [0, 1, 0.3, 0.9, 0.4, 0]) * 3
    chomp = bp(ruido(r, d), 200, 800) * dec(t, 0.04) * 1.2
    m, _ = amostra(r, "macio", p * 1.3)
    y = croc + chomp
    return mix(y, igual(y, m, 0.5)), 0.0


def s_mastiga(r, p=1.0):
    d = 0.1
    t = tt(d)
    return graos(r, d, 1500, 0.001, 700 * p, 3500) * np.interp(t, [0, 0.02, d], [0, 1, 0]) * 2 + \
        bp(ruido(r, d), 150, 500) * dec(t, 0.03) * 0.5, 0.0


def s_moeda(r, p=1.0):
    """Moeda: o clique real de ficha (o contato) e o 'tin' do metal ressoando curto."""
    a, _ = amostra(r, "ficha", p * 1.3)
    f0 = r.uniform(2900, 3600) * p
    ring = modal(r, f0 * np.array([1, 1.52, 2.07, 2.62, 3.36]), [0.09, 0.07, 0.05, 0.04, 0.03], [1, 0.7, 0.5, 0.35, 0.2], 0.3)
    return mix(a * 0.9, igual(a, ring, 0.18)), 0.004


def s_moedas(r, p=1.0, d=1.2, taxa=8):
    """Chuva de moedas: trechos do punhado de moedas gravado e moedas soltas, cada uma num lugar do estéreo."""
    n = int(round(d * SR))
    y = np.zeros((n, 2))
    pecas = [amostra(r, "moedas_mao", p * r.uniform(0.95, 1.15), ini=r.uniform(0, 0.3), dur=r.uniform(0.25, 0.5))[0] for _ in range(2)]
    pecas += [s_moeda(r, p * r.uniform(0.9, 1.25))[0] * r.uniform(0.3, 0.8) for _ in range(max(1, int(d * taxa)))]
    for x in pecas:
        i, pan = int(r.uniform(0, d * 0.85) * SR), r.uniform(-0.8, 0.8)
        m = min(len(x), n - i)
        y[i:i + m, 0] += x[:m] * np.sqrt((1 - pan) / 2)
        y[i:i + m, 1] += x[:m] * np.sqrt((1 + pan) / 2)
    return y, 0.0


def s_saco_moedas(r, p=1.0):
    """Saco de moedas assentando: o couro caindo e as moedas abafadas lá dentro."""
    a, _ = amostra(r, "couro", p)
    b, _ = amostra(r, "moedas_mao", p, ini=r.uniform(0, 0.2), dur=0.35)
    return mix(a, igual(a, lp(b, 4500), 0.6)), 0.004


def s_registradora(r, p=1.0):
    """Ka-ching: a gaveta (trava metálica + moedas) e o sino brilhante; a sincronia é o 'ching'."""
    d = 1.4
    tr, _ = amostra(r, "trava", p)
    mo, _ = amostra(r, "moedas_mao", p, ini=0.05, dur=0.3)
    f0 = 2350 * p
    sino = modal(r, f0 * np.array([1, 2.01, 2.73, 4.16, 5.43]), [0.9, 0.55, 0.4, 0.22, 0.13], [1, 0.5, 0.6, 0.3, 0.2], d)
    sino += modal(r, (f0 + 2.2) * np.array([1, 2.73]), [0.8, 0.35], [0.6, 0.3], d)
    sino *= atq(tt(d), 0.002)
    return em(int(d * SR), (tr, 0), (igual(tr, mo, 0.5), 0.03), (igual(tr, sino, 0.8), 0.12)), 0.12


def s_cofrinho(r, p=1.0):
    """Moeda entrando no cofrinho: o 'tin' na fenda e a barriga de cerâmica."""
    m, _ = s_moeda(r, p * 1.1)
    c, _ = amostra(r, "prato", p * 1.2)
    return em(int(0.8 * SR), (m, 0), (igual(m, c, 0.8), 0.05)), 0.0


def s_guarda_chuva(r, p=1.0):
    """Guarda-chuva abrindo: o tecido esticando (gravado) e o clique da trava; sincronia no estalo."""
    a, sa = amostra(r, "tecido", p, True)
    b, _ = amostra(r, "trava", p * 1.2)
    return em(int(0.9 * SR), (a, 0.22 - sa), (igual(a, b, 0.4), 0.2)), 0.22


def s_toc_tecido(r, p=1.0):
    a, _ = amostra(r, "macio", p * 1.25)
    b, _ = amostra(r, "tecido", p * 1.2, dur=0.15)
    return mix(a, igual(a, b, 0.4)), 0.004


def s_squish(r, p=1.0):
    """SQUISH: o corpo macio sendo prensado (gravado, mais grave) e o molhado sintetizado por cima."""
    a, _ = amostra(r, "macio_forte", p * 0.8)
    d = 0.4
    t = tt(d)
    fcs = np.interp(t, [0, 0.08, 0.2, d], [450 * p, 1300 * p, 700 * p, 500 * p]) * (1 + 0.25 * np.sin(2 * np.pi * 28 * t))
    mol = movel(ruido(r, d), fcs, 4.0) * np.interp(t, [0, 0.02, 0.25, d], [0, 1, 0.5, 0])
    return mix(a, igual(a, mol, 0.45)), 0.004


def s_obturador(r, p=1.0):
    """Câmera: a trava metálica (abre) e o clique (fecha) 55 ms depois."""
    a, _ = amostra(r, "trava", p * 1.3)
    b, _ = amostra(r, "clique", p)
    return em(int(0.4 * SR), (a, 0), (igual(a, b, 0.8), 0.055)), 0.004


def s_carrinho(r, p=1.0, d=0.65):
    """Carrinho de supermercado: rodinhas de metal batendo (desacelerando) e o rolamento roncando."""
    n = int(round(d * SR))
    partes, tk = [], 0.0
    while tk < d * 0.85:
        x, _ = amostra(r, "metal_leve", p * r.uniform(1.4, 1.8), dur=0.08)
        partes.append((x * r.uniform(0.25, 0.6), tk))
        tk += 1 / np.interp(tk, [0, d], [30, 9])
    t = np.arange(n) / SR
    rolo = lp(ruido(r, d), 250) * (1 + 0.5 * np.sin(2 * np.pi * 18 * t)) * np.interp(t, [0, 0.05, d], [0, 1, 0])
    y = soma(n, *partes)
    return y + igual(y, rolo, 0.5), 0.0


def s_adesivo(r, p=1.0):
    a, _ = amostra(r, "pousa", p * 1.1)
    b, _ = amostra(r, "macio", p * 1.4)
    return mix(a, igual(a, b, 0.4)), 0.004


def s_papelao(r, p=1.0):
    return amostra(r, "livro", p * 0.8)


def s_medalha(r, p=1.0):
    a, _ = amostra(r, "metal_leve", p * 1.4)
    b, _ = amostra(r, "tecido", p * 1.3, dur=0.2)
    return mix(a, igual(a, b, 0.3)), 0.004


def s_dun(r, p=1.0):
    """Nota grave de alerta: o sino pesado mais grave e o subgrave."""
    a, _ = amostra(r, "sino", p * 0.6)
    return mix(a, igual(a, sub(p, 60, 40, 0.3, 0.8), 0.6)), 0.004


# ── síntese pura (o que é desenho animado) ──
def s_boing(r, p=1.0, f=150):
    """Mola: o tom sobe de uma vez e vibra descendo, com o 'twang' metálico por cima."""
    d = 0.75
    t = tt(d)
    fr = f * p * (1 + 0.55 * dec(t, 0.28) * np.sin(2 * np.pi * 10 * t)) * (1 + 0.6 * (1 - dec(t, 0.015)))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = bp((np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) * atq(t, 0.004) * dec(t, 0.3), 90, 3500)
    a, _ = amostra(r, "metal_leve", p * 0.9)
    return mix(y, igual(y, a, 0.3)), 0.0


def s_pulo(r, p=1.0):
    d = 0.13
    t = tt(d)
    return seno(np.interp(t, [0, 0.06], [300 * p, 720 * p]), d) * atq(t, 0.003) * dec(t, 0.035), 0.0


def s_catraca(r, p=1.0, d=0.85, taxa=26):
    """Manivela: catraca estalando."""
    partes = [(amostra(r, "tique", p * r.uniform(0.7, 0.9))[0] * r.uniform(0.6, 1), k / taxa * r.uniform(0.92, 1.08))
              for k in range(int(d * taxa))]
    return soma(int(round(d * SR)), *partes), 0.0


def s_bip(r, p=1.0, f=2600, d=0.07):
    t = tt(d)
    y = (seno(f * p, d) + 0.15 * seno(3 * f * p, d)) * np.minimum(atq(t, 0.003), np.clip((d - t) / 0.01, 0, 1))
    return lp(y, 6000), 0.0


def s_bip_erro(r, p=1.0):
    """A maquininha recusando: dois tons graves descendo."""
    def tom(f, d):
        t = tt(d)
        y = seno(f, d) + 0.3 * seno(3 * f, d) + 0.15 * seno(5 * f, d)
        return lp(y * np.minimum(atq(t, 0.004), np.clip((d - t) / 0.015, 0, 1)), 2500)
    return soma(int(0.36 * SR), (tom(620 * p, 0.12), 0), (tom(470 * p, 0.16), 0.17)), 0.0


def s_motor(r, p=1.0):
    """VRUM: o motor acelerando (pulsos de explosão num filtro) e o escapamento; passa da esquerda para o centro."""
    d = 0.8
    t = tt(d)
    fr = np.interp(t, [0, 0.35, 0.55, d], [38, 105, 90, 80]) * p
    ph = 2 * np.pi * np.cumsum(fr) / SR
    puls = sum(np.sin(k * ph) / k ** 0.9 for k in range(1, 26))
    y = lp(puls, 1400, 4) * (0.7 + 0.3 * np.sin(ph)) + lp(ruido(r, d), 800) * (0.5 + 0.5 * np.sin(ph)) * 0.6
    y *= np.interp(t, [0, 0.05, 0.5, d], [0, 1, 1, 0])
    pan = np.interp(t, [0, d], [-0.8, 0.0])
    return np.stack([y * np.sqrt((1 - pan) / 2), y * np.sqrt((1 + pan) / 2)], 1) * 1.41, 0.0


def s_vapor(r, p=1.0):
    """Vapor saindo da cabeça (raiva de desenho): o 'pff' e o chiado."""
    d = 0.6
    t = tt(d)
    return hp(bp(ruido(r, d), 3500 * p, 10000), 2500) * atq(t, 0.015) * dec(np.maximum(0, t - 0.1), 0.18) * 1.5 + \
        lp(ruido(r, d), 700) * dec(t, 0.03) * 0.6, 0.0


def s_pluck(r, p=1.0, f=392.0, d=0.9):
    y = ks(r, f * p, d, 0.55)
    return bp(y, 120, 6000) * dec(tt(d), d / 2.5), 0.0


def s_apito(r, p=1.0, d=0.7, f0=1500, f1=260):
    """Apito de êmbolo descendo (a queda do desenho animado)."""
    t = tt(d)
    fr = f0 * p * (f1 / f0) ** (t / d) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    y = np.sin(ph) + 0.1 * np.sin(2 * ph) + lp(ruido(r, d), 3000) * 0.04
    return y * np.minimum(atq(t, 0.03), np.clip((d - t) / 0.06, 0, 1)), 0.0


def s_globo(r, p=1.0, d=1.6):
    """Globo girando e desacelerando: o zumbido do eixo pulsando na velocidade da volta."""
    t = tt(d)
    rot = np.interp(t, [0, d], [9, 1.5])
    ph = 2 * np.pi * np.cumsum(rot) / SR
    return bp(ruido(r, d), 250 * p, 1100 * p) * (0.6 + 0.4 * np.sin(ph)) * np.interp(t, [0, 0.05, d], [0, 1, 0]), 0.0


def s_caneta(r, p=1.0, d=0.35, larga=False):
    """Caneta (ou marca-texto, com larga=True) riscando o papel: traços curtos de atrito, cada um com o toque da ponta."""
    n = int(round(d * SR))
    lo, hi = (1200, 4500) if larga else (2200, 7500)
    partes, t0 = [], 0.0
    while t0 < d - 0.03:
        dt = r.uniform(0.05, 0.12)
        k = tt(dt)
        tr = bp(r.standard_normal(len(k)), lo * p, hi) * np.sin(np.pi * k / dt) ** 0.7 * r.uniform(0.5, 1.0)
        partes.append((tr * (1 + 0.3 * np.sin(2 * np.pi * r.uniform(25, 45) * k)), t0))
        partes.append((clique(r, 3200 * p, 0.002) * 0.15, t0))
        t0 += dt * r.uniform(0.8, 1.1)
    return soma(n, *partes), 0.0


def s_tremor(r, p=1.0, n=6, passo=0.035):
    """Treme-treme (o vidro do medidor chacoalhando): batidas de vidro que diminuem."""
    partes = [(amostra(r, "vidro", p * r.uniform(1.3, 1.6), dur=0.06)[0] * (1 - k / n) * 0.6, k * passo) for k in range(n)]
    return soma(int((n * passo + 0.1) * SR), *partes), 0.0


for _nome, _grupo, _pico in [
    ("pagina", "folhear", True), ("pousa", "pousa", False), ("desliza", "desliza", True), ("empurra", "empurra", True),
    ("amasso", "amasso", False), ("livro", "livro", False), ("porta_abre", "porta_abre", False), ("porta_fecha", "porta_fecha", False),
    ("faca", "faca", False), ("rangido", "rangido", False), ("tecido", "tecido", True), ("trava", "trava", False),
    ("panela", "panela", False), ("madeira", "madeira", False), ("madeira_media", "madeira_media", False),
    ("madeira_forte", "madeira_forte", False), ("metal_leve", "metal_leve", False), ("metal_medio", "metal_medio", False),
    ("vidro", "vidro", False), ("passo", "passo", False), ("passo_leve", "passo_leve", False), ("tique", "tique", False),
    ("clique", "clique", False), ("tecla", "tecla", False), ("chave", "chave", False), ("rolagem", "rolagem", True),
    ("risco", "risco", False), ("pergunta", "pergunta", False), ("gota", "gota", False), ("cristal", "cristal", False),
    ("some", "some", True), ("surge", "surge", True), ("pop", "pop", False), ("whoosh", "whoosh", True),
    ("notificacao", "notificacao", False), ("brilho", "brilho", False), ("sininho", "sininho", False), ("macio", "macio", False),
    ("prato", "prato", False), ("moedas_mao", "moedas_mao", False), ("pedra", "pedra", False), ("grave", "grave", False)]:
    globals()["s_" + _nome] = _simples(_grupo, _pico)


SONS = {k[2:]: v for k, v in globals().items() if k.startswith("s_")}


# ═══════════════════════════════════════ medidas ═══════════════════════════════════════
def kpeso(x):
    """Filtro K da BS.1770 (48 kHz): o ouvido pesa menos o grave e mais o agudo."""
    x = lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585], x)
    return lfilter([1.0, -2.0, 1.0], [1, -1.99004745483398, 0.99007225036621], x)


def curto(x, jan=0.05, passo=0.01):
    """Loudness curta (dB) em janelas deslizantes."""
    q = np.concatenate([[0], np.cumsum(kpeso(x) ** 2)])
    w, h = int(jan * SR), int(passo * SR)
    i = np.arange(0, max(1, len(x) - w), h)
    return 10 * np.log10((q[i + w] - q[i]) / w + 1e-12)


def lufs(x):
    """Loudness integrada (BS.1770: filtro K, blocos de 400 ms, portas de −70 LUFS e −10 LU)."""
    x = x if x.ndim == 2 else x[:, None]
    w, h = int(0.4 * SR), int(0.1 * SR)
    ms = sum(np.array([np.mean(c[i:i + w] ** 2) for i in range(0, len(c) - w, h)]) for c in (kpeso(x[:, j]) for j in range(x.shape[1])))
    l = -0.691 + 10 * np.log10(ms + 1e-12)
    ms = ms[l > -70]
    l = -0.691 + 10 * np.log10(ms.mean())
    return -0.691 + 10 * np.log10(ms[-0.691 + 10 * np.log10(ms + 1e-12) > l - 10].mean())


def mono(x):
    return x.mean(1) if x.ndim == 2 else x


# ═══════════════════════════════════════ deixas ═══════════════════════════════════════
def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9%*]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


EASE = {
    "linear": lambda u: u,
    "power1.out": lambda u: 1 - (1 - u) ** 2, "power2.out": lambda u: 1 - (1 - u) ** 3, "power3.out": lambda u: 1 - (1 - u) ** 4,
    "power2.in": lambda u: u ** 3, "power3.in": lambda u: u ** 4,
    "power2.inOut": lambda u: np.where(u < 0.5, 4 * u ** 3, 1 - (-2 * u + 2) ** 3 / 2),
    "sine.inOut": lambda u: -(np.cos(np.pi * u) - 1) / 2,
}
QUIQUES = [(0.3636, 0.0), (0.7273, -8.0), (0.9091, -15.0), (1.0, -21.0)]   # contatos do bounce.out (GSAP) e o ganho de cada


def expandir(deixas, palavras):
    def T(p, t0=0.0):
        n = _norm(p)
        for w in palavras:
            if _norm(w["w"]) == n and w["s"] >= t0 - 0.12:
                return w["s"]
        raise SystemExit("✗ palavra não encontrada: %s (a partir de %.2f)" % (p, t0))

    out = []
    for i, d in enumerate(deixas):
        base = {**d, "semente": d.get("semente", i * 7919 + 17)}
        if "palavras" in d or "em" in d:     # um som em cada palavra dita no intervalo (texto aparecendo) ou em cada instante da lista
            if "palavras" in d:
                ts = []
                for w in palavras:
                    if d["palavras"][0] <= w["s"] < d["palavras"][1] and (not ts or w["s"] - ts[-1] >= 0.07):
                        ts.append(w["s"])
            else:
                ts = d["em"]
            for k, t in enumerate(ts):
                out.append({**base, "t": t + d.get("desloc", 0), "semente": base["semente"] + k})
            continue
        t = d["t"]
        t = T(t[0], t[1]) + (t[2] if len(t) > 2 else 0) if isinstance(t, list) else float(t)
        base["t"] = t
        if "quica" in d:                     # um tween bounce.out de `quica` s começando em t: um som em cada contato
            for k, (u, g) in enumerate(QUIQUES):
                out.append({**base, "t": t + u * d["quica"], "db": d.get("db", 0) + g, "semente": base["semente"] + k})
        elif "ease" in d:                    # tiques que seguem a curva: `n` tiques num tween de `dur` s com `ease`
            u = np.linspace(0, 1, 2001)
            v = EASE[d["ease"]](u)
            for k in range(1, d["n"] + 1):
                out.append({**base, "t": t + float(u[np.searchsorted(v, k / d["n"])]) * d["dur"], "semente": base["semente"] + k})
        else:
            n = d.get("rep", 1)
            for k in range(n):                # repetição: passo no tempo, `sobe` semitons a cada uma, pan andando até `pan_ate`
                out.append({**base, "t": t + k * d.get("passo", 0), "semente": base["semente"] + k,
                            "p": d.get("p", 1.0) * 2 ** (k * d.get("sobe", 0) / 12),
                            "pan": d.get("pan", 0) + (d.get("pan_ate", d.get("pan", 0)) - d.get("pan", 0)) * k / max(1, n - 1)})
    return sorted(out, key=lambda c: c["t"])


# ═══════════════════════════════════════ mixagem ═══════════════════════════════════════
def sala():
    """Resposta de uma sala pequena (RT60 ~0,4 s), estéreo descorrelacionado, com reflexões iniciais."""
    r = np.random.default_rng(5)
    t = tt(0.6)
    ir = np.stack([lp(r.standard_normal(len(t)), 5500) * dec(t, 0.4 / 6.9) for _ in range(2)], 1)
    ir[: int(0.008 * SR)] = 0
    for ms, g in ((11, 0.5), (17, 0.35), (23, 0.3), (31, 0.22)):
        ir[int(ms * SR / 1000), 0] += g
        ir[int((ms + 3) * SR / 1000), 1] += g
    return ir / np.sqrt((ir ** 2).sum(0)).max()


def atividade(voz):
    """0 a 1: quanto a voz está falando agora (loudness de 20 ms), com 15 ms de antecipação."""
    lv = curto(voz, 0.02, 0.005)
    ref = np.percentile(lv[lv > -60], 95) if (lv > -60).any() else -20.0   # voz muda (o modelo de teste)
    a = np.clip((lv - (ref - 26)) / 12, 0, 1)
    a = np.concatenate([a[3:], a[-1:].repeat(3)])          # 15 ms de antecipação
    g = np.zeros_like(a)
    for i in range(1, len(a)):                             # sobe em ~10 ms, desce em ~200 ms
        k = 0.4 if a[i] > g[i - 1] else 0.025
        g[i] = g[i - 1] + k * (a[i] - g[i - 1])
    return np.interp(np.arange(len(voz)) / SR, np.arange(len(g)) * 0.005 + 0.01, g)


def gerar(c, vref):
    r = np.random.default_rng(c["semente"])
    p = c.get("p", 1.0) * 2 ** (r.uniform(-1, 1) / 12 * c.get("varia", 1.0))
    x, sync = SONS[c["som"]](r, p, **c.get("args", {}))
    x = np.asarray(x, float)
    fim = np.interp(np.arange(len(x)), [len(x) - 64, len(x) - 1], [1, 0])        # sem estalo no fim
    x *= fim[:, None] if x.ndim == 2 else fim
    pico = curto(mono(x)).max() if len(x) > int(0.05 * SR) else curto(np.pad(mono(x), (0, int(0.06 * SR)))).max()
    alvo = vref + CAMADA[c["camada"]]["nivel"] + REALCE.get(c["camada"], 0.0) + c.get("db", 0) + r.uniform(-1, 1)
    x *= 10 ** ((alvo - pico) / 20)
    if x.ndim == 1:
        pan = np.clip(c.get("pan", 0.0), -1, 1) * PAN_MAX
        x = np.stack([x * np.sqrt((1 - pan) / 2), x * np.sqrt((1 + pan) / 2)], 1) * 1.41
    return x, sync


def mixar(pasta):
    folha = json.load(open(os.path.join(pasta, "som.json"), encoding="utf-8"))
    tempos = json.load(open(os.path.join(pasta, "assets", "tempos.json"), encoding="utf-8"))
    palavras = sorted((w for b in tempos["blocos"] for w in b["palavras"]), key=lambda w: w["s"])
    voz, sr = sf.read(os.path.join(pasta, "assets", "raul.wav"), always_2d=True)
    assert sr == SR, "a voz precisa estar em 48 kHz"
    vm = voz.mean(1)
    n = len(vm)
    lv = curto(vm)
    vref = np.percentile(lv[lv > -60], 95) if (lv > -60).any() else -20.0   # voz muda (o modelo de teste): referência padrão
    deixas = expandir(folha["deixas"], palavras)
    errados = sorted({c["som"] for c in deixas} - set(SONS))
    if errados:   # C87: um nome fora do catálogo parava a mixagem no meio com KeyError
        raise SystemExit("⛔ som que não existe no som.json: %s. Nomes válidos: %s" % (", ".join(errados), ", ".join(sorted(SONS))))

    camadas = {k: np.zeros((n, 2)) for k in CAMADA}
    for c in deixas:
        x, sync = gerar(c, vref)
        i = int(round((c["t"] - sync) * SR))
        if i < 0:
            x, i = x[-i:], 0
        m = min(len(x), n - i)
        if m > 0:
            camadas[c["camada"]][i:i + m] += x[:m]

    a = atividade(vm)[:, None]
    ir = sala()
    # proteção da fala: em cada 10 ms com fala, se os efeitos chegam a menos de `folga` dB da voz na faixa da fala (300 Hz–
    # 4,5 kHz), primeiro só essa faixa dos efeitos abaixa o que faltar (o grave do soco e o brilho ficam); no fundo, se o
    # que vaza do grave ou do agudo ainda passa, o efeito inteiro desce o resto. Ataque imediato, volta em ~80 ms.
    q = int(0.01 * SR)
    nq = n // q
    ev = (bp(vm, 300, 4500, 4)[:nq * q] ** 2).reshape(nq, q).mean(1)
    fala = a[::q, 0][:nq] > 0.12

    def falta(x, folga, so_meio=False):
        es = ((x.mean(1) if so_meio else bp(x.mean(1), 300, 4500, 4))[:nq * q] ** 2).reshape(nq, q).mean(1)
        f = np.clip(10 * np.log10((es + 1e-12) / (ev + 1e-12)) + folga, 0, 30) * fala
        f = np.maximum.reduce([np.roll(f, k) for k in (-2, -1, 0, 1)])         # abre um pouco antes do pico
        for i in range(1, nq):
            f[i] = max(f[i], f[i - 1] * 0.88)                                  # volta em ~80 ms
        return 10 ** (-np.interp(np.arange(n), np.arange(nq) * q + q / 2, f) / 20)[:, None]

    def protege(x, folga, inteiro):
        baixo = sosfiltfilt(butter(4, 300, "lowpass", fs=SR, output="sos"), x, axis=0)
        alto = sosfiltfilt(butter(4, 4500, "highpass", fs=SR, output="sos"), x, axis=0)
        meio = (x - baixo - alto) * 10 ** (-CARVE * a / 20)                    # EQ dinâmico fixo enquanto ele fala
        meio *= falta(meio, folga, True)
        y = baixo + alto + meio
        return y * falta(y, folga) if inteiro else y

    # o destaque (carimbo, BUM, PLAFT) é a pancada combinada com a palavra: folga menor e o grave intocado
    fundo, frente, envio = np.zeros((n, 2)), np.zeros((n, 2)), np.zeros((n, 2))
    for k, x in camadas.items():
        x = x * 10 ** (-CAMADA[k]["duck"] * a / 20)
        if k == "destaque":
            frente += x
        else:
            fundo += x
        envio += x * CAMADA[k]["sala"]
    fundo += np.stack([fftconvolve(envio[:, j], ir[:, j])[:n] for j in range(2)], 1)
    bus = protege(fundo, FOLGA, True) + protege(frente, FOLGA_DESTAQUE, False)
    # subgrave fora (abaixo de 70 Hz, 24 dB/oitava): o celular não reproduz e o loudnorm contaria, baixando a voz
    bus = sosfiltfilt(butter(2, 70, "highpass", fs=SR, output="sos"), bus, axis=0)
    bus = sosfiltfilt(butter(2, 16000, "lowpass", fs=SR, output="sos"), bus, axis=0)
    # teto: nem no respiro um efeito fica mais alto que a fala (ganho por quadro de 10 ms, volta em ~150 ms)
    lb = curto(bus.mean(1), 0.05, 0.01)
    corta = np.clip(lb - (vref + TETO), 0, None)
    for i in range(1, len(corta)):
        corta[i] = max(corta[i], corta[i - 1] * 0.935)
    bus *= 10 ** (-np.interp(np.arange(n), np.arange(len(corta)) * q + 0.025 * SR, corta) / 20)[:, None]
    # limitador de pico (−9 dBFS): o estalo do carimbo não pode empurrar o pico da mixagem e travar o loudnorm linear
    lim = 10 ** (PICO / 20)
    ms = SR // 1000
    nm = n // ms
    pk = np.abs(bus[:nm * ms]).max(1).reshape(nm, ms).max(1)
    g = np.minimum(1.0, lim / np.maximum(pk, 1e-9))
    g = np.minimum.reduce([np.roll(g, k) for k in (-2, -1, 0, 1)])                # 2 ms de antecipação
    for i in range(1, nm):
        if g[i] > g[i - 1]:
            g[i] = g[i - 1] + (g[i] - g[i - 1]) * 0.02                           # solta em ~50 ms
    bus *= np.interp(np.arange(n), np.arange(nm) * ms + ms / 2, g)[:, None]

    sf.write(os.path.join(pasta, "assets", "sfx_mix.wav"), np.clip(bus, -1, 1), SR, subtype="PCM_16")
    mix = voz + bus
    pk = np.abs(mix).max()
    if pk > 0.89:                          # o loudnorm do finalizar.py ajusta o volume; aqui só não deixa clipar
        mix *= 0.89 / pk
    os.makedirs(os.path.join(pasta, "renders"), exist_ok=True)
    sf.write(os.path.join(pasta, "renders", "som_mix.wav"), mix, SR, subtype="PCM_24")
    relatorio(pasta, folha, deixas, voz, bus, palavras)


def relatorio(pasta, folha, deixas, voz, bus, palavras):
    linhas = []
    w = int(0.4 * SR)

    def jan(x):
        x = mono(x)
        return np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-12) for i in range(0, len(x) - w, w)])
    vv, ss = jan(voz), jan(bus)
    ativo = ss > -80
    linhas.append("NÍVEL (RMS em janelas de 0,4 s)")
    linhas.append("  voz (janelas com fala): %.1f dB" % np.median(vv[vv > vv.max() - 30]))
    linhas.append("  efeitos: mediana %.1f · p90 %.1f · máx %.1f dB  (C77 antigo: −48,1 · −27,3 · −24,4)" %
                  (np.median(ss[ativo]), np.percentile(ss[ativo], 90), ss.max()))
    linhas.append("  pico: voz %.1f dBFS · efeitos %.1f dBFS" % (20 * np.log10(np.abs(voz).max()), 20 * np.log10(np.abs(bus).max() + 1e-12)))
    lv_, lm_ = lufs(voz), lufs(voz + bus)
    linhas.append("  loudness integrada: voz %.1f · voz + efeitos %.1f LUFS → no −14 do finalizar a voz desce %.1f dB" % (lv_, lm_, lm_ - lv_))
    linhas.append("")
    cont = {}
    for c in deixas:
        cont[c["camada"]] = cont.get(c["camada"], 0) + 1
    linhas.append("DEIXAS: %d sons de %d tipos · %s" % (len(deixas), len({c["som"] for c in deixas}),
                                                     " · ".join("%s %d" % kv for kv in sorted(cont.items(), key=lambda kv: -kv[1]))))
    dur = len(voz) / SR
    dens = np.histogram([c["t"] for c in deixas if c["camada"] != "textura"], bins=int(np.ceil(dur / 10)), range=(0, np.ceil(dur / 10) * 10))[0]
    linhas.append("  por 10 s (sem textura): " + " ".join(str(x) for x in dens))
    linhas.append("")
    # mascaramento: na faixa da fala, quanto a voz fica acima dos efeitos em cada palavra
    vb = bp(mono(voz), 300, 4500, 4)
    sb = bp(mono(bus), 300, 4500, 4)
    ruins = []
    for k, p in enumerate(palavras):
        s = p["s"]
        e = palavras[k + 1]["s"] if k + 1 < len(palavras) else p["e"]
        e = min(e, s + 0.6)
        if e - s < 0.06:
            continue
        i, j = int(s * SR), int(e * SR)
        snr = 10 * np.log10((np.mean(vb[i:j] ** 2) + 1e-12) / (np.mean(sb[i:j] ** 2) + 1e-12))
        if snr < 10:
            ruins.append((snr, p["w"], s))
    linhas.append("MASCARAMENTO (voz − efeitos na faixa 300 Hz–4,5 kHz, por palavra): %d palavras abaixo de 10 dB" % len(ruins))
    for snr, w_, s in sorted(ruins)[:15]:
        linhas.append("  %6.2f s  %-14s %.1f dB" % (s, w_, snr))
    # audibilidade: o efeito é ouvido se, em alguma banda de oitava, chega a 6 dB da voz nos 150 ms em que toca
    linhas.append("")
    oit = [(100 * 2 ** k, 200 * 2 ** k) for k in range(7)]
    V = [bp(mono(voz), lo, hi, 3) for lo, hi in oit]
    B = [bp(mono(bus), lo, hi, 3) for lo, hi in oit]
    aud = {}
    for c in deixas:
        i, j = int(max(0, c["t"] - 0.01) * SR), int((c["t"] + 0.15) * SR)
        snr = max(10 * np.log10((np.mean(b[i:j] ** 2) + 1e-14) / (np.mean(v[i:j] ** 2) + 1e-12)) for v, b in zip(V, B))
        aud.setdefault(c["camada"], []).append((snr, c["t"], c["som"]))
    linhas.append("AUDIBILIDADE (passa de −6 dB contra a voz em alguma oitava): " + " · ".join(
        "%s %.0f%%" % (k, 100 * np.mean([x[0] > -6 for x in L])) for k, L in sorted(aud.items())))
    for k in ("destaque", "acao"):
        for snr, t, s in sorted(aud.get(k, []))[:5]:
            if snr <= -6:
                linhas.append("  abafado: %6.2f s  %-13s %-9s %.1f dB" % (t, s, k, snr))
    txt = "\n".join(linhas)
    open(os.path.join(pasta, "som_relatorio.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)


def mux(pasta):
    r = os.path.join(pasta, "renders")
    bruto = os.path.join(r, "etapa3_bruto.mp4")
    so_video = os.path.join(r, "etapa3_bruto_imagem.mp4")
    # guarda a imagem do render; o áudio sai sempre do som_mix.wav. O render sai com AAC e o mux grava FLAC: um etapa3_bruto
    # em AAC é render NOVO e substitui a imagem guardada (C82, 16/10/2026: o mux de depois de um 2º render usava a imagem do 1º)
    codec = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "csv=p=0",
                            bruto], capture_output=True, text=True).stdout.strip()
    if not os.path.exists(so_video) or codec != "flac":
        os.replace(bruto, so_video)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", so_video, "-i", os.path.join(r, "som_mix.wav"), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "flac", bruto], check=True)
    print("✓ %s com o som novo (imagem do render, áudio sem perda)" % bruto)


def catalogo(saida):
    os.makedirs(saida, exist_ok=True)
    for nome, f in SONS.items():
        x = np.asarray(f(np.random.default_rng(1), 1.0)[0], float)
        x = x / (np.abs(x).max() + 1e-9) * 0.7
        sf.write(os.path.join(saida, nome + ".wav"), x, SR, subtype="PCM_16")
    print("%d sons em %s" % (len(SONS), saida))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    if sys.argv[1] == "--catalogo":
        catalogo(sys.argv[2])
    else:
        mixar(sys.argv[1])
        if "--mux" in sys.argv:
            mux(sys.argv[1])
        else:
            # último passo antes do render: erro de JavaScript (C47) e a área de segurança da animação (Mickael, 17/10/2026,
            # depois do C80/C83: etiqueta embaixo da busca do TikTok, carimbo saindo pela lateral, perna embaixo do texto do post)
            aqui = os.path.dirname(os.path.abspath(__file__))
            for js, args in (("erros_js.mjs", [os.path.join(sys.argv[1], "index.html")]), ("zona_segura.mjs", [sys.argv[1]])):
                r = subprocess.run(["node", os.path.join(aqui, js)] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
                print(r.stdout.strip())
                if r.returncode:
                    print(r.stderr.strip()[-1500:])      # ex.: o playwright-core que falta (ver o cabeçalho do .mjs)
                    raise SystemExit("⛔ corrija antes do render (%s)" % js)
