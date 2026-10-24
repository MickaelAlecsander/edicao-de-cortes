// Confere a ÁREA DE SEGURANÇA da animação em todo o vídeo, antes do render. Abre o index.html no Chrome sem tela, anda na
// linha do tempo e mede cada peça visível (o retângulo do que ela desenha, não da caixa).
//   node <skill>/scripts/zona_segura.mjs cortes/<slug> [--passo 0.25]
// Nasceu em 17/10/2026 (Mickael, depois do C80 e do C83): "aquela nossa área de segurança... sumiu. Teve muita coisa que
// ficou para fora dos lados, ou ficou embaixo da barra de pesquisa lá em cima". Etiquetas no topo (y < 150), carimbos e
// personagens saindo pela direita, BOLETIM e quadro-negro embaixo dos botões e do texto do post na tela cheia.
// A zona (LINHA.md, "Layout e zona segura"):
//   · folha de cima (50/50): x de 40 a 1040, y de 150 a 955 (a barra de busca do TikTok cobre ~120 px de cima);
//   · tela cheia: x de 40 a 1040, y de 150 a 1700 (o nome e o texto do post cobrem de ~1740 para baixo), e entre y 900
//     e 1700 nada passa de x 930 (a coluna de botões do TikTok).
// Só conta o que fica fora por 0,75 s seguidos ou mais: a peça que atravessa a borda no travelling ou entrando voando passa.
// Peça que está inteira fora do quadro (outra cena do chão) não conta, nem os papeizinhos que voam do carimbo (pz…). Conta o
// zoom lento da "respiração" (_vida.js, 3,5% para o centro): ele empurra o que está no topo da cena ~15 px para cima, então
// etiqueta de cena começa em y 45 (tela 200), não em 10. Sai com erro se houver alguma.
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import fs from "node:fs";
// playwright-core: 1º o instalado nesta pasta (`cd <skill>/scripts && npm install playwright-core`), depois o global
// (`npm install -g playwright-core`). O navegador é o Chrome instalado na máquina (channel "chrome"), sem baixar outro.
async function playwright() {
  try { return await import("playwright-core"); } catch {}
  try {
    const raiz = execSync("npm root -g", { encoding: "utf-8" }).trim();
    return await import(pathToFileURL(path.join(raiz, "playwright-core", "index.mjs")).href);
  } catch {}
  console.error("⛔ falta o playwright-core: rode `npm install playwright-core` na pasta scripts/ da skill");
  process.exit(2);
}
const { chromium } = await playwright();

const pasta = path.resolve(process.argv[2]);
const iPasso = process.argv.indexOf("--passo");
const PASSO = iPasso > 0 ? +process.argv[iPasso + 1] : 0.25;
const MIN = 0.75, TOL = 6;
const dur = JSON.parse(fs.readFileSync(path.join(pasta, "assets/tempos.json"), "utf-8")).duracao;

const b = await chromium.launch({ channel: "chrome", headless: true });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.addInitScript(() => { window.__timelines = {}; });
await p.goto("file:///" + path.join(pasta, "index.html").split(path.sep).join("/"));
for (let k = 0; k < 60 && !(await p.evaluate(() => !!(window.__timelines && window.__timelines.main))); k++) await p.waitForTimeout(500);
await p.waitForTimeout(1000);
// a Archivo Black não está instalada no Windows: sem ela o Chrome mede com uma fonte mais estreita e dá ✓ em grito que o
// render (que usa a de verdade) corta na borda (23/10/2026: um grito saiu cortado e outro vídeo tinha 13 peças fora)
await p.addStyleTag({ url: "https://fonts.googleapis.com/css2?family=Archivo+Black&family=IBM+Plex+Mono:wght@700&display=block" });
await p.evaluate(async () => { try { await document.fonts.load('100px "Archivo Black"', "AÇÃO"); await document.fonts.load('700 40px "IBM Plex Mono"', "A"); await document.fonts.ready; } catch (e) {} });
await p.waitForTimeout(500);
if (!(await p.evaluate(() => document.fonts.check('100px "Archivo Black"')))) {
  console.log("⛔ a Archivo Black não carregou (sem internet?): a medida não vale");
  await b.close();
  process.exit(1);
}

const amostras = [];
for (let t = 0; t <= dur; t += PASSO) {
  const fora = await p.evaluate((t) => {
    const tl = window.__timelines.main;
    tl.pause(); tl.seek(t, false);
    const FUNDO = new Set(["mesa", "piso", "mundo", "topo", "leg", "marca", "hud"]);
    const vis = (e) => {
      let op = 1;
      for (let x = e; x && x !== document.body; x = x.parentElement) {
        const cs = getComputedStyle(x);
        if (cs.display === "none" || cs.visibility === "hidden") return 0;
        op *= +cs.opacity;
      }
      return op;
    };
    // a folha da tela cheia cobrindo tudo: a folha de cima não aparece
    const cheias = [...document.querySelectorAll(".cheia")].filter((f) => vis(f) > 0.1);
    const cobre = cheias.some((f) => f.getBoundingClientRect().top < 8);
    const pecas = [...document.querySelectorAll("#mundo [id], .cheia-dentro [id], .reels [id]")]
      .filter((e) => !FUNDO.has(e.id) && !e.closest("[data-fundo]") && !e.querySelector("[id]") && !/^(cena|c)\d+$/.test(e.id) && !/^pz\d+_/.test(e.id));   // pz = os papeizinhos que voam do carimbo (não são informação)
    const out = [];
    for (const e of pecas) {
      const naCheia = !!e.closest(".cheia, .reels");   // o reels de vídeo real usa a zona da tela cheia
      if (!naCheia && cobre) continue;
      if (vis(e) < 0.15) continue;
      // o que desenha: as formas do SVG (fora de defs/clipPath/máscara) e, nos rótulos de HTML, o <span> (a caixa do div
      // do selo/etiqueta é mais larga que o texto)
      const desenhos = [...e.querySelectorAll("path, rect, circle, ellipse, polygon, polyline, line, text, image, span, img")]
        .filter((d) => !d.closest("defs, clipPath, mask, pattern, symbol, marker"));
      let r = null;
      for (const d of desenhos.length ? desenhos : [e]) {
        const q = d.getBoundingClientRect();
        if (q.width < 1 && q.height < 1) continue;
        r = r ? { l: Math.min(r.l, q.left), t: Math.min(r.t, q.top), r: Math.max(r.r, q.right), b: Math.max(r.b, q.bottom) }
              : { l: q.left, t: q.top, r: q.right, b: q.bottom };
      }
      if (!r) continue;
      const Y1 = naCheia ? 1920 : 960;
      if (r.r <= 0 || r.l >= 1080 || r.b <= 0 || r.t >= Y1) continue;           // inteira fora do quadro: outra cena
      // o palco com câmera da tela cheia (imersao.js, 19/10/2026): parte do corpo cortada pela BORDA DA TELA num close é
      // enquadramento, não informação; o que fica dentro da tela (e todo texto do hud) continua valendo
      if (e.closest(".mundoC") && (r.l < -2 || r.r > 1082 || r.t < -2 || r.b > 1922)) continue;
      // zona da TELA desde 23/10/2026 (o TikTok corta até ~100 px de cada lado no celular 20:9/21:9; abas/pesquisa até ~250 px)
      const z = naCheia ? { l: 110, t: 270, r: 970, b: 1700 } : { l: 110, t: 270, r: 970, b: 955 };
      const lados = [];
      if (r.l < z.l) lados.push(["esquerda", z.l - r.l]);
      if (r.r > z.r) lados.push(["direita", r.r - z.r]);
      if (r.t < z.t) lados.push(["em cima", z.t - r.t]);
      if (r.b > z.b) lados.push(["embaixo", r.b - z.b]);
      if (naCheia && r.b > 900 && r.t < 1700 && r.r > 880) lados.push(["nos botões", r.r - 880]);
      const ruins = lados.filter(([, px]) => px > 6);
      if (ruins.length) out.push({ id: e.id, onde: naCheia ? "tela cheia" : "folha", lados: ruins.map(([l, px]) => [l, Math.round(px)]) });
    }
    return out;
  }, t);
  amostras.push({ t, fora });
}
await b.close();

// junta as amostras seguidas de cada peça e fica com o que dura MIN ou mais
const abertos = new Map(), achados = [];
const fecha = (id, ate) => {
  const a = abertos.get(id);
  if (a && ate - a.t0 >= MIN) achados.push({ ...a, t1: ate });
  abertos.delete(id);
};
for (const { t, fora } of amostras) {
  const agora = new Set(fora.map((f) => f.id));
  for (const id of [...abertos.keys()]) if (!agora.has(id)) fecha(id, t);
  for (const f of fora) {
    const a = abertos.get(f.id);
    if (!a) abertos.set(f.id, { id: f.id, t0: t, onde: f.onde, lados: Object.fromEntries(f.lados) });
    else for (const [l, px] of f.lados) a.lados[l] = Math.max(a.lados[l] || 0, px);
  }
}
for (const id of [...abertos.keys()]) fecha(id, dur);
achados.sort((x, y) => x.t0 - y.t0);
for (const a of achados)
  console.log(`⛔ ${a.t0.toFixed(2)}–${a.t1.toFixed(2)} s  ${a.id} (${a.onde}): ` +
    Object.entries(a.lados).map(([l, px]) => `${px} px ${l}`).join(", "));
console.log(achados.length ? `⛔ ${achados.length} peça(s) fora da área de segurança` : "✓ tudo dentro da área de segurança");
process.exit(achados.length ? 1 : 0);
