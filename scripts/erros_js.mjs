// Abre o index.html de um corte no Chrome sem tela e lista os erros de JavaScript. Sai com erro se houver algum além dos
// dois de sempre do arquivo local: o "main" (a janela do HyperFrames não existe fora do render) e o grão bloqueado por CORS.
//   node <skill>/scripts/erros_js.mjs cortes/<slug>/index.html
// Nasceu em 10/10/2026 (C47): um W() que não achava a palavra no próprio bloco quebrou a linha do tempo, o render saiu
// com a cena 0 parada até o fim e só se viu depois. O sonoplastia.py chama este arquivo no fim, antes de todo render.
import path from "node:path";
import { execSync } from "node:child_process";
import { pathToFileURL } from "node:url";
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

const alvo = path.resolve(process.argv[2]);
const b = await chromium.launch({ channel: "chrome", headless: true });
const p = await b.newPage();
const erros = [];
p.on("pageerror", (e) => erros.push(e.message));
p.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });
await p.goto("file:///" + alvo.split(path.sep).join("/"));
await p.waitForTimeout(4000);
await b.close();
const ruins = erros.filter((e) => !/setting 'main'|CORS|ERR_FAILED/.test(e));
for (const e of ruins) console.log("⛔ " + e);
console.log(ruins.length ? `⛔ ${ruins.length} erro(s) de JavaScript: o render sairia quebrado` : "✓ sem erro de JavaScript");
process.exit(ruins.length ? 1 : 0);
