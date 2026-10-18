
        // ══════════════════════════════════════════════════════════════════════
        // BANCO DE ELEMENTOS (06/10/2026, aprovado pelo Mickael no mock-up "hoje × proposta": "pode seguir")
        // Entra no cenas.js depois do personagens.js. Os nomes terminam em N para não colidir com os do motor.
        //   etiquetas e carimbos: o mesmo rotulo(...) de sempre; o visual novo vem do CSS abaixo
        //   moedaN(d) · pilhaN(d, n) · vistoN(s) · xisN(s) · interroN(s) · documentoN(w, h, seed, t1, t2, faixa)
        //   casinhaN(w, h, parede, seed) · multidaoN(w, h, n, linhas, seed) · stfN(w, h) · grafN(w, h, seed)
        // ══════════════════════════════════════════════════════════════════════
        (function () {
          // etiqueta de papel rasgado: bordas em zigue-zague, fita crepe num canto, sombra, letra mínima de 28 px
          const z = [];
          for (let i = 0; i <= 20; i++) z.push(`${i * 5}% ${i % 2 ? 0 : 7}%`);
          for (let i = 1; i <= 4; i++) z.push(`${i % 2 ? 99 : 100}% ${i * 25}%`);
          for (let i = 20; i >= 0; i--) z.push(`${i * 5}% ${i % 2 ? 100 : 93}%`);
          for (let i = 3; i >= 1; i--) z.push(`${i % 2 ? 1 : 0}% ${i * 25}%`);
          // o papel é o ::before (recortado); a fita é o ::after, fora do recorte; a sombra vem do filtro na etiqueta
          const css = `
            .tag { filter: drop-shadow(0 6px 3px rgba(30, 27, 46, 0.3)) drop-shadow(0 14px 12px rgba(30, 27, 46, 0.16)); }
            .tag > span { background: transparent !important; box-shadow: none !important; border-radius: 0; padding: 14px 24px 12px;
              font-size: max(28px, 1em); position: relative; isolation: isolate; }
            .tag > span::before { content: ""; position: absolute; inset: 0; z-index: -1; background: #f8f2e4; clip-path: polygon(${z.join(",")}); }
            .tagt > span::before { background: #1e1b2e; } .tagv > span::before { background: #e5432d; } .taga > span::before { background: #2c56a0; }
            .tag > span::after { content: ""; position: absolute; left: -16px; top: -12px; width: 56px; height: 22px; background: rgba(214, 195, 160, 0.9); transform: rotate(-26deg); }
            .tag:nth-of-type(odd) > span { transform: rotate(-1.6deg); }
            .tag:nth-of-type(even) > span { transform: rotate(1.3deg); }
            .tag:nth-of-type(even) > span::after { left: auto; right: -16px; transform: rotate(24deg); }
            .selo > span { border-width: 8px; outline: 3px solid currentColor; outline-offset: -17px; padding: 14px 34px 8px; background: rgba(248, 242, 228, 0.78); border-radius: 14px; }
            .selo > span::before, .selo > span::after { content: "★"; font-size: 0.42em; vertical-align: middle; margin: 0 0.35em; position: relative; top: -0.12em; }
          `;
          const st = document.createElement("style");
          st.textContent = css;
          document.head.appendChild(st);
        })();

        // moeda dourada: espessura, serrilha, brilho e R$ em relevo
        function moedaN(d, txt = "R$") {
          const r = d / 2;
          let s = `<ellipse cx="${r}" cy="${r + d * 0.07}" rx="${r}" ry="${r}" fill="${C.amar2}"/><circle cx="${r}" cy="${r}" r="${r}" fill="${C.amar}"/>`;
          for (let k = 0; k < 36; k++) { const a = (k / 36) * Math.PI * 2; s += `<path d="M${r + Math.cos(a) * r * 0.92} ${r + Math.sin(a) * r * 0.92} L${r + Math.cos(a) * r} ${r + Math.sin(a) * r}" stroke="${C.amar2}" stroke-width="${Math.max(1.5, d * 0.02)}"/>`; }
          const fs = d * 0.34;
          return s + `<circle cx="${r}" cy="${r}" r="${r * 0.74}" fill="none" stroke="${C.amar2}" stroke-width="${Math.max(2, d * 0.03)}"/>${fT(r + d * 0.02, r + d * 0.14, txt, fs, C.amar2)}${fT(r, r + d * 0.12, txt, fs, "#fff3c4")}` +
            `<path d="M${r * 0.45} ${r * 0.55} Q${r * 0.7} ${r * 0.25} ${r * 1.05} ${r * 0.3}" stroke="#fff8dc" stroke-width="${d * 0.06}" fill="none" stroke-linecap="round" opacity=".8"/>`;
        }
        const pilhaN = (d, n) => Array.from({ length: n }, (_, k) => `<ellipse cx="${d / 2}" cy="${d * 0.9 + (n - 4) * d * 0.14 - k * d * 0.14}" rx="${d / 2}" ry="${d * 0.16}" fill="${k % 2 ? C.amar : C.amar2}" stroke="${C.amar2}" stroke-width="2"/>`).join("") +
          `<ellipse cx="${d / 2}" cy="${d * 0.9 + (n - 4) * d * 0.14 - n * d * 0.14}" rx="${d / 2}" ry="${d * 0.16}" fill="${C.amar}"/>`;
        // ✓ e ✗ de pincel: o traço afina na ponta (dois traços sobrepostos)
        const vistoN = (s, cor = "#3c9a4f") => `<g transform="scale(${s / 60})"><path d="M6 32 L24 52 L58 8" fill="none" stroke="${C.claro}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 32 L24 52 L58 8" fill="none" stroke="${cor}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/><path d="M40 30 L58 8" stroke="${cor}" stroke-width="6" stroke-linecap="round" opacity=".6"/></g>`;
        const xisN = (s, cor = C.verm) => `<g transform="scale(${s / 60})"><path d="M8 8 Q30 32 54 56 M54 6 Q30 30 6 58" fill="none" stroke="${C.claro}" stroke-width="20" stroke-linecap="round"/><path d="M8 8 Q30 32 54 56 M54 6 Q30 30 6 58" fill="none" stroke="${cor}" stroke-width="12" stroke-linecap="round"/><path d="M54 56 L56 68" stroke="${cor}" stroke-width="5" stroke-linecap="round"/><circle cx="56" cy="72" r="4" fill="${cor}"/></g>`;
        // "?" de papel com espessura e risquinhos de tremor
        const interroN = (s, cor = C.verm) => `<g transform="scale(${s / 100})">${fT(54, 92, "?", 110, C.verm2)}${fT(50, 88, "?", 110, cor)}<path d="M4 18 L16 24 M8 46 L20 46 M86 12 L96 4 M90 40 L100 38" stroke="${C.tinta}" stroke-width="5" stroke-linecap="round"/></g>`;
        // documento: orelha dobrada, clipe, linhas, marca-texto, assinatura
        function documentoN(w, h, seed, t1, t2 = "", faixa = C.tinta) {
          const f1 = caber(t1, w - 50, h * 0.11), f2 = t2 ? caber(t2, w - 30, h * 0.07) : 0;
          let s = `<path d="M0 0 L${w - 34} 0 L${w} 34 L${w} ${h} L0 ${h} Z" fill="${C.claro}"/><path d="M${w - 34} 0 L${w - 34} 34 L${w} 34 Z" fill="${C.kraft}"/>` +
            `<rect width="${w - 34}" height="${h * 0.17}" fill="${faixa}"/>${fT((w - 34) / 2, h * 0.085 + f1 * 0.36, t1, f1, C.claro)}${t2 ? fT(w / 2, h * 0.26, t2, f2, C.tinta) : ""}`;
          const n = Math.max(2, Math.floor((h * 0.5) / 22));
          for (let i = 0; i < n; i++) s += `<rect x="${w * 0.08}" y="${h * 0.33 + i * 22}" width="${w * 0.84 * (0.55 + rnd(seed + i) * 0.45)}" height="7" rx="3" fill="${C.tinta}" opacity=".2"/>`;
          s += `<rect x="${w * 0.08}" y="${h * 0.33 + 22 - 5}" width="${w * 0.5}" height="14" fill="${C.amar}" opacity=".45"/>`;
          s += `<path d="M${w * 0.1} ${h - 26} Q${w * 0.18} ${h - 44} ${w * 0.25} ${h - 28} Q${w * 0.32} ${h - 14} ${w * 0.4} ${h - 34}" stroke="${C.azul2}" stroke-width="3" fill="none" stroke-linecap="round"/>`;
          return s + `<path d="M${w * 0.62} -16 L${w * 0.62} 36 Q${w * 0.62} 46 ${w * 0.69} 46 Q${w * 0.76} 46 ${w * 0.76} 36 L${w * 0.76} -4" fill="none" stroke="#8a8f9c" stroke-width="5" stroke-linecap="round"/>`;
        }
        // casinha: beiral, telhas, chaminé, janela acesa, porta com maçaneta
        function casinhaN(w, h, parede = C.kraft, seed = 1) {
          let s = `<rect x="${w * 0.68}" y="${h * 0.06}" width="${w * 0.1}" height="${h * 0.22}" fill="${C.tinta}"/><path d="M${-w * 0.04} ${h * 0.44} L${w / 2} 0 L${w * 1.04} ${h * 0.44} Z" fill="${C.verm}"/>`;
          for (let k = 1; k < 4; k++) s += `<path d="M${w * (0.5 - k * 0.12)} ${h * k * 0.1} L${w * (0.5 + k * 0.12)} ${h * k * 0.1}" stroke="${C.verm2}" stroke-width="3"/>`;
          s += `<rect x="${w * 0.08}" y="${h * 0.42}" width="${w * 0.84}" height="${h * 0.58}" fill="${parede}"/>`;
          s += `<rect x="${w * 0.18}" y="${h * 0.54}" width="${w * 0.24}" height="${h * 0.2}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/><path d="M${w * 0.3} ${h * 0.54} L${w * 0.3} ${h * 0.74} M${w * 0.18} ${h * 0.64} L${w * 0.42} ${h * 0.64}" stroke="${C.tinta}" stroke-width="3"/>`;
          return s + `<path d="M${w * 0.56} ${h} L${w * 0.56} ${h * 0.62} Q${w * 0.56} ${h * 0.52} ${w * 0.68} ${h * 0.52} Q${w * 0.8} ${h * 0.52} ${w * 0.8} ${h * 0.62} L${w * 0.8} ${h} Z" fill="${C.azul2}"/><circle cx="${w * 0.75}" cy="${h * 0.8}" r="${w * 0.02}" fill="${C.amar}"/>`;
        }
        // multidão: bustos com rosto, pele, cabelo e roupa variados; a fila de trás menor e mais escura
        function multidaoN(w, h, n, linhas, seed) {
          let s = "";
          const porLinha = Math.ceil(n / linhas);
          for (let l = linhas - 1; l >= 0; l--) {
            const esc = 1 - l * 0.12, fw = w / porLinha, y = h - (h / linhas) * (l + 1) * 0.9;
            for (let c = 0; c < porLinha && l * porLinha + c < n; c++) {
              const i = seed + l * 31 + c, p = PELE[i % 4], cab = ["#2a1d14", "#c9c4bc", C.tinta, "#7a4a22", C.amar2][i % 5];
              const roupa = [C.azul, C.verm2, "#3c9a4f", C.kraft2, C.rosa2, C.azul2][(i * 7) % 6];
              const x = c * fw + (l % 2 ? fw * 0.45 : 0) + (rnd(i) - 0.5) * fw * 0.2, k = (fw / 50) * esc * (0.92 + rnd(i + 5) * 0.16);
              const f = `<path d="M4 90 L4 48 Q4 36 16 36 L34 36 Q46 36 46 48 L46 90 Z" fill="${roupa}"/><circle cx="25" cy="22" r="16" fill="${p}"/><path d="M9 20 Q10 4 25 4 Q40 4 41 20 Q34 12 25 12 Q16 12 9 20 Z" fill="${cab}"/>` +
                `<circle cx="20" cy="23" r="2.2" fill="${C.tinta}"/><circle cx="30" cy="23" r="2.2" fill="${C.tinta}"/><path d="M20 29 Q25 33 30 29" stroke="${C.tinta}" stroke-width="2" fill="none" stroke-linecap="round"/>`;
              s += `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${k.toFixed(3)})" opacity="${l ? 0.85 : 1}">${recorteP(f)}</g>`;
            }
          }
          return s;
        }
        // STF que o leigo reconhece: a laje, as colunas curvas, o vidro e a bandeira
        function stfN(w, h) {
          let s = `<rect x="0" y="${h * 0.86}" width="${w}" height="${h * 0.14}" fill="${C.kraft2}"/><rect x="${w * 0.08}" y="${h * 0.34}" width="${w * 0.84}" height="${h * 0.52}" fill="#2a3f63"/>`;
          for (let k = 0; k < 7; k++) s += `<rect x="${w * 0.1 + k * w * 0.115}" y="${h * 0.36}" width="${w * 0.1}" height="${h * 0.48}" fill="#3d5a86" opacity=".7"/>`;
          s += `<rect x="0" y="${h * 0.24}" width="${w}" height="${h * 0.1}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>${fT(w / 2, h * 0.315, "SUPREMO TRIBUNAL FEDERAL", caber("SUPREMO TRIBUNAL FEDERAL", w, h * 0.06), C.tinta)}`;
          for (let k = 0; k < 6; k++) { const x = w * 0.04 + k * w * 0.185; s += `<path d="M${x} ${h * 0.86} Q${x + w * 0.045} ${h * 0.56} ${x + w * 0.09} ${h * 0.34} L${x + w * 0.12} ${h * 0.34} Q${x + w * 0.075} ${h * 0.6} ${x + w * 0.03} ${h * 0.86} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="2.5"/>`; }
          s += `<rect x="${w * 0.94}" y="${h * 0.02}" width="4" height="${h * 0.84}" fill="${C.tinta}"/><rect x="${w * 0.945}" y="${h * 0.03}" width="${w * 0.12}" height="${h * 0.08}" fill="#3c9a4f"/><path d="M${w * 1.005} ${h * 0.04} L${w * 1.04} ${h * 0.07} L${w * 1.005} ${h * 0.1} L${w * 0.97} ${h * 0.07} Z" fill="${C.amar}"/>`;
          return recorteP(s);
        }
        // gráfico em papel quadriculado, com a linha de caneta desenhável (id da linha em "lid")
        function grafN(w, h, seed, lid) {
          let s = `<path d="${pRet(w, h, seed)}" fill="#fbf8f0"/>`;
          for (let x = 20; x < w; x += 20) s += `<rect x="${x}" y="4" width="1.5" height="${h - 8}" fill="#9fb6d8" opacity=".45"/>`;
          for (let y = 20; y < h; y += 20) s += `<rect x="4" y="${y}" width="${w - 8}" height="1.5" fill="#9fb6d8" opacity=".45"/>`;
          return s + `<path d="M40 ${h - 36} L${w - 14} ${h - 36} M40 ${h - 36} L40 14" stroke="${C.tinta}" stroke-width="4" fill="none"/>`;
        }

        // ── A MÃO (09/10/2026, C44: "a mão tá horrível… nem sabia que era uma mão") ─────────────────────────────────
        // Mão de papel em pé (dedos para cima, punho embaixo), com manga, punho da camisa, 4 dedos separados, polegar,
        // juntas e unhas. Poses: "aberta", "punho", "aponta" (o indicador), "caneta" (segurando a caneta) e "pega" (os dedos
        // dobrando: use depois da "aberta" com troca() para fechar a mão). Gire o objeto para apontar para os lados.
        //   obj(c, "m0", x, y, 120, 200, maoBoa(120, 200, "aberta"), true, false)
        function maoBoa(w, h, pose = "aberta", pele = PELE[1], manga = C.tinta, punho = C.claro) {
          const sombra = "#00000033", unha = "#ffffff59";
          const dedo = (x, y, dw, dh) => `<rect x="${x}" y="${y}" width="${dw}" height="${dh}" rx="${dw / 2}" fill="${pele}" stroke="${C.tinta}" stroke-width="3"/>` +
            `<rect x="${x + dw * 0.2}" y="${y + 3}" width="${dw * 0.6}" height="${dw * 0.55}" rx="${dw * 0.25}" fill="${unha}"/>` +
            `<path d="M${x + 3} ${y + dh * 0.45} L${x + dw - 3} ${y + dh * 0.45}" stroke="${sombra}" stroke-width="2.5"/>`;
          const dobrado = (x, y, dw) => `<rect x="${x}" y="${y}" width="${dw}" height="34" rx="${dw * 0.45}" fill="${pele}" stroke="${C.tinta}" stroke-width="3"/>` +
            `<path d="M${x + 4} ${y + 17} L${x + dw - 4} ${y + 17}" stroke="${sombra}" stroke-width="2.5"/>`;
          const palma = `<path d="M30 150 L28 96 Q28 80 46 78 L86 78 Q100 80 100 96 L98 150 Q96 162 64 162 Q32 162 30 150 Z" fill="${pele}" stroke="${C.tinta}" stroke-width="3"/>`;
          const pulso = `<rect x="22" y="168" width="76" height="40" rx="6" fill="${manga}"/><rect x="20" y="158" width="80" height="16" rx="5" fill="${punho}" stroke="${C.tinta}" stroke-width="2.5"/>`;
          const polegarAberto = `<path d="M33 130 Q15 124 8 102 Q4 87 15 85 Q25 85 29 99 L37 116 Z" fill="${pele}" stroke="${C.tinta}" stroke-width="3"/>`;
          const polegarFechado = `<path d="M30 122 Q44 104 70 106 Q84 110 76 121 Q58 124 38 136 Z" fill="${pele}" stroke="${C.tinta}" stroke-width="3"/>`;
          let s = pulso;
          if (pose === "aberta") s += palma + dedo(30, 26, 17, 66) + dedo(49, 14, 17, 78) + dedo(68, 22, 17, 70) + dedo(86, 40, 15, 54) + polegarAberto +
            `<path d="M44 132 Q64 122 86 132" stroke="${sombra}" stroke-width="3" fill="none"/>`;
          else if (pose === "pega") s += palma + dedo(30, 44, 17, 46) + dedo(49, 36, 17, 54) + dedo(68, 40, 17, 50) + dedo(86, 52, 15, 42) +
            `<path d="M33 130 Q22 118 22 104 Q24 92 32 96 L40 116 Z" fill="${pele}" stroke="${C.tinta}" stroke-width="3"/>`;
          else {
            if (pose === "caneta") s += `<g transform="rotate(-32 64 112)"><rect x="57" y="-8" width="15" height="180" rx="5" fill="${C.azul2}" stroke="${C.tinta}" stroke-width="3"/>` +
              `<path d="M57 172 L64.5 196 L72 172 Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="2.5"/><rect x="58" y="4" width="13" height="18" fill="${C.claro}" opacity=".6"/></g>`;
            s += palma.replace("M30 150 L28 96 Q28 80 46 78 L86 78 Q100 80 100 96", "M30 150 L28 90 Q28 74 46 72 L86 72 Q100 74 100 90");
            s += (pose === "aponta" ? dedo(30, 4, 18, 82) : dobrado(30, 70, 18)) + dobrado(49, 66, 18) + dobrado(68, 68, 18) + dobrado(86, 74, 15) + polegarFechado;
          }
          return `<g transform="scale(${w / 120} ${h / 210})">${recorteP(s)}</g>`;
        }
