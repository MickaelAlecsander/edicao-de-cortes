# -*- coding: utf-8 -*-
"""Monta o index.html do corte (o papel padrão: folha de 0 a 960, Raul de 960 a 1920, chão fixo, travelling lateral,
TELA CHEIA, legenda v3 e a marca do canal). Generalizado do montar.py do C84.

    python montar.py                      # na pasta do corte (cortes/cNN-slug/)

Parte do motor.html (o index.html do C02) e troca as cenas dele pelas do corte:
cenas = cabeçalho (com a const TELAS) + _ajudantes.js + personagens.js + elementos.js + _desenhos.js + _cab48.js +
_base.js + CENAS + _vida.js; a legenda do motor dá lugar à legenda.js (v3). Lê assets/dados.js (as palavras com tempo,
do legendas.py) e grava index.html e assets/tela_cheia.json (as janelas que o finalizar.py não confere como "Raul parado").
A marca vem do scripts/marca.py da skill (variável EDICAO_CORTES, ou ~/.claude/skills/edicao-de-cortes).
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ── O QUE MUDA POR CORTE ──────────────────────────────────────────────────────────────────────────────────────────────
TITULO = "EXEMPLO · OS 2 PRIMEIROS BLOCOS DO C84"
CENAS = "_cenas_exemplo.js"   # o arquivo de cenas do corte (no corte novo: _cenas.js)
# As telas cheias, na ordem: (início, fim). Cada ponta é (palavra, bloco, n, desloc): o instante em que a n-ésima
# ocorrência da palavra é dita DENTRO do bloco (o mesmo T() das cenas) + desloc. Palavra None = início do bloco + desloc.
# Padrão: 3 ou mais em vídeo de até 2 min, 4 acima; 5 s ou mais cada; a 1ª logo depois do gancho; espalhadas, nunca no fim.
TELAS = [
    (("gente", "gancho", 2, -0.05), ("tipo", "gancho", 1, 0.3)),
]
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)
SKILL = os.environ.get("EDICAO_CORTES") or os.path.expanduser("~/.claude/skills/edicao-de-cortes")
sys.path.insert(0, os.path.join(SKILL, "scripts"))
try:
    from marca import aplicar  # noqa: E402  a marca do canal (07/10/2026)
except ImportError:
    sys.exit(f"⛔ não achei o scripts/marca.py da skill em {SKILL}: defina EDICAO_CORTES com a pasta da skill")

le = lambda f: open(f, encoding="utf-8").read()
cenas_txt = le(CENAS)
assert "camera(" in cenas_txt, f"{CENAS}: falta o camera([...]) no fim (sem ele a câmera fica fora do lugar e nada ferve)"

# as palavras com tempo: as mesmas que o W() do index lê
s_dados = le("assets/dados.js")
D = json.loads(s_dados[s_dados.index("{"):].rstrip().rstrip(";"))
dur = D["duracao"]
B = {b["id"]: b["inicio"] for b in D["blocos"]}
norm = lambda w: re.sub(r"^,+|,+$", "", re.sub(r"[^a-zà-ú0-9%,]", "", w.lower()))


def T(w, bloco, n=1, desl=0.0):
    """O W() do index (com o patch do bloco): a n-ésima ocorrência de w dita dentro do bloco, + desl."""
    if w is None:
        return B[bloco] + desl
    k, t0 = 0, B[bloco] - 0.06
    for p in D["palavras"]:
        if p["s"] < t0:
            continue
        if p.get("bloco") != bloco:
            if p["s"] > B[bloco]:
                break
            continue
        if norm(p["w"]) == norm(w):
            k += 1
            if k == n:
                return p["s"] + desl
    sys.exit(f"⛔ TELAS: palavra não encontrada: {w!r} (n={n}) no bloco {bloco!r}")


J = [(round(T(*a), 3), round(T(*b), 3)) for a, b in TELAS]
# a regra da tela cheia (16/10/2026): avisa, não para
minimo = 4 if dur > 120 else 3
if len(J) < minimo:
    print(f"⚠ {len(J)} tela(s) cheia(s): o padrão pede {minimo} ou mais num vídeo de {dur:.0f} s")
for i, (a, b) in enumerate(J, 1):
    if b - a < 5:
        print(f"⚠ a tela cheia {i} tem {b - a:.1f} s (o padrão é 5 s ou mais)")
if J and J[0][0] > 20:
    print(f"⚠ a 1ª tela cheia começa em {J[0][0]:.1f} s: ela vem logo depois do gancho")
for i in range(1, len(J)):
    if J[i][0] - J[i - 1][1] < 8:
        print(f"⚠ as telas cheias {i} e {i + 1} estão coladas ({J[i][0] - J[i - 1][1]:.1f} s entre elas)")
if J and dur - J[-1][1] < 6:
    print(f"⚠ a última tela cheia acaba a {dur - J[-1][1]:.1f} s do fim: ela não cai no fim")

base = le("motor.html")
CAB = f"""        // ══════════════════════════════════════════════════════════════════════
        // CENAS · {TITULO} (montadas por montar.py: motor.html + bancos + _base.js + {CENAS} + _vida.js)
        // ══════════════════════════════════════════════════════════════════════
        const TELAS = {json.dumps([list(x) for x in J])};   // as telas cheias [t0, t1] (montar.py, lista TELAS)
"""
cenas = CAB + "".join(le(f) for f in ["_ajudantes.js", "personagens.js", "elementos.js", "_desenhos.js", "_cab48.js", "_base.js", CENAS, "_vida.js"])

ini = base.index("        // ══════════════════════════════════════════════════════════════════════\n        // CENA 0")
fim = base.index("        // ── RAUL: enquadramento")
s = base[:ini] + cenas + base[fim:]
a = s.index("        // ── LEGENDA ─")
z = s.index("        window.__timelines")
s = s[:a] + le("legenda.js") + s[z:]
s = s.replace("238.25", str(dur))
s = re.sub(r"(<!-- sfx:inicio -->).*?(\s*<!-- sfx:fim -->)", r"\1\2", s, flags=re.S)
s = re.sub(r"\s*<!-- gráfico que o próprio vídeo.*?</video>\n", "\n", s, flags=re.S)
s = s.replace('<small>/11</small>', '<small>/${TOTAL}</small>')
LAYOUT = [
    # 50/50: a janela do Raul de 960 a 1920, a folha até 990 com a borda rasgada em ~960, a legenda centrada em 960
    ("top: 768px; width: 1080px; height: 1152px;", "top: 960px; width: 1080px; height: 960px;"),          # janela + fundo
    ("#raul { position: absolute; inset: 0; width: 1080px; height: 1152px;", "#raul { position: absolute; inset: 0; width: 1080px; height: 960px;"),
    ("#rasgo { position: absolute; left: 0; top: 0; width: 1080px; height: 1060px;", "#rasgo { position: absolute; left: 0; top: 0; width: 1080px; height: 1252px;"),
    ('<svg id="rasgo" viewBox="0 0 1080 1060">', '<svg id="rasgo" viewBox="0 0 1080 1252">'),
    ("#topo { position: absolute; left: 0; top: 0; width: 1080px; height: 798px;", "#topo { position: absolute; left: 0; top: 0; width: 1080px; height: 990px;"),
    (".cap { position: absolute; left: 24px; top: 22px;", ".cap { position: absolute; left: 24px; top: 150px;"),
    ("#hud { position: absolute; left: 0; top: 0; width: 1080px; height: 200px;", "#hud { position: absolute; left: 0; top: 0; width: 1080px; height: 330px;"),
    ("#leg { position: absolute; left: 0; top: 698px;", "#leg { position: absolute; left: 0; top: 890px;"),
    ("const VX = 540, VY = 400;", "const VX = 540, VY = 555;"),
    ("const y = 768 + Math.sin(x / 61)", "const y = 960 + Math.sin(x / 61)"),
    ('const fibra = (dy) => "M0 660 L1080 660 L"', 'const fibra = (dy) => "M0 852 L1080 852 L"'),
    # a câmera inicial é das cenas (o camera() do _base.js): o set do motor em 0 ganhava no quadro 0 (C27)
    ("        tl.set(mundo, camAtual, 0);\n        function camPara", "        function camPara"),
    # W(palavra, bloco) só procura DENTRO do bloco (C40): para na 1ª palavra de outro bloco depois do início
    ("            if (p.s < t0) continue;\n", "            if (p.s < t0) continue;\n"
     "            if (bloco && p.bloco !== bloco) { if (p.s > B[bloco]) break; continue; }\n"),
    # o CHÃO FIXO (12/10/2026): as cenas lado a lado a cada 1300 px, na mesma altura, e a troca é um travelling lateral
    ("        function cena(i, x, y) {\n", "        function cena(i, x, y) {\n          x = i * 1300; y = 0;\n"),
    ("          const a = camAtual, b = camS(i, lx, z);\n"
     "          const ax = (VX - a.x) / a.scale, ay = (VY - a.y) / a.scale, bx = (VX - b.x) / b.scale, by = (VY - b.y) / b.scale;\n"
     "          const d = Math.hypot(bx - ax, by - ay);\n"
     "          const zm = Math.max(0.06, Math.min(0.5, 1300 / (d + 1300)));\n"
     "          const extra = Math.min(0.55, d / 40000);\n"
     "          camVia(cam((ax + bx) / 2, (ay + by) / 2, zm), b, t - 0.3 - extra * 0.5, 0.32 + extra, 0.42 + extra);\n",
     "          camPara(camS(i, lx, z), t - 0.32, 0.82, \"power2.inOut\");\n"),
    # o Raul SEM ZOOM (14/10/2026): sai o 1,00/1,08 por bloco com o avanço de 3%
    ("""        D.blocos.forEach((b, i) => {
          const z = i % 2 ? 1.08 : 1.0;
          tl.fromTo("#raul-cam", { scale: z }, { scale: z + 0.03, duration: b.dur, ease: "none", immediateRender: false }, b.inicio);
        });""", "        // o Raul sem zoom (14/10/2026): o enquadramento vem pronto do cortar.py"),
    # a TELA CHEIA (16/10/2026): a folha, o grão e a borda de cima; a legenda fica por cima dela
    ("      #rasgo-sombra {", "      .cheia { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 20; }\n"
     "      .cheia-papel { position: absolute; inset: 0; background: #efe6d3 url(assets/papel.png) repeat;\n"
     "        box-shadow: inset 0 22px 22px -14px rgba(30, 27, 46, 0.32); }\n"
     "      .cheia-grao { position: absolute; inset: 0; background: url(assets/grao.png) repeat; mix-blend-mode: overlay; opacity: 0.5; }\n"
     "      .cheia-dentro { position: absolute; inset: 0; }\n"
     "      #leg { z-index: 25; }\n"
     "      #rasgo-sombra {"),
    # o papel pousa, amassa um pouco e balança até parar (C72)
    ("""            { autoAlpha: 1, scale: 1, y: 0, x: 0, rotation: 0, duration: dur, ease: S(dur, "back.out(1.8)"), immediateRender: false }, t);
        };""", """            { autoAlpha: 1, scale: 1, y: 0, x: 0, rotation: 0, duration: dur, ease: S(dur, "back.out(1.8)"), immediateRender: false }, t);
          (Array.isArray(el) ? el : [el]).forEach((e) => {
            const nome = typeof e === "string" ? e : e.id || "x", sem = [...nome].reduce((a, c) => a + c.charCodeAt(0), 0);
            tl.fromTo(e, { scaleX: 1.07, scaleY: 0.93 }, { scaleX: 1, scaleY: 1, duration: 0.5, ease: "elastic.out(1, 0.45)", immediateRender: false }, t + dur);
            tl.fromTo(e, { rotation: (rnd(sem) < 0.5 ? -1 : 1) * (1.6 + rnd(sem + 1) * 1.8) }, { rotation: 0, duration: 0.9, ease: "elastic.out(1, 0.3)", immediateRender: false }, t + dur);
          });
        };"""),
    # o carimbo solta papel picado (C72)
    ("""          if (tremor) treme(t + 0.06, 7 * big, 0.2, Math.round(t * 10));
        };""", """          if (tremor) treme(t + 0.06, 7 * big, 0.2, Math.round(t * 10));
          poeira(el, t + 0.04, 12);
        };
        // pedacinhos de papel que voam do impacto (carimbo, ✗) e caem girando
        function poeira(el, t, n = 10) {
          poeira.n = (poeira.n || 0) + 1;
          const pai = el.parentNode, w = parseFloat(el.style.width) || 200, x0 = parseFloat(el.style.left) + w / 2, y0 = parseFloat(el.style.top) + 46;
          for (let k = 0; k < n; k++) {
            const sem = poeira.n * 97 + k * 13, s = 9 + rnd(sem) * 12, a = (k / n) * Math.PI * 2 + rnd(sem + 1) * 0.7, d = 110 + rnd(sem + 2) * 150;
            const p = obj(pai, "pz" + poeira.n + "_" + k, x0 - s / 2, y0, s, s * 0.62, `<rect x="1" y="1" width="${s - 2}" height="${s * 0.62 - 2}" rx="1.5" fill="${[C.claro, C.kraft2, C.verm, C.amar][k % 4]}" stroke="${C.tinta}" stroke-width="1.5"/>`, false, false);
            p.style.zIndex = 6;
            tl.set(p, { autoAlpha: 0 }, 0);
            tl.set(p, { autoAlpha: 1 }, t);
            tl.fromTo(p, { x: 0, y: 0, rotation: 0 }, { x: Math.cos(a) * d, y: Math.sin(a) * d * 0.55 - 40, rotation: (rnd(sem + 3) - 0.5) * 720, duration: 0.45, ease: "power3.out", immediateRender: false }, t);
            tl.to(p, { y: "+=" + (90 + rnd(sem + 4) * 80), rotation: "+=" + (rnd(sem + 5) - 0.5) * 360, autoAlpha: 0, duration: 0.7, ease: "power1.in" }, t + 0.45);
          }
        }"""),
    # a trilha de efeitos do sonoplastia.py (som.json): uma faixa só, já mixada por baixo da voz
    ("      <!-- sfx:inicio -->", "      <!-- sfx:inicio --> trilha de efeitos do sonoplastia.py (som.json)\n"
     '      <audio id="sfx-mix" data-start="0" data-duration="%s" data-track-index="9" src="assets/sfx_mix.wav" data-volume="1"></audio>' % dur),
]
for a, b in LAYOUT:
    assert a in s, "motor.html mudou, não achei: " + a[:70]
    s = s.replace(a, b)
assert "grafico_gini" not in s and "/${TOTAL}" in s
if not os.path.exists("assets/sfx_mix.wav"):
    s = s.replace('src="assets/sfx_mix.wav"', 'src="assets/raul.wav" data-volume="0"')   # antes da trilha existir
json.dump([[round(a - 0.5, 3), round(b + 0.47, 3)] for a, b in J], open("assets/tela_cheia.json", "w"))
s = aplicar(s, AQUI)
open("index.html", "w", encoding="utf-8").write(s)
if os.path.isdir("capa"):   # a capa usa o mesmo papel e grão
    os.makedirs("capa/assets", exist_ok=True)
    for f in ("papel.png", "grao.png"):
        if not os.path.exists("capa/assets/" + f):
            shutil.copyfile("assets/" + f, "capa/assets/" + f)

# nome repetido no escopo do motor (const cai, ST…) mata o script inteiro e o "hyperframes check" diz 0 errors (C39)
js = s[s.rindex("<script>") + 8:s.rindex("</script>")]
open(".montado.js", "w", encoding="utf-8").write(js)
try:
    r = subprocess.run(["node", "--check", ".montado.js"], capture_output=True, text=True, encoding="utf-8")
    os.remove(".montado.js")
    if r.returncode:
        sys.exit("⛔ node --check (o script do index.html):\n" + r.stderr.strip())
    print("✓ node --check: sem erro de sintaxe")
except FileNotFoundError:
    os.remove(".montado.js")
    print("⚠ sem node no PATH: o node --check não rodou")
print("index.html montado (50/50 + %d tela(s) cheia(s)): %d linhas, %.3f s" % (len(J), s.count("\n"), dur))
