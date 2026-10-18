# -*- coding: utf-8 -*-
"""As batidas da fala, para o roteiro da animação cena a cena (10/10/2026). O método está em
references/animacao-hyperframes.md, seção 10.

    python <skill>/scripts/roteirista.py batidas cortes/<slug>
        → batidas.md: cada frase com tempo e duração, os gatilhos (números, nomes, palavras fortes) já com a âncora
          T("palavra", "bloco", n) certa (o n conta DENTRO do bloco, como o W() do motor), e as alusões (cargo ou pronome
          que aponta para alguém sem o nome: a pessoa aparece ilustrada, antes se o nome só vem depois).

"""
import html
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
STOP = set("""a o e é de do da dos das em no na nos nas um uma uns umas que se por pra para com sem ao à as os eu você ele
ela eles elas a gente isso isto aquilo esse essa este esta aqui ali lá aí né tá tô não sim mas ou então porque pois
como quando onde já também muito mais menos bem só até cara tipo assim coisa vai vou foi ser ter tem têm está estão
era fazer faz fez meu minha seu sua nosso nossa lhe me te nos vocês tudo todo toda todos todas cada qual quem""".split())
# alusão a alguém sem o nome: o cargo sempre; o pronome, uma vez por frase (Mickael, 10/10/2026: "mesmo que a fala seja
# meio que subentendido… é bom que a pessoa apareça… a imagem da pessoa traz a imersão")
CARGOS = {"presidente", "candidato", "candidata", "ministro", "ministra", "deputado", "deputada", "senador", "senadora",
          "governador", "governadora", "prefeito", "prefeita", "patrão", "empresário", "empresária", "juiz", "juíza"}
PRONOMES = {"ele", "ela", "eles", "elas", "cara"}
FECHO_FALSO = ["olha que loucura", "esse é o cenário", "acabou", "é isso", "falta agora", "que papo de doido", "simples assim"]


def norm(s):
    s = re.sub(r"[^a-zà-ú0-9%,]", "", s.lower())
    return re.sub(r"^,+|,+$", "", s)


def carrega(pasta):
    p = os.path.join(pasta, "assets", "dados.js")
    js = open(p, encoding="utf-8").read()
    return json.loads(js[js.index("=") + 1:].strip().rstrip(";"))


def ancora(D, w, bloco, n=1):
    """o instante em que a n-ésima ocorrência da palavra é dita DENTRO do bloco (o W() do motor)"""
    k = 0
    for p in D["palavras"]:
        if p.get("bloco") != bloco:
            continue
        if norm(p["w"]) == norm(w):
            k += 1
            if k == n:
                return p["s"]
    raise SystemExit("✗ âncora não encontrada: %s | %s | %d" % (w, bloco, n))


def tempo(D, a):
    if isinstance(a, (int, float)):
        return float(a)
    partes = a.split("|")
    return ancora(D, partes[0], partes[1], int(partes[2]) if len(partes) > 2 else 1)


def frases(D):
    """frases pela pontuação, pela troca de bloco ou por pausa de 0,45 s"""
    out, cur = [], []
    ps = D["palavras"]
    for i, p in enumerate(ps):
        cur.append(p)
        prox = ps[i + 1] if i + 1 < len(ps) else None
        fim = p["w"].rstrip().endswith((".", "?", "!")) or prox is None or prox.get("bloco") != p.get("bloco") or prox["s"] - p["e"] > 0.45
        if fim:
            out.append(cur)
            cur = []
    return out


def gatilhos(D, fr):
    """números, dinheiro, %, nomes próprios e palavras fortes da frase, com a âncora certa"""
    conta = {}
    for p in D["palavras"]:
        conta.setdefault(p["bloco"], []).append(p)
    out = []
    for j, p in enumerate(fr):
        w = norm(p["w"])
        if not w:
            continue
        b = p["bloco"]
        n = sum(1 for q in conta[b] if q["s"] <= p["s"] + 1e-6 and norm(q["w"]) == w)
        bruto = p["w"].strip(",.?!:;\"'")
        if re.search(r"\d", w) or "r$" in p["w"].lower():
            tipo = "número"
        elif bruto[:1].isupper() and j > 0 and bruto.lower() not in STOP:
            tipo = "nome"
        elif len(w) >= 6 and w not in STOP:
            tipo = "forte"
        else:
            continue
        out.append(dict(w=bruto, tipo=tipo, s=p["s"], ancora='T("%s", "%s"%s)' % (bruto, b, ", %d" % n if n > 1 else "")))
    return out


def alusoes(D, fr):
    """cargos e pronomes que apontam para alguém (sem o nome): pedem a pessoa ilustrada, antes se o nome vem depois"""
    conta, out, pron = {}, [], False
    for p in D["palavras"]:
        conta.setdefault(p["bloco"], []).append(p)
    for p in fr:
        w = norm(p["w"]).strip(",")
        if w in CARGOS or (w in PRONOMES and not pron):
            pron = pron or w in PRONOMES
            b = p["bloco"]
            n = sum(1 for q in conta[b] if q["s"] <= p["s"] + 1e-6 and norm(q["w"]).strip(",") == w)
            out.append('%s `T("%s", "%s"%s)`' % (p["w"].strip(",.?!"), p["w"].strip(",.?!"), b, ", %d" % n if n > 1 else ""))
    return out


def cmd_batidas(pasta):
    D = carrega(pasta)
    linhas = ["# Batidas · %s" % os.path.basename(os.path.abspath(pasta)), "",
              "Gerado por `scripts/roteirista.py batidas`. Cada frase com o tempo na montagem e os gatilhos que pedem imagem",
              "(número vira objeto; nome vira TIPO com etiqueta; palavra forte vira ação). A âncora já vem com o n certo.", "",
              "Alusão: cargo ou pronome que aponta para alguém sem dizer o nome. Se for uma pessoa concreta, ela aparece ilustrada",
              "(TIPO com etiqueta), antes da fala se o nome só vem depois (regra de 10/10/2026).", "",
              "| tempo | dur | bloco | frase | gatilhos | alusão |", "|---|---|---|---|---|---|"]
    avisos = []
    for fr in frases(D):
        t0, t1 = fr[0]["s"], fr[-1]["e"]
        txt = " ".join(p["w"] for p in fr)
        g = gatilhos(D, fr)
        gt = "<br>".join("**%s** %s `%s`" % (x["tipo"], x["w"], x["ancora"]) for x in g if x["tipo"] != "forte") + \
            ("<br>" if any(x["tipo"] != "forte" for x in g) and any(x["tipo"] == "forte" for x in g) else "") + \
            ", ".join("%s `%s`" % (x["w"], x["ancora"]) for x in g if x["tipo"] == "forte")
        linhas.append("| %.2f | %.1f | %s | %s | %s | %s |" % (t0, t1 - t0, fr[0]["bloco"], html.escape(txt), gt, ", ".join(alusoes(D, fr))))
        if t1 - t0 > 6:
            avisos.append("frase longa (%.1f s) em %.1f s: pede 2 ou mais batidas visuais (\"%s…\")" % (t1 - t0, t0, txt[:50]))
        low = txt.lower()
        for f in FECHO_FALSO:
            if f in low and t1 < D["duracao"] - 8:
                avisos.append("cara de fim no meio em %.1f s (\"%s\"): o placar mostrou que isso derruba até 20%%" % (t0, f))
    if avisos:
        linhas += ["", "## Avisos", ""] + ["- " + a for a in avisos]
    open(os.path.join(pasta, "batidas.md"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("\n".join(linhas))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "batidas":
        sys.exit("uso: python ferramentas/roteirista.py batidas cortes/<slug>")
    sys.exit(cmd_batidas(sys.argv[2]) or 0)
