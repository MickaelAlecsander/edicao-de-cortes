# -*- coding: utf-8 -*-
"""Ranking dos shorts do Raul para os posts do dia: chance de viralizar × quão pouco foi reproduzido por outros.

    python $S/ranking_shorts.py            # lista nova + buscas (lento: 1 busca a cada 8 s; as já feitas ficam no cache)
    python $S/ranking_shorts.py --cache    # refaz só a conta com a lista e as buscas já salvas

1. Viralização = log10(views) + 1,5 × log10(views ÷ mediana dos 50 vizinhos). O segundo termo mede o quanto o
   short furou a bolha da época dele: o canal cresceu, então 200 mil hoje e 200 mil há dois anos não valem igual.
2. Reprodução = quantos vídeos de OUTROS canais aparecem na busca do YouTube com o título parecido (cortes e
   reuploads). Limite: só enxerga o YouTube; repost no TikTok/Instagram não entra na conta. Cada cópia tira 0,35 ponto; mais de 6 conta como 6.
3. Saem os já usados (os ids que aparecem em LOG_CORTES.md).

Escreve `_pesquisa/ranking_shorts.md` (top 100) e guarda as buscas em `_pesquisa/shorts_buscas.json`.
"""
import json
import math
import os
import re
import statistics
import subprocess
import sys
import time
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = os.environ.get("CORTES_RAIZ", os.getcwd())   # a raiz do projeto (rodar de lá ou definir CORTES_RAIZ)
P = lambda *a: os.path.join(RAIZ, *a)
CANAL = "https://www.youtube.com/@investidorsardinha/shorts"
TOP_BUSCA = 160          # só os mais virais passam pela busca de cópias (cada busca é um pedido ao YouTube)


def tokens(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return {w for w in re.findall(r"[a-z0-9]+", s) if len(w) > 2}


def parecido(a, b):
    ta, tb = tokens(a), tokens(b)
    return len(ta & tb) / max(1, min(len(ta), len(tb))) if ta and tb else 0


def buscar(titulo):
    out = subprocess.run(["yt-dlp", "--extractor-args", "youtube:player_client=web_safari,mweb", "--flat-playlist", "-J", "ytsearch15:" + titulo], capture_output=True, text=True,
                         encoding="utf-8", timeout=120)
    if "429" in out.stderr or "Too Many Requests" in out.stderr:
        raise SystemExit("⛔ 429 (Too Many Requests) na busca. Parar tudo agora e só voltar depois de horas; as buscas já feitas ficam no cache.")
    if out.returncode:
        return None
    return [{"t": e.get("title") or "", "c": e.get("channel") or e.get("uploader") or "", "id": e.get("id")}
            for e in json.loads(out.stdout).get("entries", [])]


def main():
    lista = P("_pesquisa", "shorts_lista.json")
    if "--cache" not in sys.argv:
        with open(lista, "w", encoding="utf-8") as f:
            subprocess.run(["yt-dlp", "--extractor-args", "youtube:player_client=web_safari,mweb", "--flat-playlist", "-J", CANAL], stdout=f, check=True)
    E = [e for e in json.load(open(lista, encoding="utf-8"))["entries"] if e.get("view_count")]
    usados = set(re.findall(r"[A-Za-z0-9_-]{11}", open(P("LOG_CORTES.md"), encoding="utf-8").read())) if os.path.exists(P("LOG_CORTES.md")) else set()

    for i, e in enumerate(E):          # a lista vem do mais novo para o mais antigo
        viz = [x["view_count"] for x in E[max(0, i - 25): i + 26]]
        e["rel"] = e["view_count"] / statistics.median(viz)
        e["viral"] = math.log10(e["view_count"]) + 1.5 * math.log10(e["rel"])
        e["pos"] = i + 1
    cand = sorted([e for e in E if e["id"] not in usados], key=lambda e: -e["viral"])[:TOP_BUSCA]

    cache_p = P("_pesquisa", "shorts_buscas.json")
    cache = json.load(open(cache_p, encoding="utf-8")) if os.path.exists(cache_p) else {}
    for k, e in enumerate(cand):
        if e["id"] not in cache and "--cache" not in sys.argv:
            r = buscar(e["title"])
            if r is not None:
                cache[e["id"]] = r
                json.dump(cache, open(cache_p, "w", encoding="utf-8"), ensure_ascii=False)
            print(f"busca {k + 1}/{len(cand)}", flush=True)
            # ⚠ 02/10/2026: 160 buscas a cada 2,5 s marcaram o IP, e o download da fonte das 19h levou 403 logo depois
            # (só o formato 18, 360p, passou). Espaçar mais e NUNCA rodar antes de baixar a fonte do dia.
            time.sleep(8)
        res = cache.get(e["id"], [])
        e["copias"] = sum(1 for r in res if r["id"] != e["id"] and "sardinha" not in r["c"].lower()
                          and "raul sena" != r["c"].lower() and parecido(e["title"], r["t"]) >= 0.6)
        e["buscado"] = e["id"] in cache
        e["nota"] = e["viral"] - 0.35 * min(e["copias"], 6)

    top = sorted(cand, key=lambda e: -e["nota"])[:100]
    linhas = ["# Ranking dos shorts para os posts do dia", "",
              f"Gerado por `ferramentas/ranking_shorts.py` · {len(E)} shorts no canal · {len(usados & {e['id'] for e in E})} já usados.",
              "Nota = viralização (views e quanto furou a bolha da época) − 0,35 por cópia de outros canais na busca do YouTube.",
              "", "| # | Nota | Views | × época | Cópias | Idade (posição) | Título | Link |", "|---|---|---|---|---|---|---|---|"]
    for k, e in enumerate(top, 1):
        cop = str(e["copias"]) if e["buscado"] else "?"
        linhas.append(f"| {k} | {e['nota']:.2f} | {e['view_count']:,} | {e['rel']:.1f}× | {cop} | {e['pos']}º mais novo | "
                      f"{e['title'].replace('|', '/')} | https://youtube.com/shorts/{e['id']} |".replace(",", "."))
    open(P("_pesquisa", "ranking_shorts.md"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("ranking escrito: _pesquisa/ranking_shorts.md")
    for k, e in enumerate(top[:15], 1):
        print(f"{k:2d}. {e['nota']:.2f} · {e['view_count']:>9,} · {e['rel']:4.1f}× · cópias {e['copias']} · {e['title']}")


if __name__ == "__main__":
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        sys.exit(__doc__)   # ajuda sem fazer nenhum pedido de rede
    main()
