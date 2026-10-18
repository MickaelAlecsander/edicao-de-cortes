# -*- coding: utf-8 -*-
"""Legenda .vtt (ou .srt) → texto corrido em blocos de ~15 s, com o tempo do começo de cada bloco.

    python vtt2txt.py <arquivo.vtt> > saida.txt

Serve para ler as candidatas SÓ pelo texto, antes de baixar vídeo. A legenda automática do YouTube repete a linha
anterior em cada deixa (a linha velha em cima, a nova embaixo, e uma deixa de 10 ms entre elas); aqui fica só a linha nova.

O tempo é o da legenda automática: serve para ACHAR o trecho, nunca para cortar (a ponta sai do envelope e do MMS_FA).

Copiado de cortes_raul/ferramentas/vtt2txt.py. Mudou: aceita deixa sem a hora (a legenda do TikTok vem "00:01.234"),
.srt, CRLF e entidades (&amp;, &gt;&gt;), e acima de 1 h o rótulo vira H:MM:SS, no mesmo formato em que se pedem os
trechos ("1:25:00-1:31:30").
"""
import html
import re
import sys

TEMPO = re.compile(r"(?:(\d+):)?(\d+):(\d+)[.,]\d+ -->")


def rotulo(t):
    return "%d:%02d:%02d" % (t // 3600, t // 60 % 60, t % 60) if t >= 3600 else "%02d:%02d" % (t // 60, t % 60)


def parse(path, bloco=15):
    txt = open(path, encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
    out, seen = [], ""
    for b in txt.split("\n\n"):
        m = TEMPO.search(b)
        if not m:
            continue
        t = int(m[1] or 0) * 3600 + int(m[2]) * 60 + int(m[3])
        ls = b.split("\n")
        i = next(k for k, l in enumerate(ls) if "-->" in l)
        linhas = [html.unescape(re.sub(r"<[^>]+>", "", l)).strip() for l in ls[i + 1:]]
        linhas = [l for l in linhas if l]
        if not linhas:
            continue
        last = linhas[-1]
        if last == seen:
            continue
        seen = last
        out.append((t, last))
    # o bloco fecha ANTES da linha que passaria dos 15 s (o original fechava depois, e a linha de um minuto adiante
    # entrava com o rótulo do bloco anterior)
    res, cur, start = [], [], None
    for t, l in out:
        if start is not None and t - start >= bloco:
            res.append("[%s] %s" % (rotulo(start), " ".join(cur)))
            cur, start = [], None
        if start is None:
            start = t
        cur.append(l)
    if cur:
        res.append("[%s] %s" % (rotulo(start), " ".join(cur)))
    return "\n".join(res)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__ or "uso: python vtt2txt.py <legenda.vtt|.srt>")
    sys.stdout.reconfigure(encoding="utf-8")
    print(parse(sys.argv[1]))
