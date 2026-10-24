# -*- coding: utf-8 -*-
"""A marca do canal em todo vídeo (07/10/2026): a foto de perfil e o @ do canal, sutis e parados à esquerda, na metade
do Raul, para quem repostar o corte levar o nome junto.

    from marca import aplicar      # no montar.py do corte: html = aplicar(html, pasta_do_corte)

A foto vem de assets/modelo/marca/avatar_128.jpg desta skill (a original, avatar_tiktok.jpg, fica ao lado; se a foto de
perfil mudar, troque as duas) e vai para assets/marca.jpg do corte. A marca fica parada, sem animação, em left 30 e
top divisória + 116 (1076 no 50/50): logo abaixo da etiqueta da legenda, longe do texto do post do TikTok (embaixo à
esquerda) e dos botões (à direita), com opacidade 0,8. A capa não leva a marca. Na tela cheia ela some (o telaCheia() do
_base.js apaga o #marca e devolve a 0,8 depois).
"""
import os
import re
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTO = os.path.join(RAIZ, "assets", "modelo", "marca", "avatar_128.jpg")
CONTA = "@cortesdoraulsena"
CSS = """
      /* marca do canal (scripts/marca.py): o @ e a foto de perfil, parados, sutis */
      #marca { position: absolute; left: 115px; top: __TOPO__px; display: flex; align-items: center; gap: 12px; opacity: 0.8;
        pointer-events: none; z-index: 30; }
      #marca img { width: 56px; height: 56px; border-radius: 50%; border: 3px solid rgba(248, 242, 228, 0.92); object-fit: cover;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35); }
      #marca span { font-family: "Archivo Black", sans-serif; font-size: 25px; color: #f8f2e4; letter-spacing: 0.01em;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.65), 0 0 2px rgba(0, 0, 0, 0.5); }
"""


def aplicar(html, pasta, divisoria=960):
    """Põe a marca no index.html (idempotente) e copia a foto para <pasta>/assets/marca.jpg."""
    assert os.path.exists(FOTO), "marca: falta a foto em " + FOTO
    shutil.copyfile(FOTO, os.path.join(pasta, "assets", "marca.jpg"))
    if 'id="marca"' in html:
        return html
    html = html.replace("</style>", CSS.replace("__TOPO__", str(divisoria + 116)) + "    </style>", 1)
    m = re.search(r'<div id="leg"[^>]*></div>', html)
    assert m, "marca: não achei o #leg"
    el = f'\n      <div id="marca"><img src="assets/marca.jpg" alt="" /><span>{CONTA}</span></div>'
    return html[:m.end()] + el + html[m.end():]
