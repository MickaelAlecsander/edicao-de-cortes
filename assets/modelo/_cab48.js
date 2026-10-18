
        // ── ajudantes do C48 (a base é o C47) ─────────────────────────────────
        const tg = (c, id, x, y, w, txt, cls, fs) => rotulo(c, id, x, y, w, `<span>${txt}</span>`, cls, `font-size:${fs}px`);
        const est = document.createElement("style");
        est.textContent = `.tagg > span { color: #f8f2e4; } .tagg > span::before { background: ${VERDE}; }` +
          `.tagc > span { color: #f8f2e4; } .tagc > span::before { background: ${CINZA}; }` +
          // o que entra subindo nasce do chão: abaixo da borda da frente do palco (y 650) a cena é cortada, e nada passa pela
          // faixa da legenda (C44; era 668 com o chão de linha)
          `.cena { clip-path: inset(-700px -700px 150px -700px); }` +
          // O CHÃO FIXO (Mickael, 12/10/2026: "o chão não vai sair como se fosse uma coisa quebrada… deixa o chão fixo… hoje
          // ela é só uma linha"). Era uma linha por cena, e no recuo da câmera cada pedaço aparecia solto, numa altura. Agora
          // é um palco de papel só, no mundo, por baixo de todas as cenas: o tampo claro (560–650, o pé dos bonecos fica em
          // ~593) e a frente em kraft. Só tem traço na horizontal, e a câmera só anda na horizontal (o vai() do montar.py):
          // o chão é igual em todo x, então na troca de cena ele fica parado na tela, e só o que está em cima dele anda.
          `#piso { position: absolute; left: -6000px; top: 556px; width: 46000px; height: 700px; pointer-events: none;` +
          ` background:` +
          ` linear-gradient(to bottom, transparent 30px, rgba(30,27,46,.05) 30px, rgba(30,27,46,.05) 32px, transparent 32px,` +
          ` transparent 62px, rgba(30,27,46,.06) 62px, rgba(30,27,46,.06) 64px, transparent 64px),` +
          ` linear-gradient(to bottom, rgba(30,27,46,.3) 0, rgba(30,27,46,.3) 3px, #e8dcc2 3px, #e1d2b2 94px,` +
          ` rgba(30,27,46,.62) 94px, rgba(30,27,46,.62) 99px, #bba179 99px, #cdb78f 116px, #d6c3a0 150px, #d6c3a0 100%); }`;
        document.head.appendChild(est);
        const miudo = (c, id, x, y, w, txt, fs = 24) => rotulo(c, id, x, y, w, `<span>${txt}</span>`, "rotl", `font-size:${fs}px`);
        const entra = (el, t) => aparece(el, t, 0.22, { scale: 0.3, y: 10 });
        const sai = (els, t) => some(els, t, 0.22, { y: 100, scale: 0.6 });
        const pulsa = (el, t, s = 1.08) => tl.fromTo(el, { scale: 1 }, { scale: s, duration: 0.14, yoyo: true, repeat: 1, ease: S(0.14, "power2.out"), immediateRender: false }, t);
        const selo = (c, id, x, y, w, txt, fs, cls = "selo") => { const s = rotulo(c, id, x, y, w, `<span>${txt}</span>`, cls, `font-size:${fs}px`); s.style.zIndex = 5; return s; };
        function figura(c, id, x, y, tipo, nome, cls, t, expr = "neutro", w = 180, de = { y: 420, scale: 1 }) {
          const p = personagem(c, id, x, y, w, tipo, { expr });
          const k = w / 180;
          aparece(p, t, 0.3, de);
          let e = null;
          if (nome) {
            e = tg(c, id + "t", x - 22 * k, y + 228 * k, 230 * k, nome, "tag " + cls, Math.min(34, caber(nome, 230, 34)) * k);
            entra(e, t + 0.2);
          }
          return { p, e };
        }
        // o palco fica logo acima da mesa (o papel de fundo) e abaixo de todas as cenas; chao() de cada cena virou nada, para
        // as cenas antigas montarem sem mudar
        const piso = document.createElement("div");
        piso.id = "piso"; piso.dataset.layoutAllowOverflow = "";
        mundo.insertBefore(piso, $("#mesa").nextSibling);
        const chao = () => {};
        const T = (w, b, n = 1) => W(w, b, n);
        const xis = (c, id, x, y, t, s = 120) => { const v = obj(c, id, x, y, s, s, xisN(s), false, false); aparece(v, t, 0.2, { scale: 2, y: 0, rotation: 20 }); return v; };
        const pergunta = (c, id, x, y, t, s = 100) => { const q = obj(c, id, x, y, s, s, interroN(s), false, false); aparece(q, t, 0.22, { scale: 2, y: 0, rotation: -15 }); return q; };
        const cartaoG = (w, h, txt, cor = C.claro) => {
          const ls = txt.split("|"), fs = Math.min(...ls.map((l) => caber(l, w - 24, 32)));
          return `<path d="${pRet(w, h, 4600 + txt.length * 17, 1.3, 30)}" fill="${cor}" stroke="${C.tinta}" stroke-width="5"/>` +
            ls.map((l, k) => fT(w / 2, h / 2 + fs * 0.36 + (k - (ls.length - 1) / 2) * fs * 1.08, l, fs, C.tinta)).join("");
        };
        function voa(c, id, x, y, dx, dy, t, d = 56) {
          const m = obj(c, id, x, y, d, d, moedaN(d), false, false);
          aparece(m, t, 0.12, { scale: 0.3, y: 0 });
          tl.to(m, { x: dx, duration: 0.5, ease: S(0.5, "none") }, t + 0.1);
          tl.to(m, { y: dy - 110, duration: 0.22, ease: S(0.22, "power2.out") }, t + 0.1);
          tl.to(m, { y: dy, rotation: 300, duration: 0.28, ease: S(0.28, "power2.in") }, t + 0.32);
          tl.set(m, { autoAlpha: 0 }, t + 0.62);
          return m;
        }
        const balaoT = (c, id, x, y, w, h, txt, lado = 1) => {
          const ls = txt.split("|"), fs = Math.min(...ls.map((l) => caber(l, w - 40, 40)));
          return obj(c, id, x, y, w, h, balaoFala(w, h, lado) + ls.map((l, k) => fT(w / 2, h * 0.4 + fs * 0.36 + (k - (ls.length - 1) / 2) * fs * 1.1, l, fs, C.tinta)).join(""), true, false);
        };
        // balão de pensamento: a nuvem clara e duas bolinhas descendo para a cabeça (à esquerda, embaixo)
        const pensaT = (c, id, x, y, w, h, txt) => {
          const ls = txt.split("|"), fs = Math.min(...ls.map((l) => caber(l, w * 0.74, 36)));
          return obj(c, id, x, y, w, h, nuvem(w, h * 0.78, C.claro) +
            `<circle cx="${w * 0.24}" cy="${h * 0.86}" r="${h * 0.06}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<circle cx="${w * 0.15}" cy="${h * 0.96}" r="${h * 0.035}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>` +
            ls.map((l, k) => fT(w / 2, h * 0.46 + fs * 0.36 + (k - (ls.length - 1) / 2) * fs * 1.1, l, fs, C.tinta)).join(""), true, false);
        };
        // chacoalha um elemento no lugar (o boneco que fica bravo), sem mexer na câmera
        const chacoalha = (el, t, amp = 9) => {
          tl.fromTo(el, { x: -amp }, { x: amp, duration: 0.05, yoyo: true, repeat: 5, ease: "none", immediateRender: false }, t);
          tl.set(el, { x: 0 }, t + 0.31);
        };
        // ── desenhos novos do C48 ─────────────────────────────────────────────
        // o celular do aplicativo (a moto de entrega na tela) e o do CLT (a carteira de trabalho na tela); embaixo fica o
        // espaço do contador (y ≈ 0,74 h)
        function appTela(w, h, txt = "APP") {
          const mw = w * 0.66, mh = mw * 0.64, fs = caber(txt, w * 0.7, w * 0.2);
          return celular(w, h, "#fde8e2") + `<g transform="translate(${(w - mw) / 2} ${h * 0.16})">${moto(mw, mh)}</g>` + fT(w / 2, h * 0.16 + mh + fs, txt, fs, C.verm);
        }
        function cltTela(w, h, txt = "CLT") {
          const cw = w * 0.5, chh = cw * 1.3, fs = caber(txt, w * 0.7, w * 0.2);
          return celular(w, h, "#e3ebf6") + `<g transform="translate(${(w - cw) / 2} ${h * 0.14})">${ctps(cw, chh)}</g>` + fT(w / 2, h * 0.14 + chh + fs, txt, fs, C.azul2);
        }
        // livro: velho = capa amarelada, teia de aranha no canto e poeira (a lei que não evoluiu)
        function livroN(w, h, txt, velho = false) {
          const capa = velho ? "#c9b27a" : C.azul2, lomb = velho ? "#a8905c" : C.tinta, fs = caber(txt, w * 0.62, h * 0.13);
          let s = `<rect x="${w * 0.04}" y="${h * 0.03}" width="${w * 0.92}" height="${h * 0.94}" rx="12" fill="${capa}" stroke="${C.tinta}" stroke-width="5"/>` +
            `<rect x="${w * 0.04}" y="${h * 0.03}" width="${w * 0.13}" height="${h * 0.94}" rx="8" fill="${lomb}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<rect x="${w * 0.25}" y="${h * 0.3}" width="${w * 0.64}" height="${h * 0.22}" rx="6" fill="${velho ? "#e8dcb8" : C.claro}" stroke="${C.tinta}" stroke-width="3"/>` +
            fT(w * 0.57, h * 0.41 + fs * 0.36, txt, fs, C.tinta);
          if (velho) {
            const cx = w * 0.955, cy = h * 0.035, r = w * 0.38, A = [0, 1, 2, 3, 4].map((k) => Math.PI / 2 + (k * Math.PI) / 8);
            A.forEach((a) => (s += `<path d="M${cx} ${cy} L${cx + Math.cos(a) * r} ${cy + Math.sin(a) * r}" stroke="#f4f0e6" stroke-width="2.5"/>`));
            [0.35, 0.65, 0.95].forEach((f) => (s += `<path d="${A.map((a, k) => (k ? "L" : "M") + (cx + Math.cos(a) * r * f).toFixed(1) + " " + (cy + Math.sin(a) * r * f).toFixed(1)).join(" ")}" fill="none" stroke="#f4f0e6" stroke-width="2"/>`));
            for (let k = 0; k < 16; k++) s += `<circle cx="${(w * (0.22 + rnd(k * 7.3) * 0.68)).toFixed(1)}" cy="${(h * (0.58 + rnd(k * 3.1) * 0.36)).toFixed(1)}" r="${(2 + rnd(k) * 3).toFixed(1)}" fill="#7a6644" opacity=".5"/>`;
          }
          return s;
        }
        // a mira vermelha (quem ele acha que é o inimigo)
        const miraN = (s) => `<circle cx="${s / 2}" cy="${s / 2}" r="${s * 0.4}" fill="none" stroke="${C.verm}" stroke-width="${s * 0.06}"/>` +
          `<circle cx="${s / 2}" cy="${s / 2}" r="${s * 0.17}" fill="none" stroke="${C.verm}" stroke-width="${s * 0.05}"/>` +
          [[0.5, 0, 0.5, 0.3], [0.5, 0.7, 0.5, 1], [0, 0.5, 0.3, 0.5], [0.7, 0.5, 1, 0.5]].map(([a, b, c, d]) => `<path d="M${s * a} ${s * b} L${s * c} ${s * d}" stroke="${C.verm}" stroke-width="${s * 0.06}" stroke-linecap="round"/>`).join("");
        // guarda-chuva aberto com o texto na copa (o cabo curto: acaba acima da cabeça de quem está embaixo)
        function guardaChuvaN(w, h, txt) {
          const cy = h * 0.5, fs = caber(txt, w * 0.6, h * 0.16);
          let d = `M0 ${cy} A${w / 2} ${cy * 0.95} 0 0 1 ${w} ${cy}`;
          for (let k = 3; k >= 0; k--) d += ` Q${(w * (k + 0.5)) / 4} ${cy - h * 0.09} ${(w * k) / 4} ${cy}`;
          return `<path d="M${w / 2} ${cy} L${w / 2} ${h * 0.86} Q${w / 2} ${h * 0.98} ${w * 0.42} ${h * 0.96}" fill="none" stroke="${C.tinta}" stroke-width="${w * 0.03}" stroke-linecap="round"/>` +
            `<path d="${d} Z" fill="${C.azul}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
            [1, 2, 3].map((k) => `<path d="M${w / 2} ${h * 0.04} Q${(w * k) / 4} ${cy * 0.3} ${(w * k) / 4} ${cy}" fill="none" stroke="${C.azul2}" stroke-width="3"/>`).join("") +
            `<rect x="${w / 2 - 5}" y="0" width="10" height="${h * 0.06}" rx="4" fill="${C.tinta}"/>` + fT(w / 2, cy * 0.72, txt, fs, C.claro);
        }
        // faixa quadriculada da largada
        const xadrezN = (w, h) => {
          let s = "";
          const q = h / 2, n = Math.ceil(w / q);
          for (let r = 0; r < 2; r++) for (let k = 0; k < n; k++) s += `<rect x="${k * q}" y="${r * q}" width="${q}" height="${q}" fill="${(k + r) % 2 ? C.claro : C.tinta}"/>`;
          return s + `<rect x="2" y="2" width="${w - 4}" height="${h - 4}" fill="none" stroke="${C.tinta}" stroke-width="4"/>`;
        };
        // a pilha de carteiras de trabalho (de lado) com uma de frente em cima
        function pilhaCtps(w, h, n = 7) {
          const sh = h * 0.07;
          let s = "";
          for (let k = 0; k < n; k++) {
            const y = h - (k + 1) * sh, dx = (rnd(k * 5.1) - 0.5) * w * 0.06;
            s += `<rect x="${(w * 0.05 + dx).toFixed(1)}" y="${y.toFixed(1)}" width="${w * 0.9}" height="${sh}" rx="4" fill="${k % 2 ? "#2a4f8a" : "#234478"}" stroke="${C.tinta}" stroke-width="3"/>`;
          }
          const tw = w * 0.62, th = Math.min(h - n * sh, tw * 1.35);
          return s + `<g transform="translate(${(w - tw) / 2} ${h - n * sh - th})">${ctps(tw, th)}</g>`;
        }
        // a balança que pende: a haste fica, a travessa (com os dois pratos) gira no centro de cima
        const hasteN = (w, h) => `<rect x="${w / 2 - 14}" y="0" width="28" height="${h - 22}" fill="${C.tinta}"/><rect x="${w * 0.2}" y="${h - 26}" width="${w * 0.6}" height="26" rx="8" fill="${C.tinta}"/>`;
        function travessaN(w, h) {
          const prato = (cx) => `<path d="M${cx} 14 L${cx - 62} ${h - 30} M${cx} 14 L${cx + 62} ${h - 30}" stroke="${C.tinta}" stroke-width="3"/>` +
            `<path d="M${cx - 82} ${h - 30} L${cx + 82} ${h - 30} Q${cx} ${h + 4} ${cx - 82} ${h - 30} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>`;
          return prato(70) + prato(w - 70) + `<rect x="0" y="4" width="${w}" height="20" rx="8" fill="${C.tinta}"/><circle cx="${w / 2}" cy="14" r="14" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>`;
        }
        // os personagens (TIPO, nunca a cara de ninguém)
        const ALUNO1 = Object.assign({}, TIPO.jovem, { roupa: C.amar, corCabelo: C.azul });
        const ALUNO2 = Object.assign({}, TIPO.jovem, { roupa: C.azul, cabelo: "curto", corCabelo: "#2a1d14", pele: PELE[0] });
        const ENTREGADOR = Object.assign({}, TIPO.jovem, { roupa: C.verm, calca: C.tinta, corCabelo: C.tinta, pele: PELE[2] });
        const TRAB_CLT = Object.assign({}, TIPO.trabalhador, { capacete: false, cabelo: "curto", corCabelo: "#2a1d14" });

        const VERDE_ = "#3c9a4f", GIZ = "#e9efe6";
        const estV2 = document.createElement("style");
        estV2.textContent = `.tagg > span { color: #f8f2e4; } .tagg > span::before { background: ${VERDE_}; }`;
        document.head.appendChild(estV2);
        const PROF = Object.assign({}, TIPO.trabalhador, { capacete: false, roupa: "#7a5c3e", calca: "#3a3848", cabelo: "curto", corCabelo: "#2a1d14", oculos: true, pele: PELE[1] });
        const ENTREG = Object.assign({}, TIPO.jovem, { roupa: "#2a2838", calca: "#3a3848", cabelo: "bone", corCabelo: C.verm, pele: PELE[2] });
        const PEQ = Object.assign({}, TIPO.trabalhador, { capacete: false, roupa: C.verm2, calca: "#3a3848", cabelo: "grisalho", corCabelo: "#8d8a96", pele: PELE[2] });
        const KP = 0.9, TOPO = 240;                       // personagem de 180: o pé fica em ~593
        const pesY = (y = TOPO, w = 180) => y + 392 * (w / 200);
        // etiqueta com o nome embaixo do personagem (entre o pé e o chão, acima do corte da cena em 668). A etiqueta tem letra
        // de no mínimo 28 px (CSS da legenda v2): o centro se afasta da borda para o nome nunca sair cortado
        const nomeP = (c, id, x, t, txt, cls, w = 180, y = TOPO, lw = 240) => {
          const fs = Math.min(30, caber(txt, lw - 30, 30)), meia = (Math.max(28, fs) * 0.92 * txt.length) / 2 + 34;
          const cx = Math.min(Math.max(x + w / 2, meia + 40), 1040 - meia);   // área de segurança (17/10/2026): a etiqueta fica entre x 40 e 1040
          const e = tg(c, id, cx - lw / 2, pesY(y, w) + 6, lw, txt, "tag " + cls, fs);
          entra(e, t);
          return e;
        };
        const brotaP = (el, t, dur = 0.3) => aparece(el, t, dur, { y: 420, scale: 1 });
        // o ENTREGADOR em pé: a bag APP atrás dos ombros, o boneco e o "APP" no peito (três peças que andam juntas)
        const bagN = (w, h) => `<rect x="3" y="3" width="${w - 6}" height="${h - 6}" rx="14" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/><rect x="3" y="3" width="${w - 6}" height="${h * 0.14}" rx="10" fill="${C.verm2}"/>`;
        function entregador(c, id, x, t, expr = "neutro", w = 180, y = TOPO) {
          const k = w / 200;
          const bag = obj(c, id + "B", x + 22 * k, y + 64 * k, 156 * k, 190 * k, bagN(156 * k, 190 * k), true, false);
          personagem(c, id, x, y, w, ENTREG, { expr });
          const peito = obj(c, id + "T", x + 66 * k, y + 196 * k, 68 * k, 36 * k, `<rect x="2" y="2" width="${68 * k - 4}" height="${36 * k - 4}" rx="6" fill="${C.verm}" stroke="${C.claro}" stroke-width="2"/>${fT(34 * k, 26 * k, "APP", 22 * k, C.claro)}`, false, false);
          [bag, "#" + id, peito].forEach((e) => brotaP(e, t));
          return { bag, peito };
        }
        const andaE = (id, t, dur, dx) => [id, id + "B", id + "T"].forEach((i) => andaP(i, t, dur, dx));
        const someE = (id, t) => sai(["#" + id, "#" + id + "B", "#" + id + "T"], t);
        // um objeto na mão do personagem (a mão direita "d" ou esquerda "e" com o braço erguido ~ang): posição aproximada
        const maoP = (x, lado, ang, w = 180, y = TOPO) => {
          const k = w / 200, sx = lado === "d" ? 148 : 52, sy = 170, r = (ang * Math.PI) / 180, s = lado === "d" ? 1 : -1;
          return { x: x + (sx + s * Math.sin(r) * 118) * k, y: y + (sy + Math.cos(r) * 118) * k };
        };
        // a MOTO com o entregador montado (de lado, virada para a direita): a bag APP, o capacete vermelho, a jaqueta escura
        const MW = 330, MH = 250;
        const motoCorpoN = () =>
          `<rect x="6" y="52" width="112" height="104" rx="10" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<rect x="6" y="52" width="112" height="22" rx="8" fill="${C.verm2}" stroke="${C.tinta}" stroke-width="4"/>${fT(62, 128, "APP", 38, C.claro)}` +
          `<rect x="58" y="196" width="96" height="14" rx="7" fill="#9a948a" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M34 176 Q40 160 70 158 L206 160 L214 186 L150 198 L70 196 Q38 194 34 176 Z" fill="#4a4858" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<path d="M92 150 L186 150 Q198 152 198 162 L94 164 Q86 158 92 150 Z" fill="${C.tinta}"/>` +
          `<path d="M184 162 Q196 128 232 132 L252 160 L206 172 Z" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<rect x="128" y="176" width="70" height="38" rx="8" fill="#6b6880" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M246 120 L270 212" stroke="${C.tinta}" stroke-width="12" stroke-linecap="round"/>` +
          `<path d="M232 190 Q268 162 304 190" fill="none" stroke="${C.tinta}" stroke-width="9" stroke-linecap="round"/>` +
          `<circle cx="266" cy="136" r="13" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M238 112 L262 102" stroke="${C.tinta}" stroke-width="9" stroke-linecap="round"/>`;
        const pilotoN = () =>
          `<path d="M140 146 L204 150" stroke="#3a3848" stroke-width="30" stroke-linecap="round"/><path d="M204 150 L196 198" stroke="#3a3848" stroke-width="26" stroke-linecap="round"/>` +
          `<path d="M180 192 L222 192 Q230 206 216 210 L180 210 Z" fill="#3a2a20"/>` +
          `<path d="M118 150 L170 152 L198 86 Q194 62 170 60 L150 60 Q128 64 124 88 Z" fill="#2a2838" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          `<path d="M178 80 L214 104 L246 108" fill="none" stroke="#2a2838" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>` +
          `<circle cx="248" cy="108" r="11" fill="${C.tinta}"/><circle cx="178" cy="36" r="37" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="M148 22 Q176 2 204 18" fill="none" stroke="${C.claro}" stroke-width="7" stroke-linecap="round"/>` +
          `<path d="M182 22 Q220 18 220 42 Q220 66 184 64 Z" fill="${PELE[2]}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<circle cx="204" cy="37" r="4" fill="${C.tinta}"/><path d="M197 49 Q205 60 213 49" stroke="${C.tinta}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`;
        const rodaM = () => `<circle cx="38" cy="38" r="36" fill="${C.tinta}"/><circle cx="38" cy="38" r="17" fill="#b9b5c2" stroke="${C.tinta}" stroke-width="3"/><rect x="35" y="6" width="6" height="18" rx="3" fill="#b9b5c2"/>`;
        function motoP(c, id, x, y, comPiloto = true) {
          const g = grupo(c, id, x, y, MW, MH);
          obj(g, id + "c", 0, 0, MW, MH, motoCorpoN() + (comPiloto ? pilotoN() : ""), true, false);
          const r = [obj(g, id + "r1", 37, 174, 76, 76, rodaM(), false, false), obj(g, id + "r2", 232, 174, 76, 76, rodaM(), false, false)];
          r.forEach((e) => (e.style.transformOrigin = "50% 50%"));
          return { g, r };
        }
        const rola = (m, t, dur, dx) => {
          tl.to(m.g, { x: "+=" + dx, duration: dur, ease: S(dur, "power2.out") }, t);
          tl.to(m.r, { rotation: "+=" + (dx / (Math.PI * 72)) * 360, duration: dur, ease: S(dur, "power2.out") }, t);
        };
        const tagM = (c, id, x, y, txt, t, dur, cls = "tag tagv") => { const e = tg(c, id, x, y, 170, txt, cls, caber(txt, 150, 40)); entra(e, t); tl.set(e, { autoAlpha: 0 }, t + dur); return e; };

