        const TOTAL = 2;
        const caber = (txt, w, max) => Math.max(12, Math.min(max, Math.floor((w - 24) / (Math.max(1, txt.length) * 0.78))));
        // texto que troca por quadros prontos (tl.set, seguro para o render)
        function quadros(pai, id, x, y, w, h, txts, t, dur, fs, cor) {
          const n = txts.length;
          const els = txts.map((v, k) => {
            const el = obj(pai, id + "-" + k, x, y, w, h, fT(w / 2, h / 2 + fs * 0.36, v, fs, cor), false, false);
            tl.set(el, { autoAlpha: 0 }, 0);
            return el;
          });
          // t pode ser a lista de instantes (um por quadro), presos às palavras
          const em = (k) => (Array.isArray(t) ? t[k] : t + (dur * k) / n);
          els.forEach((el, k) => {
            tl.set(el, { autoAlpha: 1 }, em(k));
            if (k < n - 1) tl.set(el, { autoAlpha: 0 }, em(k + 1));
          });
          return els;
        }
        const estrela = (r, cor) => `<path d="M${r} 0 L${r * 1.25} ${r * 0.75} L${r * 2} ${r} L${r * 1.25} ${r * 1.25} L${r} ${r * 2} L${r * 0.75} ${r * 1.25} L0 ${r} L${r * 0.75} ${r * 0.75} Z" fill="${cor}"/>`;

        // ── desenhos do C20 ───────────────────────────────────────────────────
        const celular = (w, h, tela = C.claro) => `<rect width="${w}" height="${h}" rx="${w * 0.12}" fill="${C.tinta}"/><rect x="${w * 0.06}" y="${h * 0.07}" width="${w * 0.88}" height="${h * 0.84}" rx="${w * 0.05}" fill="${tela}"/><rect x="${w * 0.38}" y="${h * 0.028}" width="${w * 0.24}" height="${h * 0.016}" rx="3" fill="${C.claro}" opacity=".35"/>`;
        // as três janelas do caça-níquel dentro da tela do celular de w × h: [x, y, largura, altura]
        const celula = (w, h, k) => [w * 0.06 + w * 0.88 * 0.06 + k * w * 0.88 * 0.31, h * 0.34, w * 0.88 * 0.26, h * 0.19];
        function appBet(w, h) {
          const x0 = w * 0.06, y0 = h * 0.07, tw = w * 0.88, fb = caber("BET", tw, 46), fa = caber("APOSTAR", tw * 0.76, 30);
          return `<rect x="${x0}" y="${y0}" width="${tw}" height="${h * 0.15}" fill="${C.verm}"/>${fT(w / 2, y0 + h * 0.075 + fb * 0.36, "BET", fb, C.claro)}` +
            [0, 1, 2].map((k) => { const [x, y, cw, ch] = celula(w, h, k); return `<rect x="${x}" y="${y}" width="${cw}" height="${ch}" rx="8" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>`; }).join("") +
            `<rect x="${x0 + tw * 0.12}" y="${h * 0.66}" width="${tw * 0.76}" height="${h * 0.11}" rx="${h * 0.05}" fill="${C.amar}"/>${fT(w / 2, h * 0.715 + fa * 0.36, "APOSTAR", fa, C.tinta)}`;
        }
        // rolo do caça-níquel: os símbolos trocam por quadros e param no "fim"
        function rolo(pai, id, x, y, w, h, t0, t1, fim, seed) {
          const SIM = ["7", "$", "%"], fs = caber("7", w, 56);
          const els = SIM.map((s, k) => {
            const e = obj(pai, `${id}-${k}`, x, y, w, h, fT(w / 2, h / 2 + fs * 0.36, s, fs, k ? C.tinta : C.verm), false, false);
            tl.set(e, { autoAlpha: 0 }, 0);
            return e;
          });
          let ult = -1;
          const mostra = (k, t) => { if (ult >= 0) tl.set(els[ult], { autoAlpha: 0 }, t); tl.set(els[k], { autoAlpha: 1 }, t); ult = k; };
          let n = 0;
          for (let t = t0; t < t1; t += 0.09) mostra((n++ + seed) % 3, t);
          mostra(fim, t1);
        }
        // placa de protesto: a tábua em cima, o cabo embaixo (atrás da cabeça de quem segura)
        function placa(w, h, l1, l2) {
          const hb = h * 0.6, fs = Math.min(caber(l1, w, 44), caber(l2, w, 44));
          return `<rect x="${w / 2 - 7}" y="${hb - 6}" width="14" height="${h - hb + 6}" fill="${C.kraft2}"/><path d="${pRet(w, hb, Math.round(w * 7 + h), 1.6, 26)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
            fT(w / 2, hb / 2 - fs * 0.12, l1, fs, C.verm) + fT(w / 2, hb / 2 + fs * 0.92, l2, fs, C.tinta);
        }
        function folhinha(w, h, mes, dia, sem) {
          const fm = caber(mes, w, 34), fd = Math.min(h * 0.42, caber(dia, w, 140)), fs = caber(sem, w, 30);
          return `<path d="${pRet(w, h, 77, 1.6, 30)}" fill="${C.claro}"/><rect width="${w}" height="${h * 0.24}" fill="${C.verm}"/>${fT(w / 2, h * 0.12 + fm * 0.36, mes, fm, C.claro)}${fT(w / 2, h * 0.68, dia, fd, C.tinta)}${fT(w / 2, h * 0.9, sem, fs, C.tinta)}`;
        }
        // camisa de time: listras alternadas (cores em "lis"), faixa no peito e o patrocínio "BET" opcionais
        function camisa(id, w, h, cor, lis = [], faixa = null, bet = false) {
          const p = `M${w * 0.36} 0 Q${w * 0.5} ${h * 0.13} ${w * 0.64} 0 L${w * 0.86} ${h * 0.06} L${w} ${h * 0.32} L${w * 0.84} ${h * 0.42} L${w * 0.82} ${h} L${w * 0.18} ${h} L${w * 0.16} ${h * 0.42} L0 ${h * 0.32} L${w * 0.14} ${h * 0.06} Z`;
          let s = "";
          const n = lis.length ? 7 : 0;
          for (let k = 1; k < n; k += 2) s += `<rect x="${(k * w) / n}" y="0" width="${w / n}" height="${h}" fill="${lis[((k - 1) / 2) % lis.length]}"/>`;
          if (faixa) s += `<rect x="0" y="${h * 0.24}" width="${w}" height="${h * 0.12}" fill="${faixa}"/>`;
          const fb = caber("BET", w * 0.4, h * 0.14);
          const pat = bet ? `<rect x="${w * 0.3}" y="${h * 0.46}" width="${w * 0.4}" height="${h * 0.19}" rx="4" fill="${C.verm}" stroke="${C.tinta}" stroke-width="2"/>${fT(w / 2, h * 0.555 + fb * 0.36, "BET", fb, C.claro)}` : "";
          return `<defs><clipPath id="cl-${id}"><path d="${p}"/></clipPath></defs><path d="${p}" fill="${cor}"/><g clip-path="url(#cl-${id})">${s}</g>${pat}<path d="${p}" fill="none" stroke="${C.tinta}" stroke-width="${Math.max(2.5, w * 0.025)}" stroke-linejoin="round"/>`;
        }
        function banco(w, h) {
          const fr = h * 0.26, fb = caber("BANCO", w * 0.5, fr * 0.5);
          let s = `<path d="M0 ${fr} L${w / 2} 0 L${w} ${fr} Z" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="4"/>${fT(w / 2, fr * 0.78, "BANCO", fb, C.tinta)}<rect y="${fr}" width="${w}" height="${h * 0.07}" fill="${C.tinta}"/>`;
          const cw = w * 0.1;
          for (let k = 0; k < 4; k++) s += `<rect x="${w * 0.1 + (k * (w * 0.8 - cw)) / 3}" y="${fr + h * 0.07}" width="${cw}" height="${h * 0.52}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>`;
          return s + `<rect x="${w * 0.04}" y="${h * 0.85}" width="${w * 0.92}" height="${h * 0.07}" fill="${C.kraft2}"/><rect y="${h * 0.92}" width="${w}" height="${h * 0.08}" fill="${C.tinta}"/>`;
        }
        function predioBet(w, h) {
          const fb = caber("BET", w * 0.9, h * 0.12);
          let s = `<rect x="${w * 0.15}" y="${h * 0.2}" width="${w * 0.7}" height="${h * 0.8}" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="4"/><rect x="${w * 0.05}" y="0" width="${w * 0.9}" height="${h * 0.17}" rx="8" fill="${C.verm}"/>${fT(w / 2, h * 0.085 + fb * 0.36, "BET", fb, C.claro)}`;
          for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) s += `<rect x="${w * 0.23 + c * w * 0.19}" y="${h * 0.28 + r * h * 0.18}" width="${w * 0.12}" height="${h * 0.1}" fill="${C.claro}"/>`;
          return s + `<rect x="${w * 0.42}" y="${h * 0.84}" width="${w * 0.16}" height="${h * 0.16}" fill="${C.tinta}" opacity=".7"/>`;
        }
        // folhinha de outubro com os dias 5 a 18 (duas semanas)
        function calOut(w, h) {
          const hd = h * 0.24, cw = w / 7, rh = (h - hd) / 2, fm = caber("OUTUBRO", w, hd * 0.62), fd = Math.min(rh * 0.42, caber("18", cw, 40));
          let s = `<path d="${pRet(w, h, 515, 1.6, 30)}" fill="${C.claro}"/><rect width="${w}" height="${hd}" fill="${C.verm}"/>${fT(w / 2, hd / 2 + fm * 0.36, "OUTUBRO", fm, C.claro)}`;
          for (let d = 5; d <= 18; d++) {
            const k = d - 5, r = Math.floor(k / 7), c = k % 7;
            s += fT(c * cw + cw / 2, hd + r * rh + rh / 2 + fd * 0.36, String(d), fd, C.tinta);
          }
          return s;
        }
        const relogio = (d) => `<circle cx="${d / 2}" cy="${d / 2}" r="${d / 2 - 4}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="7"/>` +
          Array.from({ length: 12 }, (_, k) => `<rect x="${d / 2 - 2}" y="9" width="4" height="${d * 0.08}" fill="${C.tinta}" transform="rotate(${k * 30} ${d / 2} ${d / 2})"/>`).join("");
        const lista = (w, h) => `<path d="${pRet(w, h, 333, 1.4, 20)}" fill="${C.claro}"/>` +
          [0, 1, 2, 3].map((k) => `<rect x="10" y="${16 + k * h * 0.21}" width="${w * 0.48}" height="7" rx="3" fill="${C.tinta}" opacity=".3"/>${fT(w - 10, 24 + k * h * 0.21, "R$", caber("R$", w * 0.4, 18), C.verm, "end")}`).join("");
        function site(w, h) {
          const fb = caber("BET", w, 44);
          return `<rect width="${w}" height="${h}" rx="10" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/><rect width="${w}" height="${h * 0.2}" rx="10" fill="${C.tinta}"/>` +
            [0, 1, 2].map((k) => `<circle cx="${14 + k * 16}" cy="${h * 0.1}" r="5" fill="${[C.verm, C.amar, C.claro][k]}"/>`).join("") + fT(w / 2, h * 0.62 + fb * 0.36, "BET", fb, C.verm);
        }
        // marreta: a cabeça na ponta esquerda, o cabo com "GOVERNO"; o pivô é a mão (300, 70)
        const marreta = () => `<rect x="80" y="55" width="220" height="30" rx="8" fill="${C.tinta}"/>${fT(190, 70 + 22 * 0.36, "GOVERNO", 22, C.claro)}<rect x="0" y="0" width="84" height="140" rx="10" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/><rect x="2" y="22" width="80" height="12" fill="${C.verm2}"/><rect x="2" y="106" width="80" height="12" fill="${C.verm2}"/>`;
        const mao = (w, h, cor) => `<path d="M${w * 0.22} ${h} L${w * 0.22} ${h * 0.42} Q${w * 0.22} ${h * 0.08} ${w * 0.5} ${h * 0.08} Q${w * 0.78} ${h * 0.08} ${w * 0.78} ${h * 0.42} L${w * 0.78} ${h} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="4"/><path d="M${w * 0.22} ${h * 0.58} Q${w * 0.02} ${h * 0.52} ${w * 0.05} ${h * 0.36}" fill="none" stroke="${C.tinta}" stroke-width="7" stroke-linecap="round"/>`;
        // papel com faixa de título, subtítulo e linhas (o tamanho do texto sai da folha)
        function folha(w, h, seed, t1, t2, faixa = C.tinta) {
          const hb = h * 0.18, f1 = caber(t1, w, hb * 0.62), f2 = caber(t2, w, h * 0.1);
          let s = `<path d="${pRet(w, h, seed)}" fill="${C.claro}"/><rect width="${w}" height="${hb}" fill="${faixa}"/>${fT(w / 2, hb / 2 + f1 * 0.36, t1, f1, C.claro)}${fT(w / 2, hb + h * 0.11, t2, f2, C.tinta)}`;
          const n = Math.max(2, Math.floor((h * 0.6) / 26));
          for (let i = 0; i < n; i++) s += `<rect x="${w * 0.1}" y="${hb + h * 0.18 + i * 26}" width="${w * 0.8 * (0.6 + rnd(seed + i) * 0.4)}" height="7" rx="3" fill="${C.tinta}" opacity=".18"/>`;
          return s;
        }
        const maquina = (w, h) => `<rect width="${w}" height="${h}" rx="26" fill="${C.claro}" stroke="${C.tinta}" stroke-width="7"/><path d="M26 3.5 L${w - 26} 3.5 Q${w - 3.5} 3.5 ${w - 3.5} 26 L${w - 3.5} ${h * 0.17} L3.5 ${h * 0.17} L3.5 26 Q3.5 3.5 26 3.5 Z" fill="${C.kraft}"/><rect x="0" y="${h * 0.17}" width="${w}" height="5" fill="${C.tinta}"/>` +
          `<circle cx="${w * 0.8}" cy="${h * 0.085}" r="${h * 0.045}" fill="${C.tinta}"/><circle cx="${w * 0.64}" cy="${h * 0.085}" r="${h * 0.03}" fill="${C.verm}"/><rect x="${w * 0.08}" y="${h * 0.06}" width="${w * 0.3}" height="${h * 0.05}" rx="6" fill="${C.tinta}" opacity=".6"/>` +
          `<circle cx="${w / 2}" cy="${h * 0.58}" r="${w * 0.36}" fill="${C.tinta}"/><circle cx="${w / 2}" cy="${h * 0.58}" r="${w * 0.29}" fill="#9fb6d8"/>`;
        function distintivo(w, h) {
          const fp = caber("PF", w * 0.7, h * 0.26);
          return `<path d="M${w / 2} 4 L${w - 4} ${h * 0.14} L${w * 0.92} ${h * 0.62} Q${w * 0.8} ${h * 0.88} ${w / 2} ${h - 4} Q${w * 0.2} ${h * 0.88} ${w * 0.08} ${h * 0.62} L4 ${h * 0.14} Z" fill="${C.azul2}" stroke="${C.amar}" stroke-width="8" stroke-linejoin="round"/>${ic(w / 2 - w * 0.18, h * 0.18, (w * 0.36) / 40, estrela(20, C.amar))}${fT(w / 2, h * 0.74, "PF", fp, C.claro)}`;
        }
        const giroflex = (cor) => `<path d="M10 60 Q10 0 50 0 Q90 0 90 60 Z" fill="${cor}"/><rect y="56" width="100" height="14" rx="4" fill="${C.tinta}"/>`;
        const lupa = `<circle cx="70" cy="70" r="56" fill="${C.claro}" fill-opacity=".35" stroke="${C.tinta}" stroke-width="12"/><path d="M112 112 L168 168" stroke="${C.tinta}" stroke-width="20" stroke-linecap="round"/>`;
        function placar(w, h) {
          const fl = caber("FIM DAS BETS", w * 0.43, 34);
          let s = `<rect width="${w}" height="${h}" rx="18" fill="${C.tinta}"/><rect x="${w * 0.04}" y="${h * 0.32}" width="${w * 0.43}" height="${h * 0.6}" rx="10" fill="#2e2a45"/><rect x="${w * 0.53}" y="${h * 0.32}" width="${w * 0.43}" height="${h * 0.6}" rx="10" fill="#2e2a45"/>` +
            fT(w * 0.255, h * 0.21, "FIM DAS BETS", fl, "#8fb1ec") + fT(w * 0.745, h * 0.21, "VICIADOS", fl, C.rosa);
          for (let x = 30; x < w - 20; x += 44) s += `<circle cx="${x}" cy="10" r="4" fill="${C.amar}" opacity=".7"/>`;
          return s;
        }
        function cacaNiquel(w, h) {
          const fb = caber("BET", w * 0.84, h * 0.12), f7 = caber("7", w * 0.24, h * 0.2);
          return `<rect x="0" y="${h * 0.14}" width="${w}" height="${h * 0.86}" rx="20" fill="${C.azul2}" stroke="${C.tinta}" stroke-width="6"/><rect x="${w * 0.08}" y="3" width="${w * 0.84}" height="${h * 0.17}" rx="14" fill="${C.amar}" stroke="${C.tinta}" stroke-width="5"/>${fT(w / 2, h * 0.095 + fb * 0.36, "BET", fb, C.tinta)}` +
            `<rect x="${w * 0.1}" y="${h * 0.26}" width="${w * 0.8}" height="${h * 0.26}" rx="10" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
            [0, 1, 2].map((k) => fT(w * 0.23 + k * w * 0.27, h * 0.39 + f7 * 0.36, "7", f7, C.verm)).join("") +
            `<rect x="${w * 0.15}" y="${h * 0.62}" width="${w * 0.7}" height="${h * 0.1}" rx="6" fill="${C.amar2}"/><rect x="${w * 0.3}" y="${h * 0.82}" width="${w * 0.4}" height="${h * 0.06}" rx="4" fill="${C.tinta}"/>`;
        }
        const luva = (esq) => `<g transform="${esq ? "translate(90 0) scale(-1 1)" : ""}"><path d="M10 20 Q10 0 40 0 L60 0 Q86 0 86 30 L86 52 Q86 74 60 74 L30 74 Q10 74 10 56 Z" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/><path d="M14 44 Q0 44 0 30 Q0 18 14 20" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/><rect x="16" y="74" width="58" height="20" rx="4" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/></g>`;
        function stf(w, h) {
          const fr = h * 0.27, fs = caber("STF", w * 0.4, fr * 0.55);
          let s = `<path d="M0 ${fr} L${w / 2} 0 L${w} ${fr} Z" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>${fT(w / 2, fr * 0.8, "STF", fs, C.tinta)}<rect y="${fr}" width="${w}" height="${h * 0.07}" fill="${C.tinta}"/>`;
          const cw = w * 0.075;
          for (let k = 0; k < 6; k++) s += `<rect x="${w * 0.06 + (k * (w * 0.88 - cw)) / 5}" y="${fr + h * 0.07}" width="${cw}" height="${h * 0.5}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>`;
          return s + `<rect x="${w * 0.03}" y="${h * 0.84}" width="${w * 0.94}" height="${h * 0.06}" fill="${C.kraft}"/><rect y="${h * 0.9}" width="${w}" height="${h * 0.1}" fill="${C.kraft2}"/>`;
        }
        const lixeira = (w, h) => `<path d="M${w * 0.1} ${h * 0.18} L${w * 0.9} ${h * 0.18} L${w * 0.8} ${h} L${w * 0.2} ${h} Z" fill="#6b6880" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          [0.35, 0.5, 0.65].map((f) => `<rect x="${w * f - 3}" y="${h * 0.28}" width="6" height="${h * 0.62}" rx="3" fill="${C.tinta}" opacity=".45"/>`).join("");
        const tampa = (w) => `<rect x="0" y="18" width="${w}" height="16" rx="6" fill="${C.tinta}"/><rect x="${w * 0.4}" y="6" width="${w * 0.2}" height="14" rx="5" fill="${C.tinta}"/>`;
        const ampulheta = (w, h) => `<rect width="${w}" height="${h * 0.07}" rx="6" fill="${C.kraft2}"/><rect y="${h * 0.93}" width="${w}" height="${h * 0.07}" rx="6" fill="${C.kraft2}"/><path d="M${w * 0.14} ${h * 0.07} L${w * 0.86} ${h * 0.07} L${w * 0.54} ${h * 0.5} L${w * 0.86} ${h * 0.93} L${w * 0.14} ${h * 0.93} L${w * 0.46} ${h * 0.5} Z" fill="${C.claro}" fill-opacity=".55" stroke="${C.tinta}" stroke-width="6" stroke-linejoin="round"/>`;
        function painel(w, h) {
          const fs = caber("NÃO", w * 0.42, h * 0.4);
          return `<rect width="${w}" height="${h}" rx="16" fill="${C.tinta}"/><rect x="${w * 0.05}" y="${h * 0.16}" width="${w * 0.42}" height="${h * 0.68}" rx="10" fill="#2e2a45"/><rect x="${w * 0.53}" y="${h * 0.16}" width="${w * 0.42}" height="${h * 0.68}" rx="10" fill="#2e2a45"/>` +
            fT(w * 0.26, h / 2 + fs * 0.36, "SIM", fs, "#6b6880") + fT(w * 0.74, h / 2 + fs * 0.36, "NÃO", fs, "#6b6880");
        }
        const balao = (w, h, txt) => { const fs = caber(txt, w, h * 0.45); return `<path d="M18 0 L${w - 18} 0 Q${w} 0 ${w} 18 L${w} ${h * 0.62} Q${w} ${h * 0.8} ${w - 18} ${h * 0.8} L${w * 0.58} ${h * 0.8} L${w * 0.45} ${h} L${w * 0.43} ${h * 0.8} L18 ${h * 0.8} Q0 ${h * 0.8} 0 ${h * 0.62} L0 18 Q0 0 18 0 Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>${fT(w / 2, h * 0.4 + fs * 0.36, txt, fs, C.verm)}`; };


        // ── desenhos do C21 ───────────────────────────────────────────────────
        function predio(w, h, txt, cor = C.kraft2) {
          const fr = h * 0.26, fb = caber(txt, w * 0.5, fr * 0.5);
          let s = `<path d="M0 ${fr} L${w / 2} 0 L${w} ${fr} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="4"/>${fT(w / 2, fr * 0.8, txt, fb, C.tinta)}<rect y="${fr}" width="${w}" height="${h * 0.07}" fill="${C.tinta}"/>`;
          const cw = w * 0.1;
          for (let k = 0; k < 4; k++) s += `<rect x="${w * 0.1 + (k * (w * 0.8 - cw)) / 3}" y="${fr + h * 0.07}" width="${cw}" height="${h * 0.52}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>`;
          return s + `<rect x="${w * 0.04}" y="${h * 0.85}" width="${w * 0.92}" height="${h * 0.07}" fill="${C.kraft}"/><rect y="${h * 0.92}" width="${w}" height="${h * 0.08}" fill="${C.tinta}"/>`;
        }
        // a diarista: lenço amarelo na cabeça e avental claro (um desenho só)
        const diarista = (w, h) => `${pessoa(w, h, C.verm2)}<path d="M${w / 2 - h * 0.15} ${h * 0.15} A${h * 0.15} ${h * 0.15} 0 0 1 ${w / 2 + h * 0.15} ${h * 0.15} Z" fill="${C.amar}"/><circle cx="${w / 2 + h * 0.15}" cy="${h * 0.16}" r="${h * 0.035}" fill="${C.amar2}"/>` +
          `<rect x="${w * 0.27}" y="${h * 0.5}" width="${w * 0.46}" height="${h * 0.48}" rx="6" fill="${C.claro}"/><rect x="${w * 0.4}" y="${h * 0.64}" width="${w * 0.2}" height="${h * 0.1}" rx="3" fill="${C.kraft2}"/>`;
        const vassoura = (w, h) => `<rect x="${w / 2 - 4}" y="0" width="8" height="${h * 0.74}" fill="${C.kraft2}"/><path d="M${w * 0.12} ${h} L${w * 0.3} ${h * 0.72} L${w * 0.7} ${h * 0.72} L${w * 0.88} ${h} Z" fill="${C.amar2}"/>`;
        const balde = (w, h) => `<path d="M${w * 0.1} ${h * 0.28} Q${w / 2} ${-h * 0.25} ${w * 0.9} ${h * 0.28}" fill="none" stroke="${C.tinta}" stroke-width="5"/><path d="M0 ${h * 0.25} L${w} ${h * 0.25} L${w * 0.86} ${h} L${w * 0.14} ${h} Z" fill="${C.azul}"/>`;
        function ctps(w, h) {
          const f1 = caber("CARTEIRA DE", w, 24), f2 = caber("TRABALHO", w, 26);
          return `<rect width="${w}" height="${h}" rx="10" fill="#2a4f8a" stroke="${C.tinta}" stroke-width="4"/><circle cx="${w / 2}" cy="${h * 0.32}" r="${w * 0.17}" fill="none" stroke="${C.amar}" stroke-width="4"/>` +
            fT(w / 2, h * 0.64, "CARTEIRA DE", f1, C.claro) + fT(w / 2, h * 0.64 + f2 * 1.15, "TRABALHO", f2, C.claro);
        }
        function cartaoBF(w, h) {
          const fs = caber("FAMÍLIA", w * 0.9, h * 0.24);
          return `<rect width="${w}" height="${h}" rx="${h * 0.08}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/><rect y="${h * 0.12}" width="${w}" height="${h * 0.12}" fill="#1f6b45"/><rect x="${w * 0.08}" y="${h * 0.34}" width="${w * 0.14}" height="${h * 0.16}" rx="4" fill="${C.kraft2}"/>` +
            fT(w * 0.58, h * 0.47, "BOLSA", fs, C.tinta) + fT(w / 2, h * 0.47 + fs * 1.1, "FAMÍLIA", fs, C.tinta);
        }
        // a mão do governo: manga escura com "GOVERNO" e a mão aberta (aponta para a esquerda)
        function garra(w, h) {
          const fg = caber("GOVERNO", w * 0.52, h * 0.22);
          return `<rect x="${w * 0.42}" y="${h * 0.3}" width="${w * 0.58}" height="${h * 0.4}" rx="8" fill="${C.tinta}"/>${fT(w * 0.71, h * 0.5 + fg * 0.36, "GOVERNO", fg, C.claro)}` +
            `<ellipse cx="${w * 0.32}" cy="${h * 0.5}" rx="${w * 0.14}" ry="${h * 0.24}" fill="${C.rosa}" stroke="${C.tinta}" stroke-width="4"/>` +
            [0, 1, 2, 3].map((k) => `<rect x="${w * 0.04}" y="${h * (0.3 + k * 0.11)}" width="${w * 0.2}" height="${h * 0.09}" rx="${h * 0.045}" fill="${C.rosa}" stroke="${C.tinta}" stroke-width="3"/>`).join("") +
            `<rect x="${w * 0.24}" y="${h * 0.12}" width="${w * 0.08}" height="${h * 0.22}" rx="${w * 0.04}" fill="${C.rosa}" stroke="${C.tinta}" stroke-width="3"/>`;
        }
        function arroz(w, h) {
          const fa = caber("ARROZ", w * 0.9, 44), fk = caber("5 kg", w * 0.6, 30);
          return `<path d="M${w * 0.08} ${h * 0.12} L${w * 0.92} ${h * 0.12} L${w} ${h} L0 ${h} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/><rect x="${w * 0.1}" y="2" width="${w * 0.8}" height="${h * 0.13}" rx="4" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="3"/>` +
            `<rect x="${w * 0.05}" y="${h * 0.32}" width="${w * 0.9}" height="${h * 0.24}" fill="${C.verm}"/>${fT(w / 2, h * 0.44 + fa * 0.36, "ARROZ", fa, C.claro)}${fT(w / 2, h * 0.78, "5 kg", fk, C.tinta)}`;
        }
        function contaLuz(w, h) {
          return `${folha(w, h, 1212, "ENERGIA", "CONTA DE LUZ", C.amar2)}<path d="M${w * 0.55} ${h * 0.42} L${w * 0.38} ${h * 0.66} L${w * 0.52} ${h * 0.66} L${w * 0.44} ${h * 0.88} L${w * 0.66} ${h * 0.6} L${w * 0.52} ${h * 0.6} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/>`;
        }
        const empresario = (w, h) => `${pessoa(w, h, C.tinta, gravata(w, h))}<rect x="${w / 2 - h * 0.11}" y="${h * 0.12}" width="${h * 0.22}" height="${h * 0.05}" rx="${h * 0.02}" fill="#0c0b14"/><rect x="${w / 2 - h * 0.1}" y="${h * 0.11}" width="${h * 0.08}" height="${h * 0.06}" rx="${h * 0.02}" fill="#3a3854"/><rect x="${w / 2 + h * 0.02}" y="${h * 0.11}" width="${h * 0.08}" height="${h * 0.06}" rx="${h * 0.02}" fill="#3a3854"/>`;
        const maleta = (w, h) => `<path d="M${w * 0.35} ${h * 0.25} L${w * 0.35} ${h * 0.08} L${w * 0.65} ${h * 0.08} L${w * 0.65} ${h * 0.25}" fill="none" stroke="${C.tinta}" stroke-width="6"/><rect y="${h * 0.22}" width="${w}" height="${h * 0.78}" rx="10" fill="#6b4a2b" stroke="${C.tinta}" stroke-width="4"/>${fT(w / 2, h * 0.62 + caber("R$", w * 0.5, h * 0.36) * 0.36, "R$", caber("R$", w * 0.5, h * 0.36), C.amar)}`;
        function escudo(w, h) {
          const fs = caber("LEGÍTIMA", w * 0.82, h * 0.15);
          return `<path d="M${w / 2} 4 L${w - 4} ${h * 0.14} L${w * 0.92} ${h * 0.62} Q${w * 0.8} ${h * 0.88} ${w / 2} ${h - 4} Q${w * 0.2} ${h * 0.88} ${w * 0.08} ${h * 0.62} L4 ${h * 0.14} Z" fill="${C.azul}" stroke="${C.tinta}" stroke-width="6" stroke-linejoin="round"/>` +
            fT(w / 2, h * 0.42, "LEGÍTIMA", fs, C.claro) + fT(w / 2, h * 0.42 + fs * 1.2, "DEFESA", fs, C.claro);
        }
        const posts = (w, h) => [0, 1, 2].map((k) => `<rect x="${w * 0.12}" y="${h * (0.16 + k * 0.25)}" width="${w * 0.76}" height="${h * 0.2}" rx="8" fill="#e6dccb"/><circle cx="${w * 0.22}" cy="${h * (0.21 + k * 0.25)}" r="${w * 0.05}" fill="${C.azul}"/><rect x="${w * 0.32}" y="${h * (0.19 + k * 0.25)}" width="${w * 0.46}" height="${h * 0.025}" fill="${C.tinta}" opacity=".35"/><rect x="${w * 0.2}" y="${h * (0.27 + k * 0.25)}" width="${w * 0.58}" height="${h * 0.025}" fill="${C.tinta}" opacity=".25"/>`).join("");
        const prato = (w, h) => `<ellipse cx="${w / 2}" cy="${h / 2}" rx="${w / 2 - 3}" ry="${h / 2 - 3}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/><ellipse cx="${w / 2}" cy="${h / 2}" rx="${w * 0.32}" ry="${h * 0.3}" fill="none" stroke="${C.kraft2}" stroke-width="3"/>`;
        const carteira = (w, h) => `<rect width="${w}" height="${h}" rx="10" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="4"/><rect x="${w * 0.08}" y="${h * 0.2}" width="${w * 0.84}" height="${h * 0.6}" rx="6" fill="#8f7a55"/><rect x="${w * 0.6}" y="${h * 0.4}" width="${w * 0.32}" height="${h * 0.22}" rx="4" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="2"/>`;
        const podio = (w, h, txt) => `<rect y="0" width="${w}" height="${h}" rx="6" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>${fT(w / 2, h / 2 + caber(txt, w, h * 0.6) * 0.36, txt, caber(txt, w, h * 0.6), C.tinta)}`;
        const holofote = (w, h) => `<path d="M${w * 0.42} 0 L${w * 0.58} 0 L${w} ${h} L0 ${h} Z" fill="${C.amar}" opacity=".28"/>`;
        // fila de reconhecimento: a parede com as marcas de altura
        function parede(w, h) {
          let s = `<path d="${pRet(w, h, 4040, 1.6, 40)}" fill="${C.kraft}"/>`;
          for (let k = 1; k < 6; k++) s += `<rect x="0" y="${h - k * h * 0.16}" width="${w}" height="3" fill="${C.tinta}" opacity=".35"/>${fM(10, h - k * h * 0.16 - 6, (150 + k * 10) + "", 16, C.tinta, "start", 0.55)}`;
          return s;
        }
        const numero = (n) => `<rect width="70" height="44" rx="6" fill="${C.tinta}"/>${fT(35, 22 + 26 * 0.36, String(n), 26, C.claro)}`;
        const saco = (w, h) => `<path d="M${w * 0.32} ${h * 0.12} L${w * 0.68} ${h * 0.12} L${w * 0.6} ${h * 0.28} Q${w} ${h * 0.5} ${w * 0.9} ${h * 0.85} Q${w * 0.8} ${h} ${w / 2} ${h} Q${w * 0.2} ${h} ${w * 0.1} ${h * 0.85} Q0 ${h * 0.5} ${w * 0.4} ${h * 0.28} Z" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="3"/>${fT(w / 2, h * 0.78, "R$", caber("R$", w, 22), C.tinta)}`;
        const prefeito = (w, h) => `${pessoa(w, h, C.azul2, gravata(w, h, C.amar))}<path d="M${w * 0.12} ${h * 0.4} L${w * 0.88} ${h * 0.8} L${w * 0.88} ${h * 0.88} L${w * 0.12} ${h * 0.48} Z" fill="#1f6b45"/>`;
        const classeMedia = (w, h) => `${pessoa(w, h, C.azul)}<rect x="${w * 0.3}" y="${h * 0.52}" width="${w * 0.4}" height="${h * 0.06}" fill="${C.claro}" opacity=".6"/>`;
        function caixaReg(w, h) {
          const fd = caber("R$ 0,00", w * 0.5, h * 0.12);
          return `<rect x="${w * 0.08}" y="${h * 0.02}" width="${w * 0.55}" height="${h * 0.28}" rx="8" fill="#2e2a45" stroke="${C.tinta}" stroke-width="4"/>${fT(w * 0.355, h * 0.16 + fd * 0.36, "R$", fd, C.amar)}` +
            `<rect x="0" y="${h * 0.36}" width="${w}" height="${h * 0.64}" rx="12" fill="${C.tinta}"/>` +
            Array.from({ length: 9 }, (_, k) => `<rect x="${w * 0.1 + (k % 3) * w * 0.14}" y="${h * 0.46 + Math.floor(k / 3) * h * 0.13}" width="${w * 0.1}" height="${h * 0.09}" rx="4" fill="#6b6880"/>`).join("") +
            `<rect x="${w * 0.6}" y="${h * 0.46}" width="${w * 0.3}" height="${h * 0.35}" rx="6" fill="${C.verm}"/>`;
        }
        function cupom(w, h) {
          let s = `<path d="M0 0 L${w} 0 L${w} ${h - 10} L${w * 0.9} ${h} L${w * 0.8} ${h - 10} L${w * 0.7} ${h} L${w * 0.6} ${h - 10} L${w * 0.5} ${h} L${w * 0.4} ${h - 10} L${w * 0.3} ${h} L${w * 0.2} ${h - 10} L${w * 0.1} ${h} L0 ${h - 10} Z" fill="#fbf7ee" stroke="${C.tinta}" stroke-width="3"/>`;
          s += fM(w / 2, 34, "CUPOM", 22, C.tinta, "middle") + `<rect x="14" y="46" width="${w - 28}" height="2" fill="${C.tinta}" opacity=".5"/>`;
          s += fM(16, 84, "COXINHA", 22, C.tinta) + fM(w - 16, 84, "1 UN", 20, C.tinta, "end");
          s += fM(16, 124, "IMPOSTO", 22, C.verm) + fM(w - 16, 124, "SIM", 22, C.verm, "end");
          for (let k = 0; k < 3; k++) s += `<rect x="16" y="${150 + k * 26}" width="${(w - 32) * (0.5 + rnd(k + 66) * 0.5)}" height="6" rx="3" fill="${C.tinta}" opacity=".18"/>`;
          return s;
        }
        const coxinha = (w, h) => `<path d="M${w / 2} 4 Q${w * 0.95} ${h * 0.6} ${w * 0.82} ${h * 0.9} Q${w / 2} ${h + 4} ${w * 0.18} ${h * 0.9} Q${w * 0.05} ${h * 0.6} ${w / 2} 4 Z" fill="#c98a3c" stroke="${C.tinta}" stroke-width="4"/><path d="M${w * 0.3} ${h * 0.7} Q${w / 2} ${h * 0.78} ${w * 0.7} ${h * 0.7}" fill="none" stroke="#e9b86e" stroke-width="5" stroke-linecap="round"/>`;
        function moto(w, h) {
          const r = h * 0.2, fe = caber("ENTREGA", w * 0.3, h * 0.12);
          return `<circle cx="${w * 0.2}" cy="${h - r - 3}" r="${r}" fill="${C.tinta}"/><circle cx="${w * 0.2}" cy="${h - r - 3}" r="${r * 0.45}" fill="#6b6880"/><circle cx="${w * 0.82}" cy="${h - r - 3}" r="${r}" fill="${C.tinta}"/><circle cx="${w * 0.82}" cy="${h - r - 3}" r="${r * 0.45}" fill="#6b6880"/>` +
            `<path d="M${w * 0.2} ${h - r - 3} L${w * 0.36} ${h * 0.5} L${w * 0.7} ${h * 0.5} L${w * 0.82} ${h - r - 3}" fill="none" stroke="${C.verm}" stroke-width="${h * 0.07}" stroke-linejoin="round"/><path d="M${w * 0.36} ${h * 0.46} L${w * 0.62} ${h * 0.46}" stroke="${C.tinta}" stroke-width="${h * 0.06}" stroke-linecap="round"/>` +
            `<path d="M${w * 0.72} ${h * 0.5} L${w * 0.78} ${h * 0.26} L${w * 0.86} ${h * 0.24}" fill="none" stroke="${C.tinta}" stroke-width="6" stroke-linecap="round"/>` +
            `<rect x="${w * 0.02}" y="${h * 0.12}" width="${w * 0.32}" height="${h * 0.3}" rx="6" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4"/>${fT(w * 0.18, h * 0.27 + fe * 0.36, "ENTREGA", fe, C.claro)}`;
        }
        const cone = (w, h) => `<path d="M${w * 0.4} 0 L${w * 0.6} 0 L${w * 0.9} ${h * 0.88} L${w * 0.1} ${h * 0.88} Z" fill="${C.verm}"/><path d="M${w * 0.32} ${h * 0.3} L${w * 0.68} ${h * 0.3} L${w * 0.74} ${h * 0.48} L${w * 0.26} ${h * 0.48} Z" fill="${C.claro}"/><rect x="0" y="${h * 0.86}" width="${w}" height="${h * 0.14}" rx="4" fill="${C.tinta}"/>`;
        const placaBlitz = (w, h) => `<rect x="${w / 2 - 6}" y="${h * 0.42}" width="12" height="${h * 0.58}" fill="${C.kraft2}"/><rect width="${w}" height="${h * 0.44}" rx="8" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4"/>${fT(w / 2, h * 0.22 + caber("BLITZ", w, h * 0.3) * 0.36, "BLITZ", caber("BLITZ", w, h * 0.3), C.claro)}`;
        const cadeado = (w, h) => `<path d="M${w * 0.24} ${h * 0.46} L${w * 0.24} ${h * 0.28} Q${w * 0.24} 4 ${w / 2} 4 Q${w * 0.76} 4 ${w * 0.76} ${h * 0.28} L${w * 0.76} ${h * 0.46}" fill="none" stroke="${C.tinta}" stroke-width="${w * 0.12}"/><rect x="0" y="${h * 0.42}" width="${w}" height="${h * 0.58}" rx="8" fill="${C.amar2}" stroke="${C.tinta}" stroke-width="4"/><circle cx="${w / 2}" cy="${h * 0.68}" r="${w * 0.08}" fill="${C.tinta}"/>`;
        const pulpito = (w, h) => `<path d="M${w * 0.1} ${h * 0.25} L${w * 0.9} ${h * 0.25} L${w * 0.8} ${h} L${w * 0.2} ${h} Z" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="4"/><rect x="0" y="${h * 0.18}" width="${w}" height="${h * 0.1}" rx="5" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w * 0.5} ${h * 0.18} L${w * 0.58} ${h * 0.04}" stroke="${C.tinta}" stroke-width="5"/><rect x="${w * 0.54}" y="0" width="${w * 0.12}" height="${h * 0.08}" rx="${h * 0.04}" fill="${C.tinta}"/>`;
        // a pauta (o fio do vídeo): faixa "PAUTA", a caixinha do item 1 e as linhas dos outros itens
        function pauta(w, h) {
          let s = `<path d="${pRet(w, h, 2121, 1.6, 30)}" fill="${C.claro}"/><rect width="${w}" height="${h * 0.14}" fill="${C.tinta}"/>${fT(w / 2, h * 0.07 + caber("PAUTA", w, h * 0.09) * 0.36, "PAUTA", caber("PAUTA", w, h * 0.09), C.claro)}`;
          s += `<rect x="40" y="${h * 0.24}" width="60" height="60" rx="6" fill="none" stroke="${C.tinta}" stroke-width="5"/>`;
          for (let k = 0; k < 5; k++) s += `<rect x="40" y="${h * 0.52 + k * 44}" width="34" height="34" rx="5" fill="none" stroke="${C.tinta}" stroke-width="3" opacity=".35"/><rect x="92" y="${h * 0.52 + k * 44 + 12}" width="${(w - 140) * (0.55 + rnd(k + 300) * 0.4)}" height="10" rx="5" fill="${C.tinta}" opacity=".18"/>`;
          return s;
        }

