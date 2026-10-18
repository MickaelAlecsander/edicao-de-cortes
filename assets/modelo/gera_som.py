# -*- coding: utf-8 -*-
"""Escreve o som.json (a folha de deixas do sonoplastia.py) nas MESMAS palavras das cenas: cada deixa diz (palavra,
bloco, n, deslocamento), igual ao T() do _cenas.js, e vai para a folha como ["palavra", desde, deslocamento]. O par de som
de cada TELA CHEIA (sobe: whoosh + página; desce: whoosh) sai sozinho do assets/tela_cheia.json do montar.py.

    python montar.py && python gera_som.py && python <skill>/scripts/sonoplastia.py .

Regras (references/audio.md): o som cai no quadro do movimento (contato do carimbo = t + 0,01; o meio do entra()); o
efeito fica sempre por baixo da fala; muito efeito pode, alto não; nada de impacto grave no último segundo.
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
tempos = json.load(open("assets/tempos.json", encoding="utf-8"))
norm = lambda w: re.sub(r"^,+|,+$", "", re.sub(r"[^a-zà-ú0-9%,]", "", w.lower()))
B = {b["id"]: b for b in tempos["blocos"]}


def T(w, bloco, n=1):
    ach = [p["s"] for p in B[bloco]["palavras"] if norm(p["w"]) == norm(w)]
    assert len(ach) >= n, f"palavra não encontrada: {w!r} (n={n}) no bloco {bloco!r}"
    return ach[n - 1]


D = []


def d(nota, w, bloco, desl, som, camada, pan=0.0, db=None, n=1, **extra):
    """deixa na palavra w (n-ésima do bloco) + desl; w=None: início do bloco + desl; bloco=None: desl é o tempo absoluto"""
    if bloco is None:
        t = round(desl, 3)
    elif w is None:
        t = round(B[bloco]["inicio"] + desl, 3)
    else:
        t = [w, round(T(w, bloco, n) - 0.05, 3), desl]
    x = {"nota": nota, "t": t, "som": som, "camada": camada, "pan": pan}
    if db is not None:
        x["db"] = db
    x.update(extra)
    D.append(x)


GA, EU = "gancho", "eua"
CARIMBO = 0.01   # o carimba(el, T − 0,05) bate no papel ~0,06 s depois

# ── as deixas do _cenas_exemplo.js (troque pelas do seu _cenas.js) ─────────────────────────────────────────────────────
d("O DISCURSO DE SEMPRE", None, GA, 0.1, "pousa", "miudo", 0.0, -5)
d("o jovem", None, GA, 0.15, "pousa", "miudo", -0.2, -5)
d("o despertador", "acordar", GA, -0.2, "surge", "miudo", -0.6, -4)
d("o despertador toca", "5", GA, -0.1, "tique", "textura", -0.6, -2, rep=6, passo=0.09)
d("5:00", "5", GA, -0.1, "pop", "miudo", -0.6, -4)
d("o pulo", "acordar", GA, 0.1, "pulo", "acao", 0.0, -6)
d("TRABALHA DURO", "trabalhar", GA, -0.15, "pousa", "miudo", 0.5, -4)
d("o saco de dinheiro", "conseguir", GA, -0.2, "saco_moedas", "acao", 0.5, -6)
d("o saco foge", "enriquecer", GA, 0.2, "whoosh", "transicao", 0.5, -8, pan_ate=0.9)
d("a pizza VERDADE", "Isso", GA, 0.0, "pousa", "acao", 0.3, -5)
d("carimbo MEIA VERDADE", "meia", GA, CARIMBO, "carimbo", "destaque", 0.3)
d("X nem meia", "nem", GA, 0.0, "bip_erro", "miudo", 0.4, -5)
d("UM PEDACINHO", "pedacinho", GA, -0.05, "corte", "acao", 0.3, -3)
d("cartão NASCIMENTO", "nascimento", GA, -0.3, "pousa", "miudo", -0.5, -4)
d("a coroa", "nascimento", GA, 0.0, "brilho", "miudo", -0.5, -4)
d("cartão CRIME", "crimes", GA, -0.3, "pousa", "miudo", 0.5, -4)
d("cartão TRABALHO", "trabalho", GA, -0.3, "pousa", "miudo", -0.5, -4)
d("cartão DE TODO TIPO", "todo", GA, -0.3, "pergunta", "miudo", 0.5, -3)
d("BRASIL x MUNDO", "Brasil", EU, -0.15, "pousa", "miudo", 0.0, -5)
d("o globo", "comparação", EU, -0.2, "globo", "acao", -0.5, -6)
d("a bandeira dos EUA", "Estados", EU, -0.2, "tecido", "miudo", 0.0, -5)
d("a barra cresce", "71%", EU, -0.15, "desliza", "acao", 0.2, -5)
d("71%", "71%", EU, 0.3, "pop", "miudo", 0.4, -4)
d("as cédulas voam", "construíram", EU, 0.0, "moedas", "acao", 0.3, -6)

# ── o par de cada TELA CHEIA, nas janelas que o montar.py gravou ([t0 − 0,5, t1 + 0,47]) ──────────────────────────────
for i, (a, b) in enumerate(json.load(open("assets/tela_cheia.json")), 1):
    d(f"TELA CHEIA {i} sobe", None, None, a, "whoosh", "transicao", 0.0, 1)
    d(None, None, None, a + 0.1, "pagina", "transicao", 0.0, -1)
    d(f"TELA CHEIA {i} desce", None, None, b - 0.47, "whoosh", "transicao", 0.0, 0)

for x in D:
    if x["nota"] is None:
        del x["nota"]
json.dump({"nota": "Folha de deixas gerada pelo gera_som.py, nas mesmas palavras do _cenas.js; cada TELA CHEIA tem o par de "
                   "transição (sobe: whoosh + página; desce: whoosh), por baixo da fala.",
           "deixas": D}, open("som.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(D), "deixas")
