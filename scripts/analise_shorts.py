# -*- coding: utf-8 -*-
"""Análise de shorts: o que, dentro do vídeo, puxou comentário (mapa de calor por frase).

    python $S/analise_shorts.py <id ou url> ...      # baixa metadados, legenda e comentários e analisa
    python $S/analise_shorts.py --cache [<id> ...]    # refaz só a análise com o que já está baixado (sem ids: todos)

Por quê: views e likes dizem QUE o short pegou; os comentários dizem O QUÊ pegou. Cada comentário é ligado à frase do
vídeo que ele cita ou à qual reage (palavras em comum sem acento, pesadas pela raridade delas na transcrição, e números),
e cada frase soma 1 + likes de cada comentário ligado a ela. As frases mais quentes são candidatas a gancho e a fecho.
As respostas contam à parte: thread com muita resposta é discussão ou briga (contagem parcial: o yt-dlp traz no máximo
30 respostas por short, `max_comments=300,all,30`, e elas caem nas primeiras threads).

Limite: a ligação é por palavra. Ironia, emoji e comentário sobre o Raul (e não sobre a fala) ficam em "geral". A leitura
dos comentários é o juiz; o mapa só aponta onde olhar (a mesma lição da REGUA.md: contar palavra não mede o trecho).

Grava `_pesquisa/shorts_analise/bruto/` (info enxuta + legenda original pt.*-orig), `_pesquisa/shorts_analise/<id>.json` (métricas,
frases com peso, comentários com a frase ligada) e `_pesquisa/shorts_analise/relatorio.md`.
"""
import html
import json
import math
import os
import re
import subprocess
import sys
import time
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = os.environ.get("CORTES_RAIZ", os.getcwd())   # a raiz do projeto (rodar de lá ou definir CORTES_RAIZ)
PASTA = os.path.join(RAIZ, "_pesquisa", "shorts_analise")
BRUTO = os.path.join(PASTA, "bruto")
LIMIAR = 4.0      # soma mínima de raridade das palavras em comum (e no mínimo 2 delas) para ligar o comentário a uma frase
CAMPOS = ["id", "title", "upload_date", "duration", "view_count", "like_count", "channel", "comments"]
STOP = set("""a o e é as os ao aos de da do das dos du em no na nos nas num numa um uma uns umas que se por pra pro pras
pros para com sem sob mas mais menos ou nem como quando onde porque pq por que entao então ja já so só tambem também ate
até ainda muito muita muitos muitas pouco tudo nada todo toda todos todas isso isto esse essa esses essas este esta estes
estas aquele aquela aqui ali la lá ai aí eu tu ele ela nos nós eles elas voce você voces vocês vc vcs me te lhe mim meu
minha meus minhas seu sua seus suas dele dela deles delas nao não sim ne né ta tá to tô ser ter tem tinha tenho temos
tao tão sao são foi era vai vou vao vão fica ficar fazer faz fez estar esta está estou estao estão ha há pode poder
qual quais quem cara gente coisa coisas assim tipo bem bom boa mesmo mesma outro outra outros outras vez vezes dia
hoje agora sempre nunca raul kkk kkkk kkkkk rs pelo pela pelos pelas sobre entre depois antes ver quer sabe sabia
falar fala falou disse dizer diz acho acha achar olha vamos melhor dele deu dar fosse seria estava estavam consegue
sei quero feito vem veio fazendo nosso nossa nossos nossas""".split())


def sem_acento(s):
    return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()


STOP = {sem_acento(w) for w in STOP}


def pares(texto):
    """(raiz, palavra) das palavras de conteúdo: raiz = 5 letras (quebrando/quebra, governo/governar); números inteiros."""
    out = []
    for w in re.findall(r"[a-z]+|\d+", sem_acento(texto)):
        if w.isdigit():
            out.append((w, w))
        elif len(w) > 2 and w not in STOP:
            out.append(((w[:-1] if w.endswith("s") and len(w) > 4 else w)[:5], w))
    return out


def raizes(texto):
    return [r for r, _ in pares(texto)]


def termos(coments, na_fala):
    """Em quantos comentários cada palavra aparece (likes só desempatam), mesmo sem frase ligada: as que estão na fala (o
    que ecoou) e as que o público trouxe de fora (selic, serasa, emendas...). Cobre o "geral", onde a ligação não chega.
    Conta pessoas, não likes: com likes, um comentário de 200 likes punha todas as palavras dele no topo."""
    n, likes, forma = {}, {}, {}
    for c in coments:
        for r, w in dict(pares(c["texto"])).items():
            if not r.isdigit():
                n[r] = n.get(r, 0) + 1
                likes[r] = likes.get(r, 0) + c["likes"]
                forma.setdefault(r, {}).setdefault(w, 0)
                forma[r][w] += 1
    top = lambda dentro: [[max(forma[r], key=forma[r].get), n[r]] for r in sorted(n, key=lambda r: (-n[r], -likes[r]))
                          if (r in na_fala) == dentro and n[r] >= 2][:15]
    return top(True), top(False)


def vid(arg):
    m = re.search(r"(?:shorts/|v=|youtu\.be/)([A-Za-z0-9_-]{11})", arg)
    return m[1] if m else arg


def baixar(i):
    """Uma chamada do yt-dlp por short: metadados + comentários (top) + legenda automática original (pt.*-orig).
    429: PARA TUDO, sem nova tentativa (um IP marcado só volta com tempo; ver references/pesquisa-e-download.md)."""
    cmd = ["yt-dlp", "--skip-download", "--no-simulate", "--force-overwrites", "--write-info-json", "--write-comments",
           "--write-auto-subs", "--sub-langs", "pt.*-orig", "--extractor-args", "youtube:max_comments=300,all,30;comment_sort=top",
           "-o", os.path.join(BRUTO, "%(id)s.%(ext)s"), "https://www.youtube.com/shorts/" + i]
    for _ in (1,):
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        info_p = os.path.join(BRUTO, i + ".info.json")
        if "429" in r.stderr or "Too Many Requests" in r.stderr:
            raise SystemExit(f"⛔ {i}: 429 (Too Many Requests). Parar tudo agora e só voltar depois de horas; rodar de novo com --cache usa o que já veio.")
        if r.returncode == 0 and os.path.exists(info_p):
            info = json.load(open(info_p, encoding="utf-8"))
            enxuta = {k: info.get(k) for k in CAMPOS}
            enxuta["comments"] = [{k: c.get(k) for k in ("id", "parent", "text", "like_count", "author_is_uploader", "is_pinned")}
                                  for c in info.get("comments") or []]
            total = re.findall(r"/~(\d+)\)", r.stderr + r.stdout)      # o total que o YouTube anuncia (o comment_count vira os baixados)
            enxuta["comentarios_total"] = int(total[-1]) if total else len(info.get("comments") or [])
            json.dump(enxuta, open(info_p, "w", encoding="utf-8"), ensure_ascii=False)
            return True
        print(f"  {i}: falhou ({(r.stderr.strip().splitlines() or ['?'])[-1][:160]})", flush=True)
    return False


def palavras_vtt(path):
    """(segundo, palavra) da legenda automática: só as linhas com tempo por palavra (as outras repetem a anterior)."""
    out = []
    for bloco in open(path, encoding="utf-8").read().split("\n\n"):
        m = re.search(r"(\d+):(\d+):(\d+\.\d+) -->", bloco)
        linha = next((l for l in bloco.split("\n") if "<c>" in l), None)
        if not m or not linha:
            continue
        t0 = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
        primeiro = linha.split("<", 1)[0]
        out += [(t0, w) for w in html.unescape(primeiro).split()]
        for ts, txt in re.findall(r"<(\d+:\d+:\d+\.\d+)><c>([^<]*)</c>", linha):
            h, mi, s = ts.split(":")
            out += [(int(h) * 3600 + int(mi) * 60 + float(s), w) for w in html.unescape(txt).split()]
    return out


def frases(palavras):
    """Junta as palavras em frases: fecha no ponto final e na troca de quem fala (>>); frase curta emenda na seguinte."""
    res, cur = [], []
    for t, w in palavras:
        if w == ">>":
            if len(cur) >= 4:
                res.append(cur)
                cur = []
            continue
        cur.append((t, w))
        if (w[-1] in ".?!" and len(cur) >= 5) or len(cur) >= 35:
            res.append(cur)
            cur = []
    if cur:
        res.append(cur)
    return [{"t": round(f[0][0], 1), "texto": " ".join(w for _, w in f)} for f in res]


def ligar(coments, fr):
    """Para cada comentário, a frase com mais palavras raras em comum (número conta como raro). Uma palavra só ou soma
    abaixo do LIMIAR: geral (um nome citado uma vez, como "Edilson", ligava tudo à frase em que ele aparece)."""
    rz = [set(raizes(f["texto"])) for f in fr]
    df = {}
    for s in rz:
        for w in s:
            df[w] = df.get(w, 0) + 1
    idf = {w: math.log(len(fr) / n) + (1.0 if w.isdigit() else 0.3) for w, n in df.items()}
    for c in coments:
        cr = set(raizes(c["texto"]))
        notas = [sum(idf[w] for w in cr & s) for s in rz]
        k = max(range(len(notas)), key=notas.__getitem__) if notas else None
        c["frase"] = k if k is not None and notas[k] >= LIMIAR and len(cr & rz[k]) >= 2 else None
        c["nota_ligacao"] = round(notas[k], 2) if k is not None else 0
        c["em_comum"] = sorted(cr & rz[k]) if c["frase"] is not None else []


def analisar(i):
    info = json.load(open(os.path.join(BRUTO, i + ".info.json"), encoding="utf-8"))
    vtt = next((os.path.join(BRUTO, f) for f in sorted(os.listdir(BRUTO)) if f.startswith(i + ".pt") and f.endswith("-orig.vtt")), "")
    fr = frases(palavras_vtt(vtt)) if vtt else []
    todos = info.get("comments") or []
    resp = {}
    for c in todos:
        if c["parent"] != "root":
            resp[c["parent"]] = resp.get(c["parent"], 0) + 1
    coments = [{"texto": c["text"], "likes": c.get("like_count") or 0, "respostas": resp.get(c["id"], 0),
                "fixado": bool(c.get("is_pinned"))}
               for c in todos if c["parent"] == "root" and not c.get("author_is_uploader")]
    ligar(coments, fr)
    ecoou, trouxe = termos(coments, {r for f in fr for r in raizes(f["texto"])})
    for f in fr:
        f.update(peso=0, n=0, respostas=0)
    geral = {"peso": 0, "n": 0}
    for c in coments:
        alvo = fr[c["frase"]] if c["frase"] is not None else geral
        alvo["peso"] += 1 + c["likes"]
        alvo["n"] += 1
        if c["frase"] is not None:
            alvo["respostas"] += c["respostas"]
    v = info.get("view_count") or 0
    d = info.get("upload_date") or ""
    res = {"id": i, "url": "https://youtube.com/shorts/" + i, "titulo": info.get("title"),
           "data": f"{d[6:8]}/{d[4:6]}/{d[:4]}" if d else "", "duracao": info.get("duration"), "views": v,
           "likes": info.get("like_count"), "comentarios": info.get("comentarios_total"), "baixados": len(todos),
           "likes_mil": round(1000 * (info.get("like_count") or 0) / v, 1) if v else None,
           "coment_mil": round(1000 * (info.get("comentarios_total") or 0) / v, 2) if v else None,
           "tem_legenda": bool(fr), "geral": geral, "ecoou": ecoou, "trouxe": trouxe, "frases": fr,
           "comentarios_lista": sorted(coments, key=lambda c: -c["likes"])}
    json.dump(res, open(os.path.join(PASTA, i + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


def mmss(t):
    return f"{int(t) // 60:02d}:{int(t) % 60:02d}"


def mil(n):
    return f"{n or 0:,}".replace(",", ".")


def curto(s, n=140):
    s = " ".join(s.split()).replace("|", "/")
    return s if len(s) <= n else s[:n - 1] + "…"


def relatorio(rs):
    rs = sorted(rs, key=lambda r: -r["views"])
    L = ["# Shorts: métricas e o que puxou comentário", "",
         "Gerado por `ferramentas/analise_shorts.py`. Peso de uma frase = soma de (1 + likes) dos comentários ligados a ela.",
         "O mapa aponta onde olhar; quem decide é a leitura dos comentários.", "",
         "| short | data | dur | views | likes | coment. | likes/mil | coment./mil | ligados | título |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        lig = sum(f["peso"] for f in r["frases"])
        tot = lig + r["geral"]["peso"]
        L.append(f"| {r['id']} | {r['data']} | {r['duracao']} s | {mil(r['views'])} | {mil(r['likes'])} | {mil(r['comentarios'])} | "
                 f"{r['likes_mil']} | {r['coment_mil']} | {100 * lig / max(1, tot):.0f}% | {curto(r['titulo'], 60)} |")
    for r in rs:
        tot = max(1, sum(f["peso"] for f in r["frases"]) + r["geral"]["peso"])
        L += ["", f"## {r['titulo']} ({r['id']})", "",
              f"{r['url']} · {r['data']} · {r['duracao']} s · {mil(r['views'])} views · {r['likes_mil']} likes/mil · "
              f"{r['coment_mil']} coment./mil · {r['baixados']} comentários baixados", ""]
        if not r["tem_legenda"]:
            L.append("Sem legenda original em português: só os comentários abaixo.")
        quentes = sorted([f for f in r["frases"] if f["peso"]], key=lambda f: -f["peso"])[:6]
        if quentes:
            L += ["**Frases mais quentes**", "", "| tempo | peso | % | coment. | respostas | frase |", "|---|---|---|---|---|---|"]
            L += [f"| {mmss(f['t'])} | {f['peso']} | {100 * f['peso'] / tot:.0f}% | {f['n']} | {f['respostas']} | {curto(f['texto'], 160)} |"
                  for f in quentes]
            L.append(f"| geral | {r['geral']['peso']} | {100 * r['geral']['peso'] / tot:.0f}% | {r['geral']['n']} | – | sem frase ligada |")
        L += ["", "**Palavras da fala que mais ecoaram nos comentários** (nº de comentários): " + ", ".join(f"{w} ({p})" for w, p in r["ecoou"]),
              "", "**O que o público trouxe de fora** (nº de comentários): " + ", ".join(f"{w} ({p})" for w, p in r["trouxe"])]
        L += ["", "**Comentários mais curtidos**", ""]
        for c in r["comentarios_lista"][:10]:
            onde = mmss(r["frases"][c["frase"]]["t"]) if c["frase"] is not None else "geral"
            L.append(f"- {c['likes']} likes · {c['respostas']} resp. · [{onde}] {curto(c['texto'])}")
    open(os.path.join(PASTA, "relatorio.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    cache = "--cache" in sys.argv
    ids = [vid(a) for a in sys.argv[1:] if a != "--cache"]
    os.makedirs(BRUTO, exist_ok=True)
    if cache and not ids:
        ids = sorted(f[:-10] for f in os.listdir(BRUTO) if f.endswith(".info.json"))
    for k, i in enumerate(ids):
        if not cache:
            print(f"{k + 1}/{len(ids)} baixando {i}", flush=True)
            if not baixar(i):
                print(f"  {i}: sem dados, segue", flush=True)
            if k < len(ids) - 1:
                time.sleep(8)      # pedidos espaçados: rajada marca o IP com 429 (PROCESSO.md)
    rs = [analisar(i) for i in ids if os.path.exists(os.path.join(BRUTO, i + ".info.json"))]
    relatorio(rs)
    for r in rs:
        q = max(r["frases"], key=lambda f: f["peso"], default=None)
        print(f"{r['id']} · {r['views']:>9,} views · {r['likes_mil']:>5} likes/mil · {r['coment_mil']:>5} coment./mil · "
              f"mais quente: {curto(q['texto'], 70) if q and q['peso'] else '-'}")
    print("relatório: _pesquisa/shorts_analise/relatorio.md")


if __name__ == "__main__":
    if len(sys.argv) < 2 or any(a in ("-h", "--help") for a in sys.argv[1:]):
        sys.exit(__doc__)   # ajuda sem fazer nenhum pedido de rede
    main()
