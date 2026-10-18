# -*- coding: utf-8 -*-
"""Monta o index.html de um REELS DE VÍDEO REAL (a pessoa na tela inteira, sem a animação de papel).

    python montar_reels.py            (na pasta do corte, depois do cortar.py, do pos_cortar.py e do legendas.py)

Lê o `reels.json` (manchetes, nome e função de quem fala, imagens de cobertura, logo, cores, música) e os arquivos que a
Etapa 2 escreve: `assets/raul.mp4` (1080×1920: o `cortes_gerar.py` com JW, JH = 1080, 1920), `assets/raul.wav`,
`assets/tempos.json` e `assets/dados.js` (a legenda). Escreve:
  · index.html             a composição do HyperFrames (vídeo + coberturas + manchetes + nomes + logo + legenda);
  · assets/tela_cheia.json as janelas das coberturas com FOTO (o finalizar.py não acusa imagem parada ali);
  · som.json               (com "som": true) o som discreto das entradas, para o sonoplastia.py.
Todo tempo do reels.json é um número (s) ou uma âncora ["palavra", "bloco", n, deslocamento], como o T() das cenas: a
âncora segue a palavra quando o corte muda. Nenhuma API.
"""
import html
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
    print(__doc__)
    sys.exit(0)

cfg = json.load(open("reels.json", encoding="utf-8"))
tempos = json.load(open("assets/tempos.json", encoding="utf-8"))
DUR = tempos["duracao"]
norm = lambda w: re.sub(r"^,+|,+$", "", re.sub(r"[^a-zà-ú0-9%,]", "", w.lower()))


def T(x):
    """número (s) ou ["palavra", "bloco", n, deslocamento] → segundos na montagem"""
    if isinstance(x, (int, float)):
        return float(x)
    x = list(x)
    w, bloco = x[0], (x[1] if len(x) > 1 else None)
    n, d = (int(x[2]) if len(x) > 2 else 1), (float(x[3]) if len(x) > 3 else 0.0)
    for b in tempos["blocos"]:
        if bloco is None or b["id"] == bloco:
            ach = [p["s"] for p in b["palavras"] if norm(p["w"]) == norm(w)]
            if len(ach) >= n:
                return round(ach[n - 1] + d, 3)
    raise SystemExit(f"⛔ âncora não achada: {x} (conferir a palavra, o bloco e o n no assets/tempos.json)")


C = {"cartao": "#ffffff", "texto": "#1e1b2e", "marca_texto": "#f5a623", "destaque": "#e5432d",
     "manchete_fundo": "#f5a623", "manchete_texto": "#1e1b2e", "nome_fundo": "#1e1b2e", "nome_texto": "#ffffff"}
C.update(cfg.get("cores", {}))
LEG_Y = cfg.get("legenda_y", 1270)
esc = lambda s: html.escape(str(s)).replace("\n", "<br>")

# ── a composição ─────────────────────────────────────────────────────────────────────────────────────────────────
midia, sobre, js, fotos, deixas = [], [], [], [], []
trilha = 2
for k, c in enumerate(cfg.get("coberturas", []), 1):
    a, z = T(c["de"]), T(c["ate"])
    if z - a < 0.5:
        raise SystemExit(f"⛔ cobertura {k}: {a:.2f}–{z:.2f} s é curta demais")
    if not os.path.exists(c["arquivo"]):
        raise SystemExit(f"⛔ cobertura {k}: falta o arquivo {c['arquivo']}")
    foto = c["arquivo"].lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    atr = f'id="cob{k}" class="clip cob" data-start="{a:.3f}" data-duration="{z - a:.3f}" data-track-index="{trilha}"'
    if foto:
        midia.append(f'      <img {atr} src="{c["arquivo"]}" alt="" />')
        fotos.append([round(a - 0.1, 3), round(z + 0.1, 3)])
    else:
        midia.append(f'      <video {atr} data-media-start="{float(c.get("inicio", 0)):.3f}" src="{c["arquivo"]}" muted playsinline></video>')
    trilha += 1
    deixas.append({"nota": f"cobertura {k}", "t": round(a - 0.12, 3), "som": "whoosh", "camada": "transicao", "pan": 0.0, "db": -4})

for k, m in enumerate(cfg.get("manchetes", []), 1):
    a, z = T(m["de"]), T(m["ate"])
    linhas = str(m["texto"]).split("\n")
    fs = min(int(m.get("tamanho", 66)), int(880 / (max(len(l) for l in linhas) * 0.66)))
    sobre.append(f'        <div id="m{k}" class="manchete" style="top:{int(m.get("y", 300))}px;font-size:{fs}px"><span>{esc(m["texto"])}</span></div>')
    js.append(f'        entra("#m{k}", {a:.3f}, {z:.3f});')
    deixas.append({"nota": f"manchete {k}", "t": round(a, 3), "som": "pousa", "camada": "miudo", "pan": 0.0, "db": -5})

for k, n in enumerate(cfg.get("nomes", []), 1):
    a, z = T(n["de"]), T(n["ate"])
    sobre.append(f'        <div id="n{k}" class="nome" style="top:{int(n.get("y", 1060))}px"><b>{esc(n["nome"])}</b>'
                 + (f'<i>{esc(n["funcao"])}</i>' if n.get("funcao") else "") + "</div>")
    js.append(f'        entra("#n{k}", {a:.3f}, {z:.3f}, -40);')
    deixas.append({"nota": f"nome {k}", "t": round(a, 3), "som": "desliza", "camada": "miudo", "pan": -0.3, "db": -6})

logo = cfg.get("logo") or {}
if logo.get("arquivo"):
    if not os.path.exists(logo["arquivo"]):
        raise SystemExit(f"⛔ falta o logo: {logo['arquivo']}")
    lado = "right" if logo.get("canto", "esquerda") == "direita" else "left"
    sobre.append(f'        <img id="logo" src="{logo["arquivo"]}" alt="" style="{lado}:60px;width:{int(logo.get("tamanho", 120))}px" />')

if cfg.get("musica", {}).get("arquivo"):
    mu = cfg["musica"]
    if not os.path.exists(mu["arquivo"]):
        raise SystemExit(f"⛔ falta a música: {mu['arquivo']}")
    midia.append(f'      <audio id="musica" data-start="0" data-duration="{DUR}" data-track-index="8" src="{mu["arquivo"]}" data-volume="{float(mu.get("volume", 0.07))}"></audio>')
if os.path.exists("assets/sfx_mix.wav"):
    midia.append(f'      <audio id="sfx-mix" data-start="0" data-duration="{DUR}" data-track-index="9" src="assets/sfx_mix.wav" data-volume="1"></audio>')

SKILL = os.environ.get("EDICAO_CORTES") or os.path.expanduser("~/.claude/skills/edicao-de-cortes")
LEG = os.path.join(SKILL, "assets", "modelo", "legenda.js")
if not os.path.exists(LEG):
    raise SystemExit(f"⛔ não achei a skill em {SKILL}: defina EDICAO_CORTES=<pasta da skill>")
legenda = open(LEG, encoding="utf-8").read()

pagina = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{esc(cfg.get("titulo_do_video", "Reels"))}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script src="assets/dados.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
      #pessoa, .cob {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .cob {{ z-index: 2; }}
      .reels {{ position: absolute; inset: 0; z-index: 10; pointer-events: none; }}
      .manchete {{ position: absolute; left: 540px; transform: translateX(-50%); width: max-content; max-width: 900px; text-align: center; }}
      .manchete span {{ display: inline; padding: 6px 22px; line-height: 1.32; -webkit-box-decoration-break: clone; box-decoration-break: clone;
        background: {C["manchete_fundo"]}; color: {C["manchete_texto"]}; font-family: "Archivo Black", sans-serif; text-transform: uppercase;
        border-radius: 10px; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35); }}
      .nome {{ position: absolute; left: 60px; max-width: 840px; padding: 16px 26px 16px 22px; border-left: 10px solid {C["marca_texto"]};
        background: {C["nome_fundo"]}; color: {C["nome_texto"]}; border-radius: 0 12px 12px 0; box-shadow: 0 8px 22px rgba(0, 0, 0, 0.35); }}
      .nome b {{ display: block; font-family: "Archivo Black", sans-serif; font-size: 42px; line-height: 1.05; }}
      .nome i {{ display: block; font-family: "Archivo Black", sans-serif; font-style: normal; font-size: 26px; line-height: 1.2; opacity: 0.85; margin-top: 6px; }}
      #logo {{ position: absolute; top: 160px; height: auto; filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.4)); }}
      #leg {{ position: absolute; left: 0; top: {LEG_Y - 70}px; width: 1080px; height: 140px; pointer-events: none; z-index: 20; }}
      .etq {{ position: absolute; left: 50%; top: 50%; white-space: nowrap; font-family: "Archivo Black", sans-serif; line-height: 1;
        letter-spacing: -0.01em; text-transform: uppercase; opacity: 0; }}
      .etq span {{ display: inline-block; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <video id="pessoa" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0" src="assets/raul.mp4" muted playsinline></video>
      <audio id="voz" data-start="0" data-duration="{DUR}" data-track-index="1" src="assets/raul.wav" data-volume="1"></audio>
{chr(10).join(midia)}
      <div class="reels" id="sobre">
{chr(10).join(sobre)}
      </div>
      <div id="leg"></div>
    </div>
    <script>
      (function () {{
        const tl = gsap.timeline({{ paused: true }});
        const $ = (s) => document.querySelector(s);
        const rnd = (i) => {{ const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }};
        const S = (dur, base = "power2.out") => gsap.parseEase(base);
        const D = window.DADOS;
        // a manchete e o nome entram subindo de leve e saem esmaecendo
        const entra = (sel, a, z, dx = 0) => {{
          tl.set(sel, {{ autoAlpha: 0 }}, 0);
          tl.fromTo(sel, {{ autoAlpha: 0, y: 26, x: dx }}, {{ autoAlpha: 1, y: 0, x: 0, duration: 0.32, ease: "power2.out", immediateRender: false }}, a);
          tl.to(sel, {{ autoAlpha: 0, duration: 0.2, ease: "power1.in" }}, z);
        }};
{legenda}
        // as cores da marca por cima das da legenda do canal de papel
        const cor = document.createElement("style");
        cor.textContent = `
          #leg .pp {{ background: {C["cartao"]}; color: {C["texto"]}; border-color: {C["texto"]}; box-shadow: 5px 6px 0 rgba(0, 0, 0, 0.35); }}
          #leg .mk {{ background: {C["marca_texto"]}; }}
          #leg .forte b {{ color: {C["destaque"]}; }}`;
        document.head.appendChild(cor);
{chr(10).join(js)}
        tl.set({{}}, {{}}, {DUR});
        (window.__timelines = window.__timelines || {{}})["main"] = tl;
      }})();
    </script>
  </body>
</html>
"""
open("index.html", "w", encoding="utf-8").write(pagina)
json.dump(fotos, open("assets/tela_cheia.json", "w"))
if cfg.get("som", True):
    json.dump({"nota": "Som discreto do reels (montar_reels.py): whoosh nas coberturas, pouso nas manchetes e nos nomes.",
               "deixas": deixas}, open("som.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# sintaxe do script da página (o mesmo node --check do montar.py do papel)
corpo = pagina[pagina.rindex("<script>") + 8: pagina.rindex("</script>")]
tmp = os.path.join(os.path.abspath("."), "_check_reels.js")
open(tmp, "w", encoding="utf-8").write(corpo)
r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
os.remove(tmp)
if r.returncode:
    raise SystemExit("⛔ node --check:\n" + r.stderr)
print("✓ node --check: sem erro de sintaxe")
print("index.html montado (reels de vídeo real): %d manchete(s), %d nome(s), %d cobertura(s), %.3f s"
      % (len(cfg.get("manchetes", [])), len(cfg.get("nomes", [])), len(cfg.get("coberturas", [])), DUR))
