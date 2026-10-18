# -*- coding: utf-8 -*-
"""Gera `assets/dados.js` (palavras + legenda em blocos curtos) a partir do `assets/tempos.json`.

    python legendas.py cortes/<slug>      (ou `.` de dentro da pasta do corte)

Regra da legenda: 1 a 3 palavras, SEMPRE em linha única. O bloco fecha na pontuação,
nunca termina em palavra fraca ("de", "o", "e"...), e o número fica junto da palavra que o diz.
O tempo sai das palavras faladas: entra 0,04 s antes da primeira e fica até a próxima entrar
(ou 0,35 s depois da última, se houver pausa).

Correções de escrita (o que o Raul pronuncia diferente) vêm de `cortes.json` → "correcoes".

Legenda v2 (06/10/2026, C27): palavrão sai censurado (FODA → F**A, regra do dono do canal: "pra não sofrer restrição"),
cada bloco diz QUEM fala (`assets/quem_fala.json`, quando existe) e as palavras de destaque (número, dinheiro e as de
`cortes.json` → "destaques") vão marcadas para a legenda as pintar de vermelho. Só a legenda é censurada: `palavras`
fica crua para o W() das cenas e o sfx.py.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
MAX_PALAVRAS = 3
MAX_CHARS = 15
FRACAS = {"o", "a", "os", "as", "de", "da", "do", "das", "dos", "no", "na", "nos", "nas", "e", "em",
          "um", "uma", "por", "pra", "para", "que", "se", "com", "ao", "à", "mais"}
PALAVROES = {"foda", "fodas", "foder", "fodeu", "fodido", "fodida", "fodendo", "fodase", "fode", "fodem", "fudido", "fudida",
             "fuder", "fudeu", "porra", "porras", "porrada",
             "merda", "merdas", "caralho", "caralhos", "caralha", "puta", "putas", "puto", "putos", "putaria", "bosta",
             "cacete", "buceta", "cu", "cuzão", "arrombado", "arrombada", "fdp", "pqp", "vsf"}
DINHEIRO = {"mil", "milhão", "milhões", "bilhão", "bilhões", "trilhão", "trilhões", "r$", "reais", "pau"}
UNIDADES = DINHEIRO | {"anos", "ano", "meses", "dias", "cadeiras", "vezes", "pessoas"}


def censura(w):
    """FODA. → F**A. (1ª e última letra, a pontuação fica)."""
    m = re.match(r"^(\W*)(.+?)(\W*)$", w)
    a, n, z = m.groups()
    if "-" in n:                     # "foda-se" → "F**A-SE" (C44: o hífen escondia o palavrão)
        return a + "-".join(censura(p) for p in n.split("-")) + z
    if n.lower() not in PALAVROES:
        return w
    return a + (n[0] + "*" * (len(n) - 1) if len(n) < 3 else n[0] + "*" * (len(n) - 2) + n[-1]) + z


def quem_fala(pasta):
    p = os.path.join(pasta, "assets", "quem_fala.json")
    # trecho curto por cima da fala do outro ("Tem mérito?" de 0,25 s) não decide quem fala. Quando o tempo das palavras
    # e o da diarização não batem, o pos_cortar.py do corte marca "quem" na palavra, e isso vale (C29)
    segs = [x for x in json.load(open(p, encoding="utf-8")) if x["e"] - x["s"] >= 0.4] if os.path.exists(p) else []
    def quem(s, e):
        best, ov = "raul", 0.0
        m = (s + e) / 2              # palavra de duração zero do Whisper ("para" 17,19–17,19 no C29) não sobrepõe nada
        s, e = min(s, m - 0.05), max(e, m + 0.05)
        for x in segs:
            o = min(e, x["e"]) - max(s, x["s"])
            if o > ov:
                # só "apresentador" é a outra voz: o diarize às vezes dá ao Raul um rótulo solto ("A", "B") no meio da fala
                best, ov = ("apresentador" if x["quem"] == "apresentador" else "raul"), o
        return best
    return quem


def juntar_numeros(ws):
    """O Whisper quebra "6,5%" em "6" + ",5%" e "J.P." em "J" + ".P.": junta de volta."""
    out = []
    for w in ws:
        if out and re.match(r"^[,.][0-9A-Za-z]", w["w"]):
            out[-1] = dict(out[-1], w=out[-1]["w"] + w["w"], e=w["e"])
        else:
            out.append(dict(w))
    return out


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    pasta = os.path.abspath(sys.argv[1])
    tempos = json.load(open(os.path.join(pasta, "assets", "tempos.json"), encoding="utf-8"))
    cfg = json.load(open(os.path.join(pasta, "cortes.json"), encoding="utf-8"))
    corr = cfg.get("correcoes", {})
    destaques = {d.lower() for d in cfg.get("destaques", [])}
    quem = quem_fala(pasta)

    palavras = []
    for b in tempos["blocos"]:
        for w in juntar_numeros(b["palavras"]):
            txt = corr.get(w["w"].strip(" ,.?!…"), w["w"].strip(" ,.?!…"))
            if not txt:
                continue
            palavras.append({"w": txt, "s": w["s"], "e": w["e"], "bloco": b["id"], "quem": w.get("quem") or quem(w["s"], w["e"]),
                             "pausa": bool(re.search(r"[,.?!…]$", w["w"]))})

    # blocos de legenda
    grupos, cur = [], []
    for i, p in enumerate(palavras):
        cur.append(p)
        prox = palavras[i + 1] if i + 1 < len(palavras) else None
        chars = len(" ".join(x["w"] for x in cur))
        fecha = (p["pausa"] or len(cur) >= MAX_PALAVRAS or prox is None or prox["bloco"] != p["bloco"]
                 or chars + 1 + len(prox["w"]) > MAX_CHARS or prox["s"] - p["e"] > 0.35 or prox["quem"] != p["quem"])
        # palavra fraca não fecha bloco, e o número leva junto a palavra que o anuncia ("cai 6,5%")
        puxa = prox is not None and prox["bloco"] == p["bloco"] and len(cur) > 1 and not p["pausa"] and (
            p["w"].lower() in FRACAS or (re.search(r"\d", prox["w"]) and not re.search(r"\d", p["w"]))
            or (re.search(r"\d", p["w"]) and prox["w"].lower() in UNIDADES)) and prox["quem"] == p["quem"]
        if fecha and puxa:
            cur.pop()                                   # ela abre o próximo bloco
            grupos.append(cur)
            cur = [p]
            continue
        if fecha:
            grupos.append(cur)
            cur = []
    if cur:
        grupos.append(cur)

    leg = []
    for i, g in enumerate(grupos):
        ini = max(0.02, g[0]["s"] - 0.04)   # em 0,00 exato a etiqueta não aparece (o set de esconder ganha do fromTo no mesmo instante)
        if i == 0:   # a legenda do gancho entra no 1º quadro: a transcrição costuma atrasar a 1ª palavra (C68, 12/10: 0,25 s sem legenda)
            ini = 0.02
        fim = g[-1]["e"] + 0.35
        if i + 1 < len(grupos):
            fim = min(fim, grupos[i + 1][0]["s"] - 0.04)
        fim = min(max(fim, g[-1]["e"]), tempos["duracao"])
        if i + 1 < len(grupos):   # nunca duas etiquetas na tela: a próxima entra, esta sai
            fim = min(fim, max(0.0, grupos[i + 1][0]["s"] - 0.04))
        def forte(w):
            n = w.lower().strip(" ,.?!…")
            return bool(re.search(r"\d", n)) or n in DINHEIRO or n in destaques or n in PALAVROES
        leg.append({"ini": round(ini, 3), "fim": round(fim, 3), "quem": g[0]["quem"],
                    "palavras": [{"w": censura(x["w"].upper()), "s": x["s"], "e": x["e"], "forte": forte(x["w"])} for x in g]})

    dados = {"duracao": tempos["duracao"],
             "blocos": [{"id": b["id"], "inicio": b["inicio"], "dur": b["dur"]} for b in tempos["blocos"]],
             "palavras": palavras, "legenda": leg}
    with open(os.path.join(pasta, "assets", "dados.js"), "w", encoding="utf-8") as f:
        f.write("// gerado por legendas.py; não editar à mão\nwindow.DADOS = ")
        json.dump(dados, f, ensure_ascii=False)
        f.write(";\n")
    for c in leg:
        print("%6.2f-%6.2f %s %s" % (c["ini"], c["fim"], "A" if c["quem"] != "raul" else " ",
                                     " ".join(x["w"] + ("!" if x["forte"] else "") for x in c["palavras"])))
    print("%d blocos de legenda, maior com %d caracteres"
          % (len(leg), max(len(" ".join(x["w"] for x in c["palavras"])) for c in leg)))


assert censura("FODA.") == "F**A." and censura("porra,") == "p***a," and censura("CARALHO") == "C*****O" and censura("CU") == "C*"
assert censura("MINISTRO") == "MINISTRO" and censura("COMPUTADOR") == "COMPUTADOR"

if __name__ == "__main__":
    main()

