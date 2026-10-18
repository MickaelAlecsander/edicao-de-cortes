# -*- coding: utf-8 -*-
"""Nota de viralização (0 a 10) de cada corte candidato. Sem API: só soma, confere a faixa de cada item e guarda.

A régua (itens, pesos, descontos) está em references/ranqueamento.md desta skill; as correções do dono do canal ficam
no REGUA.md do projeto e valem mais que a tabela. Os itens são dados LENDO o corte inteiro: contar palavra-chave não mede
o trecho (no canal de futebol, a régua por palavras deu 85 a uma leitura de anúncio).

    python nota_viral.py                                   # soma o radar.json, ordena e escreve o RADAR.md
    python nota_viral.py corrigir <id> <nota> "motivo"     # correção do dono do canal (no candidato e no REGUA.md)
    python nota_viral.py usar <id> <Cxx>                   # o candidato virou o corte Cxx: a nota vai para a ficha

Caminhos relativos à --raiz (padrão: a pasta atual): _pesquisa/radar.json, _pesquisa/fichas.json, RADAR.md, REGUA.md.
"""
import argparse
import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
# ponytail: os pesos ficam aqui e na tabela do ranqueamento.md; mudou um, mude o outro (o placar decide quando mudar)
MAX = {"gancho": 1.5, "segura": 2.5, "tema": 2, "formato": 1.5, "prova": 1.5, "fecho": 1}
DESCONTO = {"datado": 2, "repete": 1.5, "fonte_alheia": 2, "propaganda": 1}
COMO = ("Um candidato por corte possível (régua em references/ranqueamento.md da skill edicao-de-cortes). criterios: "
        "gancho 0–1,5, segura 0–2,5, tema 0–2, formato 0–1,5, prova 0–1,5, fecho 0–1; descontos (true/false): datado, "
        "repete, fonte_alheia, propaganda. 'nota_viral.py' soma e escreve o RADAR.md; 'usar <id> <Cxx>' leva a nota para "
        "a ficha; 'corrigir <id> <nota> \"motivo\"' guarda a correção do dono do canal.")


def nota(c):
    k = c["criterios"]
    for item, mx in MAX.items():
        if not 0 <= k.get(item, 0) <= mx:
            raise SystemExit("✗ %s: %s = %s fora de 0–%g" % (c["id"], item, k[item], mx))
    n = sum(k.get(i, 0) for i in MAX) - sum(v for i, v in DESCONTO.items() if k.get(i))
    return round(max(0.0, min(10.0, n)), 1)


def decisao(n):
    return "produzir" if n >= 7 else "só se não houver melhor" if n >= 5 else "não produzir"


def acha(R, cid):
    c = next((x for x in R["candidatos"] if x["id"] == cid), None)
    if not c:
        raise SystemExit("✗ candidato %r não está no radar (ids: %s)" % (cid, ", ".join(x["id"] for x in R["candidatos"])))
    return c


def le_json(p, vazio):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else vazio


def grava_json(p, obj):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    json.dump(obj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def radar_md(R, saida, radar):
    cs = sorted(R["candidatos"], key=lambda c: -nota(c))
    out = ["# Radar de cortes", "",
           "Gerado por `nota_viral.py` em %s a partir de `%s` (não editar à mão). A régua está no `ranqueamento.md` da"
           " skill; as correções do dono do canal, no `REGUA.md`." % (datetime.now().strftime("%d/%m %H:%M"), radar), "",
           "| # | nota | decisão | corte candidato | vídeo | dur | gancho · segura · tema · formato · prova · fecho | descontos | correção | virou |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(cs, 1):
        k, m = c["criterios"], c.get("correcao") or {}
        out.append("| %d | **%.1f** | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, nota(c), decisao(nota(c)), c["titulo"], c.get("video", "–"), c.get("dur", "–"),
            " · ".join("%g" % k.get(x, 0) for x in MAX), ", ".join(x for x in DESCONTO if k.get(x)) or "–",
            "%g (%s)" % (m["nota"], m["motivo"]) if m else "–", c.get("corte") or "–"))
    out += ["", "## Por que cada nota", ""]
    out += ["- **%s (%.1f):** %s" % (c["titulo"], nota(c), c.get("por_que", "")) for c in cs]
    open(saida, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return cs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", nargs="?", default="somar", choices=["somar", "corrigir", "usar"])
    ap.add_argument("args", nargs="*", help="corrigir: <id> <nota> \"motivo\" · usar: <id> <Cxx>")
    ap.add_argument("--raiz", default=".", help="pasta do projeto (padrão: a atual)")
    ap.add_argument("--radar", help="padrão: <raiz>/_pesquisa/radar.json")
    ap.add_argument("--fichas", help="padrão: <raiz>/_pesquisa/fichas.json")
    ap.add_argument("--saida", help="padrão: <raiz>/RADAR.md")
    ap.add_argument("--regua", help="padrão: <raiz>/REGUA.md (onde as correções se acumulam)")
    a = ap.parse_args()
    radar = a.radar or os.path.join(a.raiz, "_pesquisa", "radar.json")
    fichas = a.fichas or os.path.join(a.raiz, "_pesquisa", "fichas.json")
    saida = a.saida or os.path.join(a.raiz, "RADAR.md")
    regua = a.regua or os.path.join(a.raiz, "REGUA.md")
    precisa = {"somar": 0, "corrigir": 3, "usar": 2}[a.acao]
    if len(a.args) != precisa:
        ap.error("%s pede %d argumento(s)" % (a.acao, precisa))

    if not os.path.exists(radar):
        grava_json(radar, {"_como": COMO, "candidatos": []})
        print("radar vazio criado em %s: acrescente os candidatos (formato no ranqueamento.md) e rode de novo" % radar)
        return
    R = json.load(open(radar, encoding="utf-8"))

    if a.acao == "corrigir":
        cid, n, motivo = a.args
        c = acha(R, cid)
        antes = nota(c)
        c["correcao"] = {"nota": float(n.replace(",", ".")), "motivo": motivo, "data": datetime.now().strftime("%d/%m/%Y")}
        novo = not os.path.exists(regua)
        with open(regua, "a", encoding="utf-8") as f:
            if novo:
                f.write("# Régua de viralização: correções do dono do canal\n\nLer antes de dar nota: cada correção vale"
                        " mais que a tabela do ranqueamento.md.\n\n")
            f.write("- **%s, %s** (nota %.1f → %s): %s\n" % (c["correcao"]["data"], c["titulo"], antes, n, motivo))
    elif a.acao == "usar":
        cid, corte = a.args
        c = acha(R, cid)
        c["corte"] = corte
        F = le_json(fichas, {"_como": "Uma ficha por corte, preenchida ao propor o tema (antes do roteiro)."})
        F.setdefault(corte, {}).update({"nota": nota(c), "nota_criterios": c["criterios"], "radar": c["id"]})
        grava_json(fichas, F)

    grava_json(radar, R)
    for i, c in enumerate(radar_md(R, saida, os.path.relpath(radar, a.raiz).replace(os.sep, "/")), 1):
        print("%2d. %4.1f  %-24s %s" % (i, nota(c), decisao(nota(c)), c["titulo"]))
    print("→ %s" % saida)


if __name__ == "__main__":
    main()
