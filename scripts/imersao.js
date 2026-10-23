        // ══════════════════════════════════════════════════════════════════════
        // IMERSÃO: o padrão da animação desde 19/10/2026 (C90). Mickael: "a animação, de fato, a partir de agora, vai ser o
        // nosso produto… o texto, principalmente quando a tela estiver inteira, seja um dos elementos que tem um destaque…
        // não quero que a animação fique parada… e que isso se torna um padrão. Não vai mudar nossa estética".
        // Mesma estética (papel, Archivo Black, fita, carimbo); o que muda é a estrutura:
        //   · manchete(): a ideia da frase em letra grande, cada palavra entrando quando é dita, com marca-texto;
        //   · virada(): a página da tela cheia vira de verdade (uma folha atravessa a tela com sombra);
        //   · vive(): nada fica parado; o objeto balança e respira por baixo das outras animações;
        //   · garraP(): a garra que desce do alto, pega e sobe (o "imposto que tira um pedaço");
        //   · quica(), conta(), barraSobe(), pensando(): queda com quique, número que conta, barra que cresce, os "…";
        //   · raulCheio(): depois da tela cheia, o Raul na TELA INTEIRA por 2–3 s, e a folha de cima desce do alto e o empurra
        //     de volta para a metade de baixo (Mickael, 19/10: "depois da animação que completa a tela inteira, o Raul aparece
        //     por completo por uns 2, 3 segundos… e aí já corta para ele aparecendo apenas na outra metade").
        // ══════════════════════════════════════════════════════════════════════
        const estIm = document.createElement("style");
        estIm.textContent =
          `.manch { font-family: "Archivo Black", sans-serif; line-height: 1.12; color: #1e1b2e; white-space: nowrap; }` +
          `.manch .p { display: inline-block; margin: 0 0.1em; transform-origin: 50% 85%; position: relative; z-index: 1; }` +
          `.manch .hl::before { content: ""; position: absolute; left: -0.1em; right: -0.1em; bottom: 0.06em; height: 0.44em; z-index: -1;` +
          ` background: #f2c230; border-radius: 5px; transform: scaleX(var(--m, 0)); transform-origin: 0 50%; }` +
          `.manch .vm { color: #e5432d; }` +
          `.virada { position: absolute; left: 0; top: -60px; width: 1260px; height: 2040px; z-index: 60; pointer-events: none;` +
          ` background: #efe6d3 url(assets/papel.png) repeat; box-shadow: -34px 0 44px rgba(30,27,46,.30), 34px 0 44px rgba(30,27,46,.22); }`;
        document.head.appendChild(estIm);

        // manchete(pai, id, x, y, w, fs, "O *ESTADO*, COM | E !MAIÚSCULO", bloco, palavraInicial, n, o)
        //   · cada palavra entra no instante em que é DITA: procura a palavra na fala, em ordem, a partir de T(palavraInicial);
        //     "TEXTO=falada" amarra a palavra da tela a outra palavra da fala; a que não acha entra 0,12 s depois da anterior;
        //   · *palavra* = marca-texto amarelo (corre da esquerda); !palavra = vermelho; "|" quebra a linha;
        //   · o.t0 (sem bloco): começa em o.t0, uma palavra a cada o.passo; o.min: nenhuma entra antes disso; o.al: alinhamento.
        function manchete(pai, id, x, y, w, fs, txt, bloco, w0, n0 = 1, o = {}) {
          const toks = txt.split(/\s+/).filter(Boolean);
          const fala = bloco ? D.palavras.filter((p) => p.bloco === bloco) : [];
          let i = bloco ? fala.findIndex((p) => p.s >= W(w0, bloco, n0) - 0.001) : 0, tAnt = bloco ? W(w0, bloco, n0) : o.t0;
          const pal = [];
          let html = "";
          toks.forEach((tk) => {
            if (tk === "|") { html += "<br>"; return; }
            let cls = "p", vis = tk;
            if (/^\*.*\*[,.:?!]*$/.test(vis)) { cls += " hl"; vis = vis.replace(/\*/g, ""); }
            if (vis.startsWith("!")) { cls += " vm"; vis = vis.slice(1); }
            let [mostra, chave] = vis.split("=");
            chave = chave || mostra;
            let t = pal.length ? tAnt + 0.12 : tAnt;
            if (bloco) {
              for (let j = i; j < Math.min(fala.length, i + 4); j++)   // janela curta: "O" não casa com um "o" dito lá na frente
                if (norm(fala[j].w) === norm(chave)) { t = fala[j].s; i = j + 1; break; }
            } else t = pal.length ? tAnt + (o.passo || 0.14) : o.t0;
            t = Math.max(t, o.min || 0, pal.length ? tAnt + 0.06 : 0);   // nunca fora de ordem
            tAnt = t;
            const pid = id + "-" + pal.length;
            pal.push({ pid, t, hl: cls.includes("hl") });
            html += `<span class="${cls}" id="${pid}">${mostra}</span>`;
          });
          const el = rotulo(pai, id, x, y, w, html, "manch", `font-size:${fs}px;text-align:${o.al || "left"}`);
          el.style.zIndex = 8;
          pal.forEach(({ pid, t, hl }, k) => {
            const s = "#" + pid, r = (rnd(k * 7.7 + fs) - 0.5) * 14;
            tl.set(s, { autoAlpha: 0 }, 0);
            if (o.entrada) { o.entrada(s, t, k); return; }
            tl.fromTo(s, { autoAlpha: 1, y: fs * 0.7, scale: 0.35, rotation: r }, { y: 0, scale: 1, rotation: 0, duration: 0.34, ease: "back.out(2.6)", immediateRender: false }, t - 0.08);
            if (hl) {
              tl.fromTo(s, { "--m": 0 }, { "--m": 1, duration: 0.26, ease: "power2.out", immediateRender: false }, t + 0.16);
              tl.fromTo(s, { scale: 1 }, { scale: 1.12, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }, t + 0.3);
            }
          });
          return { el, ids: pal.map((p) => p.pid), tempos: pal.map((p) => p.t) };
        }
        // a manchete sai: as palavras caem uma atrás da outra
        function saiM(m, t) {
          m.ids.forEach((pid, k) => tl.to("#" + pid, { y: 70, rotation: (rnd(k * 3.3) - 0.5) * 30, autoAlpha: 0, duration: 0.24, ease: "power2.in" }, t + k * 0.03));
        }
        // a página da tela cheia vira: uma folha atravessa a tela da direita para a esquerda e, no meio do caminho (quando
        // cobre tudo), o que estava na página some; o que entra depois de t já está na página nova
        function virada(pai, t, ids) {
          const v = document.createElement("div");
          v.className = "virada"; v.dataset.layoutAllowOverflow = "";
          pai.appendChild(v);
          tl.set(v, { autoAlpha: 0, x: 1140 }, 0);
          tl.set(v, { autoAlpha: 1 }, t - 0.36);
          tl.fromTo(v, { x: 1140, rotation: 3 }, { x: -1340, rotation: -2, duration: 0.72, ease: "power2.inOut", immediateRender: false }, t - 0.36);
          tl.set(v, { autoAlpha: 0 }, t + 0.37);
          tl.set(ids.map((i) => "#" + i), { autoAlpha: 0 }, t);
        }
        // nada parado: o desenho (o filho de dentro, para não brigar com aparece/carimba) sobe e desce e balança de leve
        function vive(el, t0, t1 = DUR, amp = 5, rot = 1.6) {
          const b = (typeof el === "string" ? document.querySelector(el) : el).firstElementChild;
          const sem = [...(b.parentElement.id || "x")].reduce((a, c) => a + c.charCodeAt(0), 0);
          const p1 = 1.7 + rnd(sem) * 0.9, p2 = 2.3 + rnd(sem + 1) * 1.1, d = t1 - t0;
          if (d <= 0.3) return;
          tl.fromTo(b, { y: 0 }, { y: -amp, duration: p1 / 2, yoyo: true, repeat: Math.max(1, Math.ceil(d / (p1 / 2))), ease: "sine.inOut", immediateRender: false }, t0);
          tl.fromTo(b, { rotation: -rot }, { rotation: rot, duration: p2 / 2, yoyo: true, repeat: Math.max(1, Math.ceil(d / (p2 / 2))), ease: "sine.inOut", immediateRender: false }, t0);
        }
        // cai do alto e quica no chão (os quiques do bounce.out batem em ~36%, 73% e 91% da duração: é onde vai o som)
        function quica(el, t, alt = 420, dur = 0.7, rot = 0) {
          tl.set(el, { autoAlpha: 0 }, 0);
          tl.fromTo(el, { autoAlpha: 1, y: -alt, rotation: rot }, { y: 0, rotation: 0, duration: dur, ease: "bounce.out", immediateRender: false }, t);
        }
        // a GARRA: cabo que vem de cima da tela, a cabeça com o rótulo e duas garras que abrem e fecham.
        // garraP(pai, id, x, yParada, txt) → { g, desce(t, y, dur), sobe(t, y, dur, levando), abre(t), fecha(t) }
        function garraP(pai, id, x, y0, txt = "IMPOSTO", w = 170) {
          const g = grupo(pai, id, x, y0, w, 190);
          g.style.zIndex = 12;
          const cabo = obj(g, id + "c", w / 2 - 6, -1500, 12, 1510, `<rect x="0" y="0" width="12" height="1510" fill="${C.tinta}"/><rect x="3" y="0" width="3" height="1510" fill="#6b6880"/>`, false, false);
          cabo.dataset.fundo = "";   // o cabo sai do alto da tela de propósito: a área de segurança não conta
          const fs = caber(txt, w - 26, 30);
          obj(g, id + "h", 0, 0, w, 74, `<rect x="3" y="3" width="${w - 6}" height="68" rx="16" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/>` +
            `<rect x="12" y="10" width="${w - 24}" height="14" rx="7" fill="#ff7a6a" opacity=".6"/>` + fT(w / 2, 37 + fs * 0.36, txt, fs, C.claro), true, false);
          const dente = (s) => `<path d="M${s < 0 ? 46 : 8} 4 L${s < 0 ? 16 : 38} 70 Q${s < 0 ? 10 : 44} 98 ${s < 0 ? 40 : 14} 112" fill="none" stroke="${C.tinta}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>` +
            `<path d="M${s < 0 ? 46 : 8} 4 L${s < 0 ? 16 : 38} 70 Q${s < 0 ? 10 : 44} 98 ${s < 0 ? 40 : 14} 112" fill="none" stroke="#9a948a" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>`;
          const e = obj(g, id + "e", 14, 60, 54, 118, dente(-1), false, false), d = obj(g, id + "d", w - 68, 60, 54, 118, dente(1), false, false);
          e.style.transformOrigin = "85% 4%"; d.style.transformOrigin = "15% 4%";
          e.style.zIndex = 1; d.style.zIndex = 1;
          tl.set(g, { autoAlpha: 0, y: -1100 }, 0);
          const G = {
            g,
            desce(t, y, dur = 0.6) { tl.set(g, { autoAlpha: 1 }, t); tl.fromTo(g, { y: -1100 + (y - y0) * 0 }, { y: y - y0, duration: dur, ease: "power2.inOut", immediateRender: false }, t); return G; },
            sobe(t, dur = 0.6, levando = []) {
              tl.to(g, { y: -1100, duration: dur, ease: "power2.in" }, t);
              levando.forEach((l) => tl.to(l, { y: "-=1100", duration: dur, ease: "power2.in" }, t));
              return G;
            },
            abre(t) { tl.to(e, { rotation: 24, duration: 0.18, ease: "back.out(2)" }, t); tl.to(d, { rotation: -24, duration: 0.18, ease: "back.out(2)" }, t); return G; },
            fecha(t) { tl.to(e, { rotation: -6, duration: 0.12, ease: "power3.in" }, t); tl.to(d, { rotation: 6, duration: 0.12, ease: "power3.in" }, t); return G; },
          };
          return G;
        }
        // número que conta (quadros trocados por tl.set: seguro no render); desacelera no fim, como contador de verdade
        function conta(pai, id, x, y, w, h, valores, t, dur, fs, cor = C.tinta) {
          const n = valores.length, ts = valores.map((_, k) => t + dur * (1 - Math.pow(1 - k / Math.max(1, n - 1), 2)));
          return { els: quadros(pai, id, x, y, w, h, valores, ts, dur, fs, cor), ts };
        }
        // barra que cresce de baixo para cima
        function barraSobe(pai, id, x, yBase, w, h, cor, t, dur = 0.6) {
          const b = obj(pai, id, x, yBase - h, w, h, `<path d="${pRet(w, h, id.length * 31 + h, 1.4, 26)}" fill="${cor}" stroke="${C.tinta}" stroke-width="5"/>`, true, false);
          b.style.transformOrigin = "50% 100%";
          tl.set(b, { autoAlpha: 0 }, 0);
          tl.fromTo(b, { autoAlpha: 1, scaleY: 0 }, { scaleY: 1, duration: dur, ease: "power3.out", immediateRender: false }, t);
          return b;
        }
        // os três pontinhos de quem está pensando ("É de uma…")
        function pensando(pai, id, x, y, t0, t1) {
          const n = Math.max(3, Math.round((t1 - t0) / 0.22)), txts = [], ts = [];
          for (let k = 0; k < n; k++) { txts.push([".", "..", "..."][k % 3]); ts.push(t0 + k * 0.22); }
          const bal = pensaT(pai, id + "b", x, y, 170, 120, " ");
          bal.style.zIndex = 8;
          aparece(bal, t0 - 0.1, 0.2, { scale: 0.3, y: 10 });
          tl.to(bal, { autoAlpha: 0, scale: 0.6, duration: 0.15 }, t1);
          const q = quadros(pai, id, x + 25, y + 4, 120, 70, txts, ts, t1 - t0, 54, C.tinta);
          tl.set(q, { autoAlpha: 0 }, t1);
          q.forEach((e) => (e.style.zIndex = 9));
          return bal;
        }
        // O RAUL NA TELA INTEIRA: em tA (a tela cheia começa a descer) a janela do Raul já está do tamanho da tela (o dobro,
        // presa no alto) e a folha de cima está escondida acima; a tela cheia desce e mostra o Raul inteiro, que assenta com um
        // zoom curto. Em tB a folha de cima desce do alto e empurra a janela de volta para a metade de baixo (as duas com a
        // mesma curva: a borda da folha encosta na borda do Raul o caminho todo, sem fresta).
        // legY: no Raul em close o rosto enche o meio da tela; a legenda sobe para cima da cabeça (−420 = y 470–610) e volta
        // quando a folha desce (C91, 19/10: a legenda tampava a testa dele)
        function raulCheio(tA, tB, dx = 72, legY = 0) {
          tl.set("#topo", { y: -990 }, tA - 0.02);
          tl.set("#rasgo", { y: -990, autoAlpha: 0 }, tA - 0.02);
          tl.set("#raul-janela", { y: -960, x: dx, scale: 2, transformOrigin: "50% 0%" }, tA - 0.02);
          tl.fromTo("#raul-janela", { scale: 2.14 }, { scale: 2, duration: 1.0, ease: "power2.out", immediateRender: false }, tA);
          tl.set("#rasgo", { autoAlpha: 1 }, tB);
          tl.to(["#topo", "#rasgo"], { y: 0, duration: 0.55, ease: "power3.inOut" }, tB);
          tl.to("#raul-janela", { y: 0, x: 0, scale: 1, duration: 0.55, ease: "power3.inOut" }, tB);
          // fonte em tela dividida (slide + painel do Raul, C93): a janela ampliada 2× ficaria 3× a fonte, só o rosto e
          // mole. O montar.py põe então o #raul-cheio-cam: o painel INTEIRO a 1,78× (cortar.py com janela 1252×1920), por
          // cima da janela; na descida ele encolhe para o tamanho da janela (data-k) e some quando os dois coincidem. data-y: até
          // onde ele desce (padrão 960); na fonte VERTICAL (C95) é o quadro inteiro 1:1 e desce 960 − y do recorte
          const rc = document.getElementById("raul-cheio-cam");
          if (rc) {
            tl.set(rc, { autoAlpha: 0 }, 0);
            tl.set(rc, { autoAlpha: 1, y: 0, scale: 1, transformOrigin: "50% 0%" }, tA - 0.02);
            tl.fromTo(rc, { scale: 1.06 }, { scale: 1, duration: 1.0, ease: "power2.out", immediateRender: false }, tA);
            tl.to(rc, { y: +(rc.dataset.y || 960), scale: +rc.dataset.k, duration: 0.55, ease: "power3.inOut" }, tB);
            tl.set(rc, { autoAlpha: 0 }, tB + 0.56);
          }
          if (legY) {
            tl.to("#leg", { y: legY, duration: 0.4, ease: "power3.inOut" }, tA - 0.1);
            tl.to("#leg", { y: 0, duration: 0.55, ease: "power3.inOut" }, tB);
          }
          RAUL_CHEIO.push([tA, tB + 0.55]);
        }
        const RAUL_CHEIO = [];

        // ── v2 do padrão (19/10/2026, depois da 1ª prévia: "por mais que a gente use a tela inteira a gente só anima a parte
        // de cima no mesmo lugar que quando tá dividido… repense toda a animação em tela cheia… outro tipo de imersão,
        // interação entre personagens, elementos"). A tela cheia vira um PALCO com CÂMERA: o mundo é maior que a tela, os
        // personagens são grandes (o rosto acima da legenda, o corpo passando por trás dela) e a câmera faz plano aberto, close
        // no rosto, na mão, no objeto e sobe/desce pelo cenário. O texto é o GRITO: palavras grandes, de contorno, que batem
        // na tela quando são ditas, nos espaços livres (alto: y 160–480; baixo: y 1100–1690, x até 920).
        const estIm2 = document.createElement("style");
        estIm2.textContent =
          `.mundoC { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; }` +
          `.mundoC-hud { position: absolute; inset: 0; z-index: 30; pointer-events: none; }` +
          `.grito { font-family: "Archivo Black", sans-serif; line-height: 1.02; color: #f8f2e4; white-space: nowrap; text-align: center;` +
          ` text-shadow: -5px -5px 0 #1e1b2e, 5px -5px 0 #1e1b2e, -5px 5px 0 #1e1b2e, 5px 5px 0 #1e1b2e, 0 -6px 0 #1e1b2e, 0 6px 0 #1e1b2e,` +
          ` -6px 0 0 #1e1b2e, 6px 0 0 #1e1b2e, 10px 12px 0 rgba(30,27,46,.38); }` +
          `.grito .p { display: inline-block; margin: 0 0.12em; transform-origin: 50% 70%; }` +
          `.grito .vm { color: #e5432d; } .grito .am { color: #f2c230; }`;
        document.head.appendChild(estIm2);
        // a TELA CHEIA desce do alto como uma cortina de papel (a borda de baixo rasgada vem na frente) e, no fim, continua
        // descendo e sai por baixo, mostrando o que está atrás (o Raul na tela inteira)
        function telaCheiaI(n, t0, t1) {
          const f = document.createElement("div");
          f.id = "cheia" + n; f.className = "cheia"; f.dataset.layoutAllowOverflow = "";
          f.style.height = "1964px";
          f.innerHTML = `<div class="cheia-papel"></div><div class="cheia-grao"></div>`;
          const P = [], Q = [];
          for (let x = 0; x <= 1080; x += 27) P.push(`${x}px ${(5 + rnd(x * 1.7 + n * 31) * 15).toFixed(1)}px`);
          for (let x = 1080; x >= 0; x -= 27) Q.push(`${x}px ${(1960 - 5 - rnd(x * 2.3 + n * 17) * 15).toFixed(1)}px`);
          f.style.clipPath = `polygon(${P.join(", ")}, ${Q.join(", ")})`;
          raiz.insertBefore(f, document.querySelector("#leg"));
          const dentro = document.createElement("div");
          dentro.className = "cheia-dentro"; dentro.dataset.layoutAllowOverflow = "";
          f.appendChild(dentro);
          tl.set(f, { autoAlpha: 0, y: -1990 }, 0);
          tl.set(f, { autoAlpha: 1 }, t0 - 0.55);
          tl.fromTo(f, { y: -1990 }, { y: 0, duration: 0.55, ease: "power3.out", immediateRender: false }, t0 - 0.55);
          tl.to(f, { y: 1990, duration: 0.5, ease: "power2.in" }, t1);
          tl.set(f, { autoAlpha: 0 }, t1 + 0.5);
          tl.to("#marca", { autoAlpha: 0, duration: 0.2 }, t0 - 0.5);
          tl.to("#marca", { autoAlpha: 0.8, duration: 0.3 }, t1 + 0.42);
          // REGRA (Mickael, 22/10/2026): sem a legenda do meio na tela cheia ("a legenda já está aparecendo durante a animação
          // compondo a cena": os gritos). Ela some quando a cortina desce e volta quando a cortina sai (Raul cheio e folha
          // dividida têm legenda). Fala que importa e não tem grito vira balão (fala()) na própria cena.
          tl.to("#leg", { autoAlpha: 0, duration: 0.2 }, t0 - 0.45);
          tl.to("#leg", { autoAlpha: 1, duration: 0.2 }, t1);
          FULL.push([t0 - 0.55, t1 + 0.5]);
          return dentro;
        }
        // o palco com câmera: { w: o mundo (coordenadas livres, maior que a tela), hud: a camada fixa da tela (os gritos) }
        function mundoC(dentro, id) {
          const w = document.createElement("div");
          w.id = id; w.className = "mundoC"; w.dataset.layoutAllowOverflow = "";
          dentro.appendChild(w);
          const hud = document.createElement("div");
          hud.id = id + "hud"; hud.className = "mundoC-hud"; hud.dataset.layoutAllowOverflow = "";
          dentro.appendChild(hud);
          return { w, hud };
        }
        // a trilha da câmera: [[t, px, py, zoom, qx, qy, dur, ease]]: em t a câmera leva o ponto (px, py) do mundo para (qx, qy)
        // da tela; entre um plano e o próximo ela aproxima 3,5% devagar (nada parado)
        function camTrilha(w, L) {
          L.forEach(([t, px, py, s, qx = 540, qy = 960, dur = 0.7, ease = "power3.inOut"], i) => {
            const v = (z) => ({ x: qx - px * z, y: qy - py * z, scale: z });
            if (dur <= 0) tl.set(w, v(s), t); else tl.to(w, Object.assign(v(s), { duration: dur, ease }), t);
            const ini = t + Math.max(dur, 0), d = (i + 1 < L.length ? L[i + 1][0] : ini + 4) - ini;
            if (d > 0.6) tl.to(w, Object.assign(v(s * 1.035), { duration: d, ease: "sine.inOut" }), ini);
          });
        }
        // o GRITO: como a manchete (cada palavra quando é dita; *amarela*, !vermelha, "|" quebra), mas a palavra BATE: entra
        // grande e girada, assenta com mola, e fica viva (sobe e desce de leve) até sair
        function grito(pai, id, y, fs, txt, bloco, w0, n0 = 1, o = {}) {
          const bate = (sel, t, k) => {
            const r = (rnd(k * 4.1 + fs) - 0.5) * 30;
            tl.set(sel, { autoAlpha: 1 }, t - 0.06);   // a visibilidade num set próprio: no render (19/10) a 1ª palavra de um grito sumia
            tl.fromTo(sel, { scale: 2.5, rotation: r, y: -fs * 0.3 }, { scale: 1, rotation: 0, y: 0, duration: 0.26, ease: "back.out(2.2)", immediateRender: false }, t - 0.06);
            tl.fromTo(sel, { y: 0 }, { y: -6, duration: 0.7 + rnd(k) * 0.3, yoyo: true, repeat: 15, ease: "sine.inOut", immediateRender: false }, t + 0.3);
          };
          const m = manchete(pai, id, o.x ?? 60, y, o.w ?? 960, fs, txt.replace(/\*([^*\s]+)\*/g, "§$1§"), bloco, w0, n0, Object.assign({ al: "center", entrada: bate }, o));
          m.el.className = "o grito";
          m.ids.forEach((pid) => {
            const sp = document.getElementById(pid);
            if (sp.textContent.includes("§")) { sp.textContent = sp.textContent.replace(/§/g, ""); sp.classList.add("am"); }
          });
          return m;
        }
        const saiG = (m, t) => m.ids.forEach((pid, k) => tl.to("#" + pid, { scale: 0, rotation: (rnd(k * 2.7) - 0.5) * 60, autoAlpha: 0, duration: 0.2, ease: "back.in(2)" }, t + k * 0.03));
        // tremor de qualquer camada (o treme() da base só sacode a folha de cima)
        function sacode(sel, t, amp = 14, dur = 0.32, seed = 1) {
          const n = Math.max(2, Math.round(dur * 24));
          tl.fromTo(sel, { x: 0, y: 0 }, { x: amp, y: amp * 0.6, duration: dur, immediateRender: false,
            ease: (p) => (p >= 1 ? 0 : (rnd(seed * 31 + Math.floor(p * n)) * 2 - 1) * (1 - p)) }, t);
        }
