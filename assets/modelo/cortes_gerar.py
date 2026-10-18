# -*- coding: utf-8 -*-
"""MODELO do cortes_gerar.py de cada corte (vem com assets/modelo/): escreve o cortes.json que o cortar.py lê.

    python cortes_gerar.py && python $S/cortar.py . && python pos_cortar.py && python $S/legendas.py .

Preencher depois do roteiro aprovado (references/corte-e-fala.md tem as regras e o porquê de cada uma):
  · FONTE: o <id>_opus.mkv (vídeo + a melhor faixa de áudio, com o atraso já aplicado; ver pesquisa-e-download.md);
  · PAL: as palavras da transcrição local no tempo do .mkv (o transcrever_local.py roda no mesmo arquivo que se corta);
  · cada bloco: (id, janela do início, janela do fim, recorte, extras). A janela é o VALE de silêncio que o pausas.py
    marcou com ✓ ([início, fim] do vale, em segundos da fonte); o cortar.py corta no ponto mais quieto dela;
  · recorte [x, w, y] na fonte de 1920×1080 para a janela de 1080×960 (w × 960/1080 de altura): o plano aberto com o
    Raul inteiro e sem zoom; na tela dividida, o painel dele preenchendo a janela;
  · extras: "trocas" [[t, recorte], ...] no pts EXATO do 1º quadro novo (scripts/trocas.py); "fala_ok" {"ini"/"fim":
    motivo medido no envelope} só quando a trava barrar e o envelope provar que está certo; "respiro": s contra a emenda
    seca (pausa de menos de ~200 ms); "fade_fim": s.
Exemplo abaixo: dois blocos do C84 (17/10/2026), um no plano aberto e um com troca para a tela dividida.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
FONTE, PAL = "../../_fontes/<id>_opus.mkv", "../../_pesquisa/<id>_palavras_mkv.json"
JW, JH = 1080, 960
F = [353, 1215, 0]   # plano aberto: o Raul inteiro, x 353–1568 (medir na folha de contato de cada fonte)
S = [1186, 734, 0]   # tela dividida: o painel do Raul de 1186 a 1920, preenchendo a janela (zoom ok, nunca laterais desfocadas)
B = [
    # ("id", [vale do início], [vale do fim], recorte, {extras})
    ("gancho", [6.215, 6.235], [27.720, 27.790], F, {}),
    ("top", [468.040, 468.430], [488.580, 488.795], S, {"trocas": [[479.333, F]]}),
    # ("lemann2", [564.675, 564.740], [575.140, 575.220], F, {"respiro": 0.15, "fala_ok": {"ini": "a voz antes do corte é o fim de 'Saverin.'; vale de −62 dB"}}),
]
blocos = [{"id": bid, "ini": ini, "fim": fim, "x": x, **extra} for bid, ini, fim, x, extra in B]
DESTAQUES = []   # palavras que a legenda pinta de VERMELHO (números, nomes, o soco de cada frase); o marca-texto amarelo vai em toda palavra dita
cfg = {"fonte": FONTE, "palavras": PAL, "janela": [JW, JH], "correcoes": {}, "destaques": DESTAQUES,
       "recorte": {"w": 1215, "y": 0}, "blocos": blocos}
json.dump(cfg, open("cortes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(blocos), "blocos, %.1f s" % sum(b["fim"][0] - b["ini"][1] for b in blocos))
