
        // ── desenhos do C30 (o C36 reaproveita) que faltam nos bancos (o resto vem de personagens.js, elementos.js e _ajudantes.js) ──
        const VERDE = "#3c9a4f", VERDE2 = "#2b7a3b";
        // balão de fala de papel com o rabinho embaixo, para o lado "lado" (-1 = esquerda, 1 = direita)
        function balaoFala(w, h, lado, fundo = C.claro) {
          const hb = h * 0.8, bx = lado > 0 ? w * 0.7 : w * 0.3;
          return `<path d="M24 0 L${w - 24} 0 Q${w} 0 ${w} 24 L${w} ${hb - 24} Q${w} ${hb} ${w - 24} ${hb} L${bx + 22 * lado} ${hb} L${bx + 50 * lado} ${h} L${bx - 18 * lado} ${hb} L24 ${hb} Q0 ${hb} 0 ${hb - 24} L0 24 Q0 0 24 0 Z" fill="${fundo}" stroke="${C.tinta}" stroke-width="6" stroke-linejoin="round"/>`;
        }
        const coracao = (s, cor = C.verm) => `<path d="M${s / 2} ${s * 0.92} C ${-s * 0.1} ${s * 0.5}, ${s * 0.05} ${s * 0.02}, ${s / 2} ${s * 0.28} C ${s * 0.95} ${s * 0.02}, ${s * 1.1} ${s * 0.5}, ${s / 2} ${s * 0.92} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="3"/>`;
        function sol(s) {
          let r = "";
          for (let k = 0; k < 10; k++) r += `<rect x="${s / 2 - 4}" y="0" width="8" height="${s * 0.2}" rx="4" fill="${C.amar2}" transform="rotate(${k * 36} ${s / 2} ${s / 2})"/>`;
          return r + `<circle cx="${s / 2}" cy="${s / 2}" r="${s * 0.28}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/>`;
        }
        const nuvem = (w, h, cor = "#6b6880") => `<path d="M${w * 0.18} ${h} Q0 ${h} 0 ${h * 0.72} Q0 ${h * 0.45} ${w * 0.22} ${h * 0.45} Q${w * 0.26} ${h * 0.05} ${w * 0.55} ${h * 0.1} Q${w * 0.8} 0 ${w * 0.84} ${h * 0.4} Q${w} ${h * 0.42} ${w} ${h * 0.7} Q${w} ${h} ${w * 0.8} ${h} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="4"/>`;
        const raio = (w, h) => `<path d="M${w * 0.6} 0 L${w * 0.1} ${h * 0.55} L${w * 0.45} ${h * 0.55} L${w * 0.3} ${h} L${w * 0.92} ${h * 0.38} L${w * 0.55} ${h * 0.38} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>`;
        const gota = (w, h, cor = "#4a90c8") => `<path d="M${w / 2} 0 Q${w} ${h * 0.55} ${w * 0.9} ${h * 0.72} Q${w * 0.75} ${h} ${w / 2} ${h} Q${w * 0.25} ${h} ${w * 0.1} ${h * 0.72} Q0 ${h * 0.55} ${w / 2} 0 Z" fill="${cor}" stroke="${C.tinta}" stroke-width="3"/>`;

        // a fita da conta (calculadora de papel), deitada: corta-se e desenrola pelo clip-path
        function fitaConta(w, h, seed) {
          let s = `<path d="${pRet(w, h, seed, 1.4, 24)}" fill="#fbf7ee" stroke="${C.tinta}" stroke-width="3"/>`;
          const fs = Math.min(h * 0.3, 26);
          for (let x = 18, k = 0; x < w - 60; x += 118, k++) {
            s += fM(x, h * 0.42, "GASTO", fs * 0.8, C.tinta, "start", 0.75) + fM(x, h * 0.78, "R$ " + (["9", "7", "8", "6", "9"][k % 5]) + "00", fs * 0.8, C.verm, "start");
            s += `<rect x="${x + 100}" y="${h * 0.12}" width="2" height="${h * 0.76}" fill="${C.tinta}" opacity=".15"/>`;
          }
          return s;
        }
        // tesoura grande deitada, as pontas para a esquerda
        const tesouraN = (w, h) => `<circle cx="${w * 0.84}" cy="${h * 0.24}" r="${h * 0.18}" fill="none" stroke="${C.verm}" stroke-width="${h * 0.09}"/><circle cx="${w * 0.84}" cy="${h * 0.76}" r="${h * 0.18}" fill="none" stroke="${C.verm}" stroke-width="${h * 0.09}"/>` +
          `<path d="M${w * 0.7} ${h * 0.34} L0 ${h * 0.56} L${w * 0.06} ${h * 0.62} L${w * 0.72} ${h * 0.5} Z" fill="#c9ccd6" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.7} ${h * 0.66} L0 ${h * 0.44} L${w * 0.06} ${h * 0.38} L${w * 0.72} ${h * 0.5} Z" fill="#e3e5ec" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/><circle cx="${w * 0.6}" cy="${h * 0.5}" r="${h * 0.05}" fill="${C.tinta}"/>`;

        // a estatal: prédio com frontão, a gota de petróleo na fachada e a faixa ESTATAL
        function estatal(w, h) {
          return predio(w, h, "ESTATAL", C.kraft2) + `<g transform="translate(${w * 0.42} ${h * 0.4})">${gota(w * 0.16, h * 0.2, C.tinta)}</g>`;
        }
        // a cruzeta da marionete (as varetas cruzadas na mão de quem controla)
        const cruzeta = (w, h) => `<rect x="0" y="${h * 0.42}" width="${w}" height="${h * 0.16}" rx="6" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="3"/><rect x="${w * 0.42}" y="0" width="${w * 0.16}" height="${h}" rx="6" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="3"/>`;

        // aspirador: o corpo à esquerda, a mangueira e o bocal na ponta direita (onde as moedas entram)
        function aspirador(w, h) {
          const fs = caber("IMPOSTO", w * 0.34, h * 0.14);
          return `<path d="M${w * 0.3} ${h * 0.5} C ${w * 0.5} ${h * 0.95}, ${w * 0.7} ${h * 0.1}, ${w * 0.86} ${h * 0.46}" fill="none" stroke="${C.tinta}" stroke-width="${h * 0.11}" stroke-linecap="round"/>` +
            `<path d="M${w * 0.3} ${h * 0.5} C ${w * 0.5} ${h * 0.95}, ${w * 0.7} ${h * 0.1}, ${w * 0.86} ${h * 0.46}" fill="none" stroke="#6b6880" stroke-width="${h * 0.06}" stroke-linecap="round" stroke-dasharray="6 6"/>` +
            `<path d="M${w * 0.84} ${h * 0.3} L${w} ${h * 0.2} L${w} ${h * 0.74} L${w * 0.84} ${h * 0.62} Z" fill="${C.tinta}"/>` +
            `<rect x="0" y="${h * 0.3}" width="${w * 0.4}" height="${h * 0.6}" rx="${h * 0.12}" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/>${fT(w * 0.2, h * 0.62 + fs * 0.36, "IMPOSTO", fs, C.claro)}` +
            `<circle cx="${w * 0.08}" cy="${h * 0.92}" r="${h * 0.08}" fill="${C.tinta}"/><circle cx="${w * 0.32}" cy="${h * 0.92}" r="${h * 0.08}" fill="${C.tinta}"/>`;
        }
        // o saco da carga, com a palavra na frente e o nó em cima
        function sacoN(w, h, txt) {
          const fs = caber(txt, w * 0.78, h * 0.18);
          return `<path d="M${w * 0.36} ${h * 0.14} L${w * 0.64} ${h * 0.14} L${w * 0.6} ${h * 0.26} Q${w * 1.02} ${h * 0.44} ${w * 0.94} ${h * 0.82} Q${w * 0.86} ${h} ${w / 2} ${h} Q${w * 0.14} ${h} ${w * 0.06} ${h * 0.82} Q${-w * 0.02} ${h * 0.44} ${w * 0.4} ${h * 0.26} Z" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
            `<path d="M${w * 0.34} ${h * 0.14} Q${w / 2} 0 ${w * 0.66} ${h * 0.14}" fill="none" stroke="${C.tinta}" stroke-width="6"/>${fT(w / 2, h * 0.64 + fs * 0.36, txt, fs, C.tinta)}`;
        }
        // ponte de papel em arco (da esquerda para a direita)
        const ponteN = (w, h) => `<path d="M0 ${h} Q${w / 2} ${-h * 0.6} ${w} ${h} L${w} ${h * 0.8} Q${w / 2} ${-h * 0.95} 0 ${h * 0.8} Z" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="4"/>` +
          [0.2, 0.35, 0.5, 0.65, 0.8].map((f) => { const y = h - 4 * (f * (1 - f)) * h * 1.25; return `<rect x="${w * f - 3}" y="${y}" width="6" height="${h - y}" fill="${C.tinta}" opacity=".5"/>`; }).join("");

        // globo de papel: oceano, continentes simplificados, meridianos e o pino do Brasil (em 0,38w · 0,62h)
        function globoN(d) {
          const r = d / 2;
          let s = `<circle cx="${r}" cy="${r}" r="${r - 3}" fill="#9fc3e8" stroke="${C.tinta}" stroke-width="6"/>`;
          s += `<path d="M${d * 0.3} ${d * 0.42} Q${d * 0.44} ${d * 0.44} ${d * 0.46} ${d * 0.56} Q${d * 0.44} ${d * 0.78} ${d * 0.38} ${d * 0.86} Q${d * 0.32} ${d * 0.7} ${d * 0.28} ${d * 0.56} Z" fill="#6fb36f" stroke="${C.tinta}" stroke-width="3"/>`;
          s += `<path d="M${d * 0.52} ${d * 0.22} Q${d * 0.7} ${d * 0.14} ${d * 0.84} ${d * 0.3} Q${d * 0.82} ${d * 0.44} ${d * 0.68} ${d * 0.44} Q${d * 0.62} ${d * 0.6} ${d * 0.6} ${d * 0.74} Q${d * 0.54} ${d * 0.6} ${d * 0.52} ${d * 0.44} Q${d * 0.46} ${d * 0.34} ${d * 0.52} ${d * 0.22} Z" fill="#6fb36f" stroke="${C.tinta}" stroke-width="3"/>`;
          s += `<path d="M${d * 0.16} ${d * 0.26} Q${d * 0.3} ${d * 0.14} ${d * 0.4} ${d * 0.24} Q${d * 0.36} ${d * 0.36} ${d * 0.24} ${d * 0.36} Z" fill="#6fb36f" stroke="${C.tinta}" stroke-width="3"/>`;
          s += `<ellipse cx="${r}" cy="${r}" rx="${r * 0.42}" ry="${r - 3}" fill="none" stroke="${C.tinta}" stroke-width="2" opacity=".35"/><path d="M6 ${r} L${d - 6} ${r}" stroke="${C.tinta}" stroke-width="2" opacity=".35"/>`;
          return s + `<circle cx="${d * 0.38}" cy="${d * 0.62}" r="${d * 0.035}" fill="${C.verm}" stroke="${C.claro}" stroke-width="3"/>`;
        }
        function bandeiraEUA(w, h) {
          let s = `<rect width="${w}" height="${h}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>`;
          for (let k = 0; k < 7; k++) s += `<rect y="${(k * 2 * h) / 13}" width="${w}" height="${h / 13}" fill="${C.verm}"/>`;
          s += `<rect width="${w * 0.42}" height="${(h * 7) / 13}" fill="${C.azul2}"/>`;
          for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) s += `<circle cx="${w * 0.06 + c * w * 0.1}" cy="${h * 0.08 + r * h * 0.16}" r="${Math.max(1.5, w * 0.018)}" fill="${C.claro}"/>`;
          return s + `<rect width="${w}" height="${h}" fill="none" stroke="${C.tinta}" stroke-width="3"/>`;
        }
        function bandeiraChina(w, h) {
          let s = `<rect width="${w}" height="${h}" fill="#d93a2b" stroke="${C.tinta}" stroke-width="3"/>${ic(w * 0.07, h * 0.12, (w * 0.22) / 40, estrela(20, C.amar))}`;
          [[0.34, 0.08], [0.42, 0.2], [0.42, 0.36], [0.34, 0.48]].forEach(([fx, fy]) => { s += ic(w * fx, h * fy, (w * 0.07) / 40, estrela(20, C.amar)); });
          return s;
        }
        function bandeiraBR(w, h) {
          return `<rect width="${w}" height="${h}" fill="${VERDE}" stroke="${C.tinta}" stroke-width="3"/><path d="M${w / 2} ${h * 0.1} L${w * 0.92} ${h / 2} L${w / 2} ${h * 0.9} L${w * 0.08} ${h / 2} Z" fill="${C.amar}"/><circle cx="${w / 2}" cy="${h / 2}" r="${h * 0.22}" fill="${C.azul2}"/>`;
        }
        // mastro com bandeira (a bandeira em cima à direita do mastro)
        const mastro = (w, h, band) => `<rect x="0" y="0" width="7" height="${h}" fill="${C.tinta}"/><g transform="translate(7 4)">${band(w - 7, (w - 7) * 0.62)}</g>`;
        // navio cargueiro com contêineres coloridos (proa para a direita)
        function navioN(w, h, cores) {
          let s = `<path d="M0 ${h * 0.55} L${w} ${h * 0.55} L${w * 0.86} ${h} L${w * 0.08} ${h} Z" fill="${C.tinta}"/><rect x="0" y="${h * 0.55}" width="${w}" height="${h * 0.08}" fill="${C.verm}"/>`;
          const cw = (w * 0.6) / 4;
          cores.forEach((c, k) => { const col = k % 4, lin = Math.floor(k / 4); s += `<rect x="${w * 0.1 + col * cw}" y="${h * 0.55 - (lin + 1) * h * 0.18}" width="${cw - 3}" height="${h * 0.17}" fill="${c}" stroke="${C.tinta}" stroke-width="2"/>`; });
          return s + `<rect x="${w * 0.76}" y="${h * 0.18}" width="${w * 0.13}" height="${h * 0.37}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/><rect x="${w * 0.78}" y="${h * 0.24}" width="${w * 0.09}" height="${h * 0.06}" fill="#9fc3e8"/>`;
        }
        // cais: as tábuas e a água
        const cais = (w, h) => `<rect y="${h * 0.55}" width="${w}" height="${h * 0.45}" fill="#9fc3e8" opacity=".6"/><rect width="${w}" height="${h * 0.3}" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="3"/>` +
          [0.15, 0.45, 0.75].map((f) => `<rect x="${w * f}" y="${h * 0.3}" width="${w * 0.06}" height="${h * 0.6}" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="2"/>`).join("");

        // o braço do juiz: manga preta, punho branco e a mão segurando o cartão (cartão em cima)
        function bracoJuiz(w, h, cor = C.amar) {
          return recorteP(`<rect x="${w * 0.3}" y="${h * 0.46}" width="${w * 0.4}" height="${h * 0.54}" rx="12" fill="#15131f"/><rect x="${w * 0.27}" y="${h * 0.42}" width="${w * 0.46}" height="${h * 0.08}" rx="5" fill="${C.claro}"/>` +
            `<ellipse cx="${w / 2}" cy="${h * 0.38}" rx="${w * 0.24}" ry="${h * 0.08}" fill="${PELE[1]}"/>` +
            `<rect x="${w * 0.2}" y="0" width="${w * 0.6}" height="${h * 0.36}" rx="8" fill="${cor}" stroke="${C.tinta}" stroke-width="4" transform="rotate(-8 ${w / 2} ${h * 0.2})"/>`);
        }
        const cartaoA = (s) => `<rect x="${s * 0.18}" y="2" width="${s * 0.64}" height="${s - 4}" rx="${s * 0.08}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="${Math.max(2, s * 0.05)}" transform="rotate(-8 ${s / 2} ${s / 2})"/>`;
        // a mão espalmada do "mais ou menos"
        const maoPlana = (w, h, pele = PELE[1]) => recorteP(`<rect x="0" y="${h * 0.36}" width="${w * 0.3}" height="${h * 0.3}" rx="8" fill="${C.tinta}"/><rect x="${w * 0.28}" y="${h * 0.28}" width="${w * 0.4}" height="${h * 0.46}" rx="${h * 0.14}" fill="${pele}" stroke="${C.tinta}" stroke-width="3"/>` +
          [0.22, 0.38, 0.54, 0.7].map((f) => `<rect x="${w * 0.62}" y="${h * f}" width="${w * 0.36}" height="${h * 0.12}" rx="${h * 0.06}" fill="${pele}" stroke="${C.tinta}" stroke-width="3"/>`).join(""));
        // capacete de obra vazio, com a chave inglesa e o martelo no chão
        function capaceteN(w, h) {
          return recorteP(`<path d="M${w * 0.12} ${h * 0.5} Q${w * 0.14} ${h * 0.06} ${w / 2} ${h * 0.06} Q${w * 0.86} ${h * 0.06} ${w * 0.88} ${h * 0.5} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/><rect x="${w * 0.04}" y="${h * 0.48}" width="${w * 0.92}" height="${h * 0.09}" rx="6" fill="${C.amar2}" stroke="${C.tinta}" stroke-width="4"/><rect x="${w * 0.46}" y="${h * 0.08}" width="${w * 0.08}" height="${h * 0.4}" fill="${C.amar2}"/>` +
            `<rect x="${w * 0.08}" y="${h * 0.8}" width="${w * 0.42}" height="${h * 0.07}" rx="4" fill="#8a8f9c" stroke="${C.tinta}" stroke-width="3" transform="rotate(-12 ${w * 0.3} ${h * 0.83})"/><circle cx="${w * 0.1}" cy="${h * 0.86}" r="${h * 0.07}" fill="#8a8f9c" stroke="${C.tinta}" stroke-width="3"/>` +
            `<rect x="${w * 0.56}" y="${h * 0.84}" width="${w * 0.38}" height="${h * 0.06}" rx="3" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="3"/><rect x="${w * 0.86}" y="${h * 0.74}" width="${w * 0.1}" height="${h * 0.24}" rx="3" fill="#6b6880" stroke="${C.tinta}" stroke-width="3"/>`);
        }

        // ── o PLACAR (o fio do vídeo) ─────────────────────────────────────────
        const LINHAS = ["GASTO", "ESTATAIS", "IMPOSTOS", "SOCIAIS", "MUNDO"];
        // geometria do placar de w × h: cabeçalho, coluna dos nomes e as duas colunas; exec = mais uma linha embaixo
        function placarGeo(w, h, exec = false, clf = 0.4) {
          const hc = h * (exec ? 0.13 : 0.16), n = exec ? 6 : 5, hl = (h - hc) / n, cl = w * clf, cw = (w - cl) / 2;
          return { hc, hl, cl, cw, cel: (r, q) => [cl + (q === "f" ? cw : 0) + cw / 2, hc + r * hl + hl / 2] };
        }
        // nomes: o rótulo de cada linha (o placar do canto usa os números 1 a 5, do capítulo); clf: a fração da coluna dos nomes
        function placarN(w, h, exec = false, titulo = "", nomes0 = LINHAS, clf = 0.4) {
          const g = placarGeo(w, h, exec, clf);
          let s = `<path d="${pRet(w, h, 3030, 1.6, 36)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="${Math.max(3, w * 0.008)}"/>`;
          s += `<rect x="${g.cl}" y="0" width="${g.cw}" height="${g.hc}" fill="${C.verm}"/><rect x="${g.cl + g.cw}" y="0" width="${g.cw}" height="${g.hc}" fill="${C.azul}"/>`;
          const fn = Math.min(caber("FLÁVIO", g.cw, g.hc * 0.55), caber("LULA", g.cw, g.hc * 0.55));
          s += fT(g.cl + g.cw / 2, g.hc / 2 + fn * 0.36, "LULA", fn, C.claro) + fT(g.cl + g.cw * 1.5, g.hc / 2 + fn * 0.36, "FLÁVIO", fn, C.claro);
          if (titulo) { const ft = caber(titulo, g.cl, g.hc * 0.42); s += fT(g.cl / 2, g.hc / 2 + ft * 0.36, titulo, ft, C.tinta); }
          const nomes = exec ? nomes0.concat(["EXECUÇÃO"]) : nomes0;
          const fl = Math.min(...nomes.map((t) => caber(t, g.cl * 0.92, g.hl * 0.42)));
          nomes.forEach((t, r) => {
            const y = g.hc + r * g.hl;
            if (exec && r === 5) s += `<rect x="0" y="${y}" width="${w}" height="${g.hl}" fill="${C.kraft}" opacity=".55"/>`;
            s += `<rect x="${w * 0.03}" y="${y - 1.5}" width="${w * 0.94}" height="3" fill="${C.tinta}" opacity="${r ? 0.2 : 0.45}"/>`;
            s += fT(g.cl * 0.08, y + g.hl / 2 + fl * 0.36, t, fl, exec && r === 5 ? C.verm2 : C.tinta, "start");
          });
          s += `<rect x="${g.cl - 1.5}" y="${g.hc}" width="3" height="${h - g.hc - 8}" fill="${C.tinta}" opacity=".25"/><rect x="${g.cl + g.cw - 1.5}" y="${g.hc}" width="3" height="${h - g.hc - 8}" fill="${C.tinta}" opacity=".25"/>`;
          return s;
        }
        // o desenho de uma nota: "x" vermelho, "a" cartão amarelo, "v" verde
        const notaSVG = (tipo, s) => tipo === "x" ? xisN(s) : tipo === "v" ? vistoN(s, VERDE) : cartaoA(s);

        // ── desenhos do C36 ───────────────────────────────────────────────────
        // termômetro da REJEIÇÃO (o líquido é um obj à parte, para encher com scaleY)
        const termoN = (w, h) => `<rect x="${w * 0.3}" y="4" width="${w * 0.4}" height="${h * 0.74}" rx="${w * 0.2}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="6"/>` +
          `<circle cx="${w / 2}" cy="${h * 0.82}" r="${w * 0.36}" fill="${C.verm}" stroke="${C.tinta}" stroke-width="6"/>` +
          [0, 1, 2, 3, 4].map((k) => `<rect x="${w * 0.74}" y="${h * 0.12 + k * h * 0.12}" width="${w * 0.16}" height="5" fill="${C.tinta}" opacity=".5"/>`).join("");
        // urna de papel com a fenda e a etiqueta
        const urnaN = (w, h, txt) => `<path d="${pRet(w, h * 0.78, 361, 2, 30)}" transform="translate(0 ${h * 0.22})" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="M${w * 0.08} ${h * 0.22} L${w * 0.2} 0 L${w * 0.8} 0 L${w * 0.92} ${h * 0.22} Z" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<rect x="${w * 0.3}" y="${h * 0.08}" width="${w * 0.4}" height="${h * 0.06}" rx="6" fill="${C.tinta}"/>` +
          `<rect x="${w * 0.12}" y="${h * 0.48}" width="${w * 0.76}" height="${h * 0.24}" fill="${C.azul}"/>${fT(w / 2, h * 0.6 + caber(txt, w * 0.7, h * 0.13) * 0.36, txt, caber(txt, w * 0.7, h * 0.13), C.claro)}`;
        // cédula de voto com o nome
        const cedulaN = (w, h, nome, cor) => `<path d="${pRet(w, h, 373, 1.5, 24)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="${w * 0.08}" y="${h * 0.14}" width="${h * 0.3}" height="${h * 0.3}" fill="none" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w * 0.09} ${h * 0.28} L${w * 0.13} ${h * 0.4} L${w * 0.2} ${h * 0.1}" fill="none" stroke="${cor}" stroke-width="6" stroke-linecap="round"/>` +
          fT(w * 0.62, h * 0.38, nome, caber(nome, w * 0.6, h * 0.3), cor) +
          `<rect x="${w * 0.08}" y="${h * 0.6}" width="${w * 0.84}" height="6" fill="${C.tinta}" opacity=".2"/><rect x="${w * 0.08}" y="${h * 0.76}" width="${w * 0.6}" height="6" fill="${C.tinta}" opacity=".2"/>`;
        // a coluna de papel com o título e as linhas (os itens entram por cima, como tags)
        const colunaN = (w, h, titulo, cor, seed) => `<path d="${pRet(w, h, seed, 2.4, 36)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="${pRet(w, h * 0.16, seed + 9, 2, 30)}" fill="${cor}"/>${fT(w / 2, h * 0.08 + caber(titulo, w * 0.9, h * 0.1) * 0.36, titulo, caber(titulo, w * 0.9, h * 0.1), C.claro)}`;
        // chama (o "combustível" da rejeição)
        const chamaN = (w, h) => `<path d="M${w / 2} 0 Q${w * 0.95} ${h * 0.45} ${w * 0.82} ${h * 0.78} Q${w * 0.7} ${h} ${w / 2} ${h} Q${w * 0.3} ${h} ${w * 0.18} ${h * 0.78} Q${w * 0.05} ${h * 0.45} ${w * 0.38} ${h * 0.3} Q${w * 0.42} ${h * 0.5} ${w * 0.5} ${h * 0.55} Q${w * 0.42} ${h * 0.25} ${w / 2} 0 Z" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w / 2} ${h * 0.45} Q${w * 0.72} ${h * 0.7} ${w * 0.62} ${h * 0.88} Q${w / 2} ${h * 0.98} ${w * 0.38} ${h * 0.88} Q${w * 0.3} ${h * 0.7} ${w / 2} ${h * 0.45} Z" fill="${C.amar}"/>`;
        // seta grossa de papel (para a direita)
        const setaN = (w, h, cor = C.tinta) => `<path d="M0 ${h * 0.32} L${w * 0.62} ${h * 0.32} L${w * 0.62} 0 L${w} ${h / 2} L${w * 0.62} ${h} L${w * 0.62} ${h * 0.68} L0 ${h * 0.68} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="3" stroke-linejoin="round"/>`;

        // ── desenhos do C37 ───────────────────────────────────────────────────
        // chupeta: o escudo, o bico e a argola
        const chupetaN = (w, h) => `<ellipse cx="${w * 0.5}" cy="${h * 0.42}" rx="${w * 0.46}" ry="${h * 0.3}" fill="${C.rosa}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<circle cx="${w * 0.5}" cy="${h * 0.42}" r="${h * 0.1}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>` +
          `<circle cx="${w * 0.5}" cy="${h * 0.8}" r="${h * 0.17}" fill="none" stroke="${C.azul}" stroke-width="${h * 0.07}"/>`;
        // barra de papel (o líquido cresce de baixo: transformOrigin no pé)
        const barraN = (w, h, cor, seed) => `<path d="${pRet(w, h, seed, 1.6, 28)}" fill="${cor}" stroke="${C.tinta}" stroke-width="4"/>`;
        // recibo de papel com picote embaixo
        function reciboN(w, h, seed) {
          let pic = "";
          for (let x = 0; x < w; x += 24) pic += `L${x + 12} ${h - 12} L${x + 24} ${h} `;
          return `<path d="M0 0 L${w} 0 L${w} ${h} ${pic.replace(/^L/, "L")} L0 ${h} Z" fill="#fbf8f0" stroke="${C.tinta}" stroke-width="4"/>` +
            [1, 2, 3, 4].map((k) => `<rect x="24" y="${(h * k) / 5}" width="${w - 48}" height="2" fill="${C.tinta}" opacity=".15"/>`).join("");
        }
        // barra horizontal do imóvel: pago (verde) × devendo (vermelho); o verde é outro obj, que cresce
        const faixaN = (w, h) => `<rect width="${w}" height="${h}" rx="${h / 2}" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4"/>`;
        // microfone de palco
        const microN = (w, h) => `<rect x="${w * 0.47}" y="${h * 0.35}" width="${w * 0.06}" height="${h * 0.6}" fill="${C.tinta}"/>` +
          `<ellipse cx="${w / 2}" cy="${h * 0.2}" rx="${w * 0.2}" ry="${h * 0.2}" fill="#4a4858" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="${w * 0.25}" y="${h * 0.93}" width="${w * 0.5}" height="${h * 0.07}" rx="4" fill="${C.tinta}"/>`;
        // ── caricatura do Nikolas (pedido do Mickael, 08/10: "beeem parecido"; a referência é a foto do TSE que o Raul
        // mostra no vídeo): rosto redondo e jovem, cabelo castanho com volume em cima, sorriso largo com os dentes, blazer
        // azul e camisa branca aberta. Desenho em 400 × 500; "corpo" sem olhos e boca, que vêm por cima na expressão.
        const PELE_N = "#f2c9a6", CAB_N = "#5c3b25", CAB_N2 = "#7a5235", AZUL_N = "#2a5bb5", AZUL_N2 = "#1f4690";
        function nikolasN(w, h, parte) {
          // 2ª versão (2ª prévia: "a imagem do Nikolas pode ser ainda melhor"): rosto oval de bochecha cheia com sombra do
          // lado, olhos com íris, cabelo castanho com volume e risca do lado, mechas claras, orelhas com dobra, pescoço com
          // sombra, blazer azul royal com lapela e camisa branca aberta
          const SOMB = "#dfaa86", LAB = "#c9706a";
          let s = "";
          if (parte === "corpo") {
            s = `<path d="M166 288 L234 288 L238 358 L162 358 Z" fill="${PELE_N}" stroke="${C.tinta}" stroke-width="5"/>` +
              `<path d="M168 300 Q200 326 232 300 L234 322 Q200 344 166 322 Z" fill="${SOMB}"/>` +
              `<path d="M14 500 L24 428 Q50 366 138 348 L262 348 Q350 366 376 428 L386 500 Z" fill="${AZUL_N}" stroke="${C.tinta}" stroke-width="6" stroke-linejoin="round"/>` +
              `<path d="M56 420 Q60 470 52 500 M344 420 Q340 470 348 500" fill="none" stroke="${AZUL_N2}" stroke-width="6" stroke-linecap="round"/>` +
              `<path d="M154 348 L200 452 L246 348 Z" fill="#fbfbf7" stroke="${C.tinta}" stroke-width="4"/>` +
              `<path d="M176 350 L200 404 L224 350 Q200 366 176 350 Z" fill="${PELE_N}"/>` +
              `<path d="M156 346 L182 398 L198 356 L170 340 Z M244 346 L218 398 L202 356 L230 340 Z" fill="#ffffff" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
              `<path d="M140 350 L198 456 L168 486 L122 404 Z" fill="${AZUL_N2}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
              `<path d="M260 350 L202 456 L232 486 L278 404 Z" fill="${AZUL_N2}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
              // orelhas com a dobra
              `<path d="M110 196 Q84 186 86 214 Q88 246 116 244 Z" fill="${PELE_N}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/><path d="M104 206 Q94 214 102 230" fill="none" stroke="${SOMB}" stroke-width="5" stroke-linecap="round"/>` +
              `<path d="M290 196 Q316 186 314 214 Q312 246 284 244 Z" fill="${PELE_N}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/><path d="M296 206 Q306 214 298 230" fill="none" stroke="${SOMB}" stroke-width="5" stroke-linecap="round"/>` +
              // rosto oval, bochecha cheia e o queixo largo
              `<path d="M110 178 Q106 108 200 102 Q294 108 290 178 Q294 252 266 294 Q238 332 200 334 Q162 332 134 294 Q106 252 110 178 Z" fill="${PELE_N}" stroke="${C.tinta}" stroke-width="6"/>` +
              `<path d="M276 210 Q284 262 254 300 Q232 324 204 330 Q244 312 264 276 Q276 248 276 210 Z" fill="${SOMB}" opacity=".7"/>` +
              `<ellipse cx="140" cy="258" rx="24" ry="14" fill="${C.rosa}" opacity=".5"/><ellipse cx="260" cy="258" rx="24" ry="14" fill="${C.rosa}" opacity=".5"/>` +
              // cabelo: volume alto, risca do lado esquerdo da imagem, mechas jogadas para a direita, costeletas curtas
              `<path d="M106 190 Q90 128 116 92 Q146 52 204 44 Q268 40 298 84 Q318 116 300 186 Q298 156 284 140 Q274 124 252 122 Q258 108 238 100 Q212 114 180 106 Q150 108 136 124 Q120 142 120 190 Z" fill="${CAB_N}" stroke="${C.tinta}" stroke-width="6" stroke-linejoin="round"/>` +
              `<path d="M150 98 Q142 72 170 58" fill="none" stroke="#3a2416" stroke-width="5" stroke-linecap="round"/>` +
              `<path d="M174 74 Q226 50 284 86 M160 92 Q220 70 270 104 M190 58 Q240 46 276 66" fill="none" stroke="${CAB_N2}" stroke-width="7" stroke-linecap="round"/>` +
              `<path d="M108 190 L112 228 L122 228 L120 190 Z M292 186 L288 228 L278 228 L280 186 Z" fill="${CAB_N}"/>` +
              // sobrancelhas grossas
              `<path d="M136 186 Q160 172 188 180" fill="none" stroke="#3a2416" stroke-width="12" stroke-linecap="round"/><path d="M212 180 Q240 172 264 186" fill="none" stroke="#3a2416" stroke-width="12" stroke-linecap="round"/>` +
              // nariz com a sombra da asa
              `<path d="M202 210 Q192 244 198 256 Q208 264 220 256" fill="none" stroke="${C.tinta}" stroke-width="5" stroke-linecap="round"/><path d="M186 254 Q190 262 198 262" fill="none" stroke="${SOMB}" stroke-width="5" stroke-linecap="round"/>`;
          } else if (parte === "sorriso") {
            // o sorrisão: olhos apertados de quem ri (com a ruga), dentes de cima e lábio de baixo
            s = `<path d="M138 214 Q162 196 186 212" fill="none" stroke="${C.tinta}" stroke-width="8" stroke-linecap="round"/><path d="M214 212 Q238 196 262 214" fill="none" stroke="${C.tinta}" stroke-width="8" stroke-linecap="round"/>` +
              `<path d="M134 222 Q140 230 150 230 M266 222 Q260 230 250 230" fill="none" stroke="${SOMB}" stroke-width="4" stroke-linecap="round"/>` +
              `<path d="M142 268 Q200 340 258 268 Q200 280 142 268 Z" fill="#6e1c1c" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
              `<path d="M150 272 Q200 282 250 272 L244 290 Q200 300 156 290 Z" fill="#ffffff"/>` +
              `<path d="M174 276 L176 294 M200 278 L200 298 M226 276 L224 294" stroke="#ddd8d0" stroke-width="2"/>` +
              `<path d="M176 312 Q200 324 224 312" fill="none" stroke="${LAB}" stroke-width="5" stroke-linecap="round"/>` +
              `<path d="M128 262 Q134 274 128 284 M272 262 Q266 274 272 284" fill="none" stroke="${C.tinta}" stroke-width="4" stroke-linecap="round"/>`;
          } else {
            // olhos abertos com íris castanha e brilho; boca pequena ("o") ou neutra
            const olho = (cx) => `<ellipse cx="${cx}" cy="212" rx="17" ry="11" fill="#ffffff" stroke="${C.tinta}" stroke-width="4"/><circle cx="${cx + 1}" cy="213" r="8" fill="#5a3a22"/><circle cx="${cx + 1}" cy="213" r="4" fill="${C.tinta}"/><circle cx="${cx + 4}" cy="209" r="2.5" fill="#ffffff"/>`;
            s = olho(160) + olho(240) +
              (parte === "o" ? `<ellipse cx="200" cy="288" rx="16" ry="20" fill="#6e1c1c" stroke="${C.tinta}" stroke-width="4"/>`
                             : `<path d="M166 282 Q200 302 234 282" fill="none" stroke="${C.tinta}" stroke-width="6" stroke-linecap="round"/><path d="M182 304 Q200 310 218 304" fill="none" stroke="${LAB}" stroke-width="4" stroke-linecap="round"/>`);
          }
          return `<g transform="scale(${w / 400} ${h / 500})">${s}</g>`;
        }
        // chocalho de bebê
        const chocalhoN = (w, h) => `<rect x="${w * 0.44}" y="${h * 0.45}" width="${w * 0.12}" height="${h * 0.5}" rx="${w * 0.06}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<circle cx="${w / 2}" cy="${h * 0.28}" r="${w * 0.27}" fill="${C.rosa}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<circle cx="${w * 0.4}" cy="${h * 0.22}" r="${w * 0.05}" fill="${C.claro}"/><circle cx="${w * 0.58}" cy="${h * 0.32}" r="${w * 0.05}" fill="${C.claro}"/>`;

        // ── desenhos do C38 ───────────────────────────────────────────────────
        // bolsa de luxo: a alça em arco, o corpo trapézio com a aba, o fecho dourado e o pespontado
        const bolsaN = (w, h, cor = "#8a2f45", cor2 = "#6c2236") => `<path d="M${w * 0.3} ${h * 0.36} Q${w * 0.3} ${h * 0.04} ${w / 2} ${h * 0.04} Q${w * 0.7} ${h * 0.04} ${w * 0.7} ${h * 0.36}" fill="none" stroke="${C.tinta}" stroke-width="${w * 0.07}" stroke-linecap="round"/>` +
          `<path d="M${w * 0.3} ${h * 0.36} Q${w * 0.3} ${h * 0.06} ${w / 2} ${h * 0.06} Q${w * 0.7} ${h * 0.06} ${w * 0.7} ${h * 0.36}" fill="none" stroke="${cor2}" stroke-width="${w * 0.035}" stroke-linecap="round"/>` +
          `<path d="M${w * 0.12} ${h * 0.34} L${w * 0.88} ${h * 0.34} L${w * 0.97} ${h * 0.97} L${w * 0.03} ${h * 0.97} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.12} ${h * 0.34} L${w * 0.88} ${h * 0.34} L${w * 0.84} ${h * 0.6} Q${w / 2} ${h * 0.7} ${w * 0.16} ${h * 0.6} Z" fill="${cor2}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.16} ${h * 0.9} L${w * 0.84} ${h * 0.9}" stroke="${C.claro}" stroke-width="2" stroke-dasharray="8 7" opacity=".55"/>` +
          `<rect x="${w * 0.42}" y="${h * 0.58}" width="${w * 0.16}" height="${h * 0.12}" rx="4" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/>`;
        // avião de papel visto de lado (bico para a direita)
        const aviaoN = (w, h) => `<path d="M${w * 0.04} ${h * 0.5} Q${w * 0.04} ${h * 0.36} ${w * 0.2} ${h * 0.36} L${w * 0.86} ${h * 0.36} Q${w} ${h * 0.4} ${w} ${h * 0.5} Q${w} ${h * 0.6} ${w * 0.86} ${h * 0.64} L${w * 0.2} ${h * 0.64} Q${w * 0.04} ${h * 0.64} ${w * 0.04} ${h * 0.5} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w * 0.4} ${h * 0.6} L${w * 0.62} ${h * 0.6} L${w * 0.42} ${h} L${w * 0.3} ${h} Z" fill="${C.azul}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.08} ${h * 0.4} L${w * 0.04} 0 L${w * 0.16} 0 L${w * 0.26} ${h * 0.38} Z" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          [0, 1, 2, 3, 4].map((k) => `<circle cx="${w * (0.36 + k * 0.1)}" cy="${h * 0.46}" r="${h * 0.04}" fill="${C.azul2}"/>`).join("");
        // barra de busca: a caixa branca arredondada e a lupa (o texto é um rótulo por cima)
        const buscaN = (w, h) => `<rect x="2" y="2" width="${w - 4}" height="${h - 4}" rx="${h / 2}" fill="#ffffff" stroke="${C.tinta}" stroke-width="5"/>` +
          `<circle cx="${h * 0.52}" cy="${h * 0.46}" r="${h * 0.2}" fill="none" stroke="${C.tinta}" stroke-width="5"/><path d="M${h * 0.66} ${h * 0.6} L${h * 0.8} ${h * 0.74}" stroke="${C.tinta}" stroke-width="7" stroke-linecap="round"/>`;
        // a régua POUCO | MÉDIO | MUITO: vermelho, verde, vermelho (os nomes vão por cima, como rótulos)
        const reguaN = (w, h) => `<rect x="2" y="2" width="${w * 0.32}" height="${h - 4}" rx="14" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="${w * 0.34}" y="2" width="${w * 0.32}" height="${h - 4}" rx="14" fill="${VERDE}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="${w * 0.68 - 2}" y="2" width="${w * 0.32}" height="${h - 4}" rx="14" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4"/>`;
        // o ponteiro da régua (triângulo para baixo)
        const ponteiroN = (w, h) => `<path d="M4 4 L${w - 4} 4 L${w / 2} ${h - 4} Z" fill="${C.tinta}" stroke="${C.claro}" stroke-width="4" stroke-linejoin="round"/>`;

        // ── desenhos do C39 ───────────────────────────────────────────────────
        // pilha de papel: folhas finas umas sobre as outras, cada uma um pouco torta (o desenho cresce do pé)
        function pilhaPapelN(w, h, n = 26) {
          let s = "";
          const fh = h / n;
          for (let k = 0; k < n; k++) {
            const y = h - (k + 1) * fh, dx = (rnd(k * 7 + 3) - 0.5) * w * 0.12, rot = (rnd(k * 13 + 5) - 0.5) * 4;
            s += `<g transform="translate(${w / 2 + dx} ${y + fh / 2}) rotate(${rot})"><rect x="${-w * 0.42}" y="${-fh * 0.55}" width="${w * 0.84}" height="${fh * 1.1}" rx="2" fill="${k % 3 ? C.claro : "#efe6d3"}" stroke="${C.tinta}" stroke-width="2.5"/>` +
              `<rect x="${-w * 0.3}" y="-1.5" width="${w * 0.5 * (0.5 + rnd(k + 9) * 0.5)}" height="3" fill="${C.tinta}" opacity=".18"/></g>`;
          }
          return s;
        }
        // carrinho de supermercado (de lado, alça à esquerda)
        const carrinhoN = (w, h) => `<path d="M${w * 0.02} ${h * 0.08} L${w * 0.16} ${h * 0.08} L${w * 0.26} ${h * 0.68} L${w * 0.9} ${h * 0.68}" fill="none" stroke="${C.tinta}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.19} ${h * 0.22} L${w * 0.98} ${h * 0.22} L${w * 0.9} ${h * 0.58} L${w * 0.25} ${h * 0.58} Z" fill="#b9c3d6" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          [0.38, 0.52, 0.66, 0.8].map((x) => `<path d="M${w * x} ${h * 0.24} L${w * (x - 0.02)} ${h * 0.56}" stroke="${C.tinta}" stroke-width="3" opacity=".5"/>`).join("") +
          `<circle cx="${w * 0.34}" cy="${h * 0.84}" r="${h * 0.1}" fill="${C.tinta}"/><circle cx="${w * 0.82}" cy="${h * 0.84}" r="${h * 0.1}" fill="${C.tinta}"/>`;
        // boleto: faixa de cima, linhas, valor e o código de barras
        function boletoN(w, h) {
          const ft = caber("BOLETO", w * 0.4, h * 0.12), fv = caber("VENCE DIA 30", w * 0.45, h * 0.08);
          let s = `<path d="${pRet(w, h, 391, 1.4, 30)}" fill="#fbf8f0" stroke="${C.tinta}" stroke-width="5"/>` +
            `<rect x="0" y="0" width="${w}" height="${h * 0.2}" fill="${C.azul2}"/>${fT(w * 0.25, h * 0.1 + ft * 0.36, "BOLETO", ft, C.claro)}` +
            fT(w * 0.72, h * 0.1 + fv * 0.36, "VENCE DIA 30", fv, C.amar);
          for (let k = 0; k < 3; k++) s += `<rect x="${w * 0.06}" y="${h * (0.3 + k * 0.1)}" width="${w * (0.4 + rnd(k + 41) * 0.3)}" height="${h * 0.025}" fill="${C.tinta}" opacity=".2"/>`;
          let x = w * 0.06;
          for (let k = 0; x < w * 0.94; k++) { const bw = 2 + Math.floor(rnd(k + 77) * 3) * 2; s += `<rect x="${x}" y="${h * 0.66}" width="${bw}" height="${h * 0.24}" fill="${C.tinta}"/>`; x += bw + 3 + Math.floor(rnd(k + 91) * 3) * 2; }
          return s;
        }
        // cartão de crédito
        const cartaoN = (w, h) => `<rect x="2" y="2" width="${w - 4}" height="${h - 4}" rx="${h * 0.1}" fill="${C.azul}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="0" y="${h * 0.22}" width="${w}" height="${h * 0.16}" fill="${C.tinta}"/><rect x="${w * 0.1}" y="${h * 0.5}" width="${w * 0.2}" height="${h * 0.2}" rx="4" fill="${C.amar}"/>` +
          `<rect x="${w * 0.1}" y="${h * 0.78}" width="${w * 0.6}" height="${h * 0.06}" rx="3" fill="${C.claro}" opacity=".6"/>`;
        // estouro de quadrinho com o texto
        function estouroN(w, h, txt) {
          const n = 14, pts = [];
          for (let k = 0; k < n * 2; k++) {
            const a = (Math.PI * k) / n, r = k % 2 ? 0.62 + rnd(k + 3) * 0.08 : 0.98;
            pts.push(`${(w / 2 + Math.cos(a) * r * w / 2).toFixed(1)} ${(h / 2 + Math.sin(a) * r * h / 2).toFixed(1)}`);
          }
          const fs = caber(txt, w * 0.6, h * 0.36);
          return `<path d="M${pts.join(" L")} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>${fT(w / 2, h / 2 + fs * 0.36, txt, fs, C.verm)}`;
        }
        // computador (o "sistema"): tela com o texto e o pé
        function computadorN(w, h, l1, l2) {
          const f1 = caber(l1, w * 0.74, h * 0.13), f2 = caber(l2, w * 0.74, h * 0.13);
          return `<rect x="2" y="2" width="${w - 4}" height="${h * 0.72}" rx="14" fill="${C.tinta}"/><rect x="${w * 0.07}" y="${h * 0.06}" width="${w * 0.86}" height="${h * 0.58}" rx="8" fill="#9fb6d8"/>` +
            fT(w / 2, h * 0.3, l1, f1, C.tinta) + fT(w / 2, h * 0.3 + f2 * 1.3, l2, f2, C.azul2) +
            `<rect x="${w * 0.42}" y="${h * 0.72}" width="${w * 0.16}" height="${h * 0.16}" fill="#4a4858"/><rect x="${w * 0.26}" y="${h * 0.86}" width="${w * 0.48}" height="${h * 0.1}" rx="6" fill="${C.tinta}"/>`;
        }
        // calculadora de mesa
        const calculadoraN = (w, h) => `<rect x="2" y="2" width="${w - 4}" height="${h - 4}" rx="14" fill="#4a4858" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="${w * 0.12}" y="${h * 0.08}" width="${w * 0.76}" height="${h * 0.2}" rx="6" fill="#c9d8b6"/>` +
          Array.from({ length: 12 }, (_, k) => `<rect x="${w * (0.12 + (k % 3) * 0.27)}" y="${h * (0.36 + Math.floor(k / 3) * 0.15)}" width="${w * 0.22}" height="${h * 0.11}" rx="5" fill="${k === 11 ? C.verm : C.claro}"/>`).join("");
        // fachada de loja (o supermercado): toldo listrado, letreiro, porta e vitrines
        function lojaN(w, h, txt) {
          const fs = caber(txt, w * 0.8, h * 0.12);
          let s = `<rect x="${w * 0.04}" y="${h * 0.3}" width="${w * 0.92}" height="${h * 0.7}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
            `<rect x="${w * 0.02}" y="0" width="${w * 0.96}" height="${h * 0.18}" rx="8" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/>${fT(w / 2, h * 0.09 + fs * 0.36, txt, fs, C.claro)}`;
          for (let k = 0; k < 8; k++) s += `<path d="M${w * (0.02 + k * 0.12)} ${h * 0.18} L${w * (0.14 + k * 0.12)} ${h * 0.18} L${w * (0.14 + k * 0.12)} ${h * 0.3} Q${w * (0.08 + k * 0.12)} ${h * 0.36} ${w * (0.02 + k * 0.12)} ${h * 0.3} Z" fill="${k % 2 ? C.claro : C.verm}" stroke="${C.tinta}" stroke-width="3"/>`;
          s += `<rect x="${w * 0.4}" y="${h * 0.52}" width="${w * 0.2}" height="${h * 0.48}" fill="${C.azul2}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<rect x="${w * 0.1}" y="${h * 0.48}" width="${w * 0.24}" height="${h * 0.3}" fill="#9fb6d8" stroke="${C.tinta}" stroke-width="4"/><rect x="${w * 0.66}" y="${h * 0.48}" width="${w * 0.24}" height="${h * 0.3}" fill="#9fb6d8" stroke="${C.tinta}" stroke-width="4"/>`;
          return s;
        }

        // ── desenhos do C40 ───────────────────────────────────────────────────
        // morador de rua dormindo: o papelão, o cobertor cinza com o volume do corpo e a cabeça (sem rosto, de costas)
        const deitadoN = (w, h, cob = "#6b6880") => `<rect x="2" y="${h * 0.72}" width="${w - 4}" height="${h * 0.24}" rx="4" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w * 0.06} ${h * 0.74} Q${w * 0.1} ${h * 0.3} ${w * 0.42} ${h * 0.36} Q${w * 0.7} ${h * 0.2} ${w * 0.84} ${h * 0.5} L${w * 0.86} ${h * 0.74} Z" fill="${cob}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          `<circle cx="${w * 0.9}" cy="${h * 0.58}" r="${h * 0.15}" fill="#3a2a1c" stroke="${C.tinta}" stroke-width="3"/>` +
          `<path d="M${w * 0.2} ${h * 0.55} Q${w * 0.35} ${h * 0.48} ${w * 0.5} ${h * 0.55}" fill="none" stroke="${C.tinta}" stroke-width="2" opacity=".4"/>`;
        // o frasco de creolina: corpo escuro, tampa, rótulo
        function garrafaN(w, h, txt = "CREOLINA") {
          const fs = caber(txt, w * 0.8, h * 0.12);
          return `<rect x="${w * 0.36}" y="0" width="${w * 0.28}" height="${h * 0.12}" rx="4" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<path d="M${w * 0.34} ${h * 0.11} L${w * 0.66} ${h * 0.11} L${w * 0.66} ${h * 0.2} Q${w * 0.96} ${h * 0.26} ${w * 0.96} ${h * 0.4} L${w * 0.96} ${h * 0.96} Q${w * 0.96} ${h} ${w * 0.9} ${h} L${w * 0.1} ${h} Q${w * 0.04} ${h} ${w * 0.04} ${h * 0.96} L${w * 0.04} ${h * 0.4} Q${w * 0.04} ${h * 0.26} ${w * 0.34} ${h * 0.2} Z" fill="#3b2a1a" stroke="${C.tinta}" stroke-width="5"/>` +
            `<rect x="${w * 0.1}" y="${h * 0.46}" width="${w * 0.8}" height="${h * 0.3}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>${fT(w / 2, h * 0.61 + fs * 0.36, txt, fs, C.tinta)}`;
        }
        // a poça verde no chão
        const pocaN = (w, h) => `<path d="M${w * 0.08} ${h * 0.5} Q${w * 0.05} ${h * 0.1} ${w * 0.35} ${h * 0.14} Q${w * 0.55} 0 ${w * 0.75} ${h * 0.12} Q${w} ${h * 0.2} ${w * 0.95} ${h * 0.55} Q${w * 0.9} ${h} ${w * 0.55} ${h * 0.88} Q${w * 0.3} ${h} ${w * 0.15} ${h * 0.85} Q0 ${h * 0.75} ${w * 0.08} ${h * 0.5} Z" fill="#6f8f2a" stroke="${C.tinta}" stroke-width="4" opacity=".92"/>` +
          `<ellipse cx="${w * 0.4}" cy="${h * 0.38}" rx="${w * 0.12}" ry="${h * 0.1}" fill="#a9c35a" opacity=".7"/>`;
        // o cheiro: três ondas verdes subindo
        const cheiroN = (w, h) => [0.25, 0.5, 0.75].map((x) => `<path d="M${w * x} ${h} Q${w * (x - 0.12)} ${h * 0.75} ${w * x} ${h * 0.5} Q${w * (x + 0.12)} ${h * 0.25} ${w * x} 0" fill="none" stroke="#6f8f2a" stroke-width="10" stroke-linecap="round" opacity=".85"/>`).join("");
        // a barraca de salgado: toldo, balcão e a placa
        function barracaN(w, h) {
          const fs = caber("SALGADOS", w * 0.7, h * 0.12);
          let s = `<rect x="${w * 0.08}" y="${h * 0.2}" width="${w * 0.06}" height="${h * 0.5}" fill="${C.tinta}"/><rect x="${w * 0.86}" y="${h * 0.2}" width="${w * 0.06}" height="${h * 0.5}" fill="${C.tinta}"/>` +
            `<rect x="0" y="${h * 0.02}" width="${w}" height="${h * 0.2}" rx="8" fill="${C.amar}" stroke="${C.tinta}" stroke-width="5"/>${fT(w / 2, h * 0.12 + fs * 0.36, "SALGADOS", fs, C.tinta)}` +
            `<rect x="${w * 0.02}" y="${h * 0.62}" width="${w * 0.96}" height="${h * 0.38}" rx="6" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/>`;
          for (let k = 0; k < 4; k++) s += `<rect x="${w * (0.1 + k * 0.22)}" y="${h * 0.7}" width="${w * 0.14}" height="${h * 0.04}" fill="${C.claro}" opacity=".5"/>`;
          return s;
        }
        // vaca simples (o "remédio de bicho")
        const vacaN = (w, h) => `<rect x="${w * 0.12}" y="${h * 0.2}" width="${w * 0.62}" height="${h * 0.48}" rx="${h * 0.16}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<circle cx="${w * 0.3}" cy="${h * 0.38}" r="${h * 0.09}" fill="${C.tinta}"/><circle cx="${w * 0.55}" cy="${h * 0.5}" r="${h * 0.07}" fill="${C.tinta}"/>` +
          [0.18, 0.32, 0.54, 0.66].map((x) => `<rect x="${w * x}" y="${h * 0.62}" width="${w * 0.07}" height="${h * 0.34}" rx="4" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>`).join("") +
          `<rect x="${w * 0.68}" y="${h * 0.08}" width="${w * 0.28}" height="${h * 0.32}" rx="${h * 0.1}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/><rect x="${w * 0.84}" y="${h * 0.24}" width="${w * 0.14}" height="${h * 0.14}" rx="6" fill="${C.rosa}" stroke="${C.tinta}" stroke-width="3"/>` +
          `<path d="M${w * 0.7} ${h * 0.1} L${w * 0.66} 0 M${w * 0.92} ${h * 0.1} L${w * 0.96} 0" stroke="${C.tinta}" stroke-width="5" stroke-linecap="round"/>`;
        // alfinete de mapa
        const pinN = (w, h, cor = C.verm) => `<path d="M${w / 2} ${h} Q${w * 0.08} ${h * 0.52} ${w * 0.08} ${h * 0.36} Q${w * 0.08} 0 ${w / 2} 0 Q${w * 0.92} 0 ${w * 0.92} ${h * 0.36} Q${w * 0.92} ${h * 0.52} ${w / 2} ${h} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="5"/><circle cx="${w / 2}" cy="${h * 0.34}" r="${w * 0.16}" fill="${C.claro}"/>`;
        // balança de dois pratos (o haste é um obj e os pratos sobem e descem)
        const balancaN = (w, h) => `<rect x="${w * 0.47}" y="${h * 0.12}" width="${w * 0.06}" height="${h * 0.8}" fill="${C.tinta}"/><rect x="${w * 0.3}" y="${h * 0.9}" width="${w * 0.4}" height="${h * 0.1}" rx="6" fill="${C.tinta}"/>` +
          `<rect x="${w * 0.05}" y="${h * 0.1}" width="${w * 0.9}" height="${h * 0.05}" rx="4" fill="${C.tinta}"/>` +
          [0.12, 0.88].map((x) => `<path d="M${w * x} ${h * 0.14} L${w * (x - 0.1)} ${h * 0.45} M${w * x} ${h * 0.14} L${w * (x + 0.1)} ${h * 0.45}" stroke="${C.tinta}" stroke-width="3"/><path d="M${w * (x - 0.13)} ${h * 0.45} L${w * (x + 0.13)} ${h * 0.45} Q${w * x} ${h * 0.58} ${w * (x - 0.13)} ${h * 0.45} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/>`).join("");
        // torre de cidade: retângulo com a grade de janelas e a antena (o skyline de São Paulo)
        function torreN(w, h, cor = "#9a948a", luz = C.amar) {
          let s = `<rect x="${w * 0.47}" y="0" width="${w * 0.06}" height="${h * 0.08}" fill="${C.tinta}"/><rect x="2" y="${h * 0.07}" width="${w - 4}" height="${h * 0.93 - 2}" fill="${cor}" stroke="${C.tinta}" stroke-width="5"/>`;
          const cols = Math.max(2, Math.round(w / 55)), rows = Math.max(3, Math.round(h / 60));
          for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
            const acesa = rnd(i * 31 + j * 7 + w) > 0.62;
            s += `<rect x="${w * 0.1 + i * (w * 0.8) / cols}" y="${h * 0.13 + j * (h * 0.8) / rows}" width="${(w * 0.8) / cols - 10}" height="${(h * 0.8) / rows - 14}" fill="${acesa ? luz : "#2e2a45"}" opacity="${acesa ? 0.9 : 0.55}"/>`;
          }
          return s;
        }

        // ── desenhos do C41 ───────────────────────────────────────────────────
        // craca: o cone de placas cinza com a boca escura (o bicho que gruda no casco)
        const cracaN = (s, seed = 1) => recorteP(`<path d="M${s * 0.06} ${s} L${s * 0.28} ${s * 0.3} Q${s * 0.5} ${s * 0.16} ${s * 0.72} ${s * 0.3} L${s * 0.94} ${s} Z" fill="${["#cfc8b8", "#bdb5a3", "#d8d2c4"][seed % 3]}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          `<path d="M${s * 0.36} ${s * 0.27} L${s * 0.26} ${s} M${s * 0.5} ${s * 0.22} L${s * 0.5} ${s} M${s * 0.64} ${s * 0.27} L${s * 0.74} ${s}" stroke="${C.tinta}" stroke-width="3" opacity=".45"/>` +
          `<ellipse cx="${s / 2}" cy="${s * 0.3}" rx="${s * 0.16}" ry="${s * 0.07}" fill="${C.tinta}"/>`);
        // ônibus lotado: rostos espremidos nas janelas (olhos fechados de aperto), o letreiro LOTADO
        function onibusN(w, h, seed = 7) {
          const fs = caber("LOTADO", w * 0.28, h * 0.08);
          let s = `<rect x="4" y="${h * 0.06}" width="${w - 8}" height="${h * 0.76}" rx="${h * 0.08}" fill="${C.azul}" stroke="${C.tinta}" stroke-width="6"/>` +
            `<rect x="4" y="${h * 0.64}" width="${w - 8}" height="${h * 0.06}" fill="${C.amar}"/>` +
            `<rect x="${w * 0.05}" y="${h * 0.1}" width="${w * 0.3}" height="${h * 0.11}" rx="6" fill="${C.tinta}"/>${fT(w * 0.2, h * 0.155 + fs * 0.36, "LOTADO", fs, C.amar)}`;
          const nj = 5, jw = (w * 0.88) / nj;
          for (let k = 0; k < nj; k++) {
            const x = w * 0.06 + k * jw;
            s += `<rect x="${x}" y="${h * 0.25}" width="${jw - 8}" height="${h * 0.34}" rx="6" fill="#9fc3e8" stroke="${C.tinta}" stroke-width="4"/>`;
            for (let j = 0; j < 3; j++) {
              const i = seed + k * 3 + j, cx = x + (jw - 8) * (0.2 + j * 0.3), cy = h * (0.43 + (j % 2) * 0.03), rx = jw * 0.14, ry = jw * 0.19;
              s += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${PELE[i % 4]}" stroke="${C.tinta}" stroke-width="2.5"/>` +
                `<path d="M${cx - rx} ${cy - ry * 0.2} Q${cx} ${cy - ry * 1.5} ${cx + rx} ${cy - ry * 0.2}" fill="${["#2a1d14", C.tinta, "#7a4a22", "#c9c4bc"][i % 4]}"/>` +
                `<path d="M${cx - rx * 0.55} ${cy} l${rx * 0.35} ${ry * 0.12} M${cx + rx * 0.55} ${cy} l${-rx * 0.35} ${ry * 0.12}" stroke="${C.tinta}" stroke-width="2.5" stroke-linecap="round"/>` +
                `<ellipse cx="${cx}" cy="${cy + ry * 0.45}" rx="${rx * 0.22}" ry="${ry * 0.14}" fill="${C.tinta}"/>`;
            }
          }
          return s + [0.22, 0.78].map((f) => `<circle cx="${w * f}" cy="${h * 0.84}" r="${h * 0.12}" fill="${C.tinta}"/><circle cx="${w * f}" cy="${h * 0.84}" r="${h * 0.05}" fill="#9a948a"/>`).join("");
        }
        // ponteiro de relógio (gira em torno da ponta de baixo)
        const ponteiroR = (w, h) => `<rect x="${w / 2 - w * 0.25}" y="0" width="${w * 0.5}" height="${h}" rx="${w * 0.25}" fill="${C.tinta}"/>`;
        // galinha de papel (marrom), triste ou não
        function galinhaN(w, h, triste = false) {
          const cor = "#c9773a";
          let s = `<path d="M${w * 0.16} ${h * 0.52} L${w * 0.02} ${h * 0.2} L${w * 0.26} ${h * 0.36} Z" fill="#8a4a22" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
            `<path d="M${w * 0.42} ${h * 0.84} L${w * 0.4} ${h * 0.98} M${w * 0.56} ${h * 0.84} L${w * 0.58} ${h * 0.98}" stroke="${C.amar2}" stroke-width="6" stroke-linecap="round"/>` +
            `<ellipse cx="${w * 0.47}" cy="${h * 0.6}" rx="${w * 0.35}" ry="${h * 0.28}" fill="${cor}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<path d="M${w * 0.3} ${h * 0.56} Q${w * 0.48} ${h * 0.42} ${w * 0.62} ${h * 0.58} Q${w * 0.48} ${h * 0.74} ${w * 0.3} ${h * 0.56} Z" fill="#a85f2c" stroke="${C.tinta}" stroke-width="3"/>` +
            `<path d="M${w * 0.64} ${h * 0.2} Q${w * 0.66} ${h * 0.07} ${w * 0.71} ${h * 0.17} Q${w * 0.75} ${h * 0.05} ${w * 0.79} ${h * 0.17} Q${w * 0.84} ${h * 0.08} ${w * 0.85} ${h * 0.22} Z" fill="${C.verm}" stroke="${C.tinta}" stroke-width="3"/>` +
            `<circle cx="${w * 0.74}" cy="${h * 0.32}" r="${w * 0.14}" fill="${cor}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<path d="M${w * 0.86} ${h * 0.28} L${w * 0.99} ${h * 0.33} L${w * 0.86} ${h * 0.38} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3" stroke-linejoin="round"/>` +
            `<ellipse cx="${w * 0.85}" cy="${h * 0.43}" rx="${w * 0.025}" ry="${h * 0.045}" fill="${C.verm}"/>` +
            `<circle cx="${w * 0.78}" cy="${h * 0.29}" r="${w * 0.024}" fill="${C.tinta}"/>`;
          if (triste) s += `<path d="M${w * 0.72} ${h * 0.22} L${w * 0.82} ${h * 0.25}" stroke="${C.tinta}" stroke-width="4" stroke-linecap="round"/><path d="M${w * 0.79} ${h * 0.34} Q${w * 0.81} ${h * 0.4} ${w * 0.79} ${h * 0.43} Q${w * 0.77} ${h * 0.4} ${w * 0.79} ${h * 0.34} Z" fill="#4a90c8"/>`;
          return recorteP(s);
        }
        const ovoN = (w, h, racha = false) => recorteP(`<ellipse cx="${w / 2}" cy="${h / 2}" rx="${w / 2 - 3}" ry="${h / 2 - 3}" fill="#f4ead4" stroke="${C.tinta}" stroke-width="4"/>` +
          (racha ? `<path d="M${w * 0.1} ${h * 0.5} L${w * 0.28} ${h * 0.38} L${w * 0.42} ${h * 0.56} L${w * 0.58} ${h * 0.38} L${w * 0.74} ${h * 0.56} L${w * 0.9} ${h * 0.44}" fill="none" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` : ""));
        const pintinhoN = (s) => recorteP(`<ellipse cx="${s * 0.46}" cy="${s * 0.66}" rx="${s * 0.34}" ry="${s * 0.28}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<circle cx="${s * 0.62}" cy="${s * 0.34}" r="${s * 0.2}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${s * 0.8} ${s * 0.32} L${s * 0.96} ${s * 0.37} L${s * 0.8} ${s * 0.42} Z" fill="#e5832d" stroke="${C.tinta}" stroke-width="2.5"/><circle cx="${s * 0.67}" cy="${s * 0.3}" r="${s * 0.035}" fill="${C.tinta}"/>` +
          `<path d="M${s * 0.38} ${s * 0.9} L${s * 0.36} ${s * 0.99} M${s * 0.52} ${s * 0.9} L${s * 0.54} ${s * 0.99}" stroke="#e5832d" stroke-width="4" stroke-linecap="round"/>`);
        const ninhoN = (w, h) => `<ellipse cx="${w / 2}" cy="${h * 0.5}" rx="${w / 2 - 3}" ry="${h * 0.45}" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="4"/>` +
          Array.from({ length: 9 }, (_, k) => `<path d="M${w * (0.08 + k * 0.1)} ${h * (0.3 + rnd(k + 401) * 0.4)} q${w * 0.06} ${-h * 0.2} ${w * 0.12} 0" fill="none" stroke="#8a6a3a" stroke-width="3"/>`).join("");
        // luva de ladrão: manga listrada vindo da direita, mão de luva preta à esquerda
        const luvaN = (w, h) => recorteP(`<rect x="${w * 0.36}" y="${h * 0.3}" width="${w * 0.64}" height="${h * 0.4}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
          [0, 1, 2, 3, 4].map((k) => `<rect x="${w * (0.42 + k * 0.12)}" y="${h * 0.3}" width="${w * 0.06}" height="${h * 0.4}" fill="${C.tinta}"/>`).join("") +
          `<rect x="${w * 0.1}" y="${h * 0.22}" width="${w * 0.3}" height="${h * 0.56}" rx="${h * 0.16}" fill="#2a2638" stroke="${C.tinta}" stroke-width="4"/>` +
          [0.24, 0.42, 0.6].map((f) => `<rect x="0" y="${h * f}" width="${w * 0.16}" height="${h * 0.15}" rx="${h * 0.07}" fill="#2a2638" stroke="${C.tinta}" stroke-width="3"/>`).join(""));
        // pizza do PIB, a fatia (de -30° a 30°, apontando para a direita) e o buraco que ela deixa
        function pizzaN(d, txt) {
          const r = d / 2 - 6, fs = caber(txt, d * 0.36, d * 0.12);
          let s = `<circle cx="${d / 2}" cy="${d / 2}" r="${r}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="6"/><circle cx="${d / 2}" cy="${d / 2}" r="${r * 0.84}" fill="${C.verm}" opacity=".85"/>`;
          for (let k = 0; k < 6; k++) s += `<path d="M${d / 2} ${d / 2} L${d / 2 + Math.cos((k * 60 + 30) * Math.PI / 180) * r} ${d / 2 + Math.sin((k * 60 + 30) * Math.PI / 180) * r}" stroke="${C.tinta}" stroke-width="4"/>`;
          [[0.3, 0.32], [0.62, 0.26], [0.36, 0.68], [0.68, 0.66], [0.22, 0.52]].forEach(([x, y]) => (s += `<circle cx="${d * x}" cy="${d * y}" r="${d * 0.045}" fill="${C.verm2}"/>`));
          return s + `<rect x="${d * 0.1}" y="${d * 0.42}" width="${d * 0.36}" height="${d * 0.16}" rx="8" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>${fT(d * 0.28, d / 2 + fs * 0.36, txt, fs, C.tinta)}`;
        }
        const fatiaN = (d) => {
          const r = d / 2 - 6, a = Math.PI / 6, cx = d / 2, cy = d / 2;
          return `<path d="M${cx} ${cy} L${cx + Math.cos(-a) * r} ${cy + Math.sin(-a) * r} A${r} ${r} 0 0 1 ${cx + Math.cos(a) * r} ${cy + Math.sin(a) * r} Z" fill="${C.verm}" stroke="${C.tinta}" stroke-width="5"/>` +
            `<path d="M${cx + Math.cos(-a) * r} ${cy + Math.sin(-a) * r} A${r} ${r} 0 0 1 ${cx + Math.cos(a) * r} ${cy + Math.sin(a) * r}" fill="none" stroke="${C.amar}" stroke-width="${r * 0.16}"/>`;
        };
        const buracoN = (d) => {
          const r = d / 2 - 6, a = Math.PI / 6, cx = d / 2, cy = d / 2;
          return `<path d="M${cx} ${cy} L${cx + Math.cos(-a) * r} ${cy + Math.sin(-a) * r} A${r} ${r} 0 0 1 ${cx + Math.cos(a) * r} ${cy + Math.sin(a) * r} Z" fill="${C.papel}" stroke="${C.tinta}" stroke-width="4"/>`;
        };
        // caixa de produto
        const produtoN = (w, h) => `<path d="M${w * 0.08} ${h * 0.24} L${w * 0.5} ${h * 0.06} L${w * 0.92} ${h * 0.24} L${w * 0.5} ${h * 0.42} Z" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.08} ${h * 0.24} L${w * 0.5} ${h * 0.42} L${w * 0.5} ${h * 0.98} L${w * 0.08} ${h * 0.8} Z" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.92} ${h * 0.24} L${w * 0.5} ${h * 0.42} L${w * 0.5} ${h * 0.98} L${w * 0.92} ${h * 0.8} Z" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          fT(w * 0.29, h * 0.62, "PRODUTO", caber("PRODUTO", w * 0.42, h * 0.08), C.tinta);
        // o mar com ondas
        const marN = (w, h) => `<rect y="${h * 0.2}" width="${w}" height="${h * 0.8}" fill="#9fc3e8" opacity=".75"/>` +
          Array.from({ length: Math.ceil(w / 80) }, (_, k) => `<path d="M${k * 80} ${h * 0.22} q20 ${-h * 0.2} 40 0 t40 0" fill="none" stroke="#4a7ab0" stroke-width="5"/>`).join("");

        // ── desenhos do C42 ───────────────────────────────────────────────────
        // o Congresso: as duas torres, a cúpula do Senado (à esquerda) e a da Câmara (à direita) (do C35)
        function congresso(w, h, txt = "CONGRESSO") {
          const fs = caber(txt, w * 0.8, h * 0.11);
          return `<rect x="${w * 0.42}" y="0" width="${w * 0.07}" height="${h * 0.62}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<rect x="${w * 0.51}" y="0" width="${w * 0.07}" height="${h * 0.62}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<rect x="${w * 0.42}" y="${h * 0.3}" width="${w * 0.16}" height="${h * 0.05}" fill="${C.tinta}"/>` +
            `<rect x="0" y="${h * 0.62}" width="${w}" height="${h * 0.14}" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<path d="M${w * 0.06} ${h * 0.62} Q${w * 0.2} ${h * 0.4} ${w * 0.34} ${h * 0.62} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
            `<path d="M${w * 0.66} ${h * 0.5} Q${w * 0.8} ${h * 0.74} ${w * 0.94} ${h * 0.5} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
            fT(w / 2, h * 0.92, txt, fs, C.tinta);
        }
        // a coroa (os poderes imperiais)
        const coroaN = (w, h) => recorteP(`<path d="M${w * 0.06} ${h * 0.86} L${w * 0.02} ${h * 0.22} L${w * 0.28} ${h * 0.5} L${w * 0.5} ${h * 0.06} L${w * 0.72} ${h * 0.5} L${w * 0.98} ${h * 0.22} L${w * 0.94} ${h * 0.86} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<rect x="${w * 0.05}" y="${h * 0.76}" width="${w * 0.9}" height="${h * 0.16}" rx="6" fill="${C.amar2}" stroke="${C.tinta}" stroke-width="4"/>` +
          [[0.02, 0.2, C.verm], [0.5, 0.05, C.azul], [0.98, 0.2, "#3c9a4f"]].map(([x, y, c]) => `<circle cx="${w * x}" cy="${h * y}" r="${w * 0.055}" fill="${c}" stroke="${C.tinta}" stroke-width="3"/>`).join("") +
          [0.25, 0.5, 0.75].map((x) => `<circle cx="${w * x}" cy="${h * 0.84}" r="${w * 0.04}" fill="${C.verm}"/>`).join(""));
        // a orelha (ouvir)
        const orelhaN = (s, pele = PELE[1]) => recorteP(`<path d="M${s * 0.3} ${s * 0.85} Q${s * 0.12} ${s * 0.5} ${s * 0.3} ${s * 0.18} Q${s * 0.5} 0 ${s * 0.72} ${s * 0.12} Q${s * 0.95} ${s * 0.28} ${s * 0.8} ${s * 0.55} Q${s * 0.68} ${s * 0.7} ${s * 0.62} ${s * 0.88} Q${s * 0.5} ${s} ${s * 0.3} ${s * 0.85} Z" fill="${pele}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="M${s * 0.42} ${s * 0.7} Q${s * 0.3} ${s * 0.45} ${s * 0.45} ${s * 0.3} Q${s * 0.62} ${s * 0.22} ${s * 0.66} ${s * 0.4} Q${s * 0.6} ${s * 0.52} ${s * 0.5} ${s * 0.5}" fill="none" stroke="${C.tinta}" stroke-width="5" stroke-linecap="round"/>`);
        // a placa amarela de cautela
        const cautelaN = (s, txt = "CAUTELA") => recorteP(`<path d="M${s / 2} ${s * 0.04} L${s * 0.96} ${s / 2} L${s / 2} ${s * 0.96} L${s * 0.04} ${s / 2} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="8" stroke-linejoin="round"/>` +
          fT(s / 2, s * 0.42, "!", s * 0.3, C.tinta) + fT(s / 2, s * 0.64, txt, caber(txt, s * 0.6, s * 0.11), C.tinta));
        // o medidor (semicírculo com as faixas vermelha, amarela e verde); o ponteiro é o ponteiroR do C41, girando na base
        const medidorN = (w, h, txt) => {
          const cx = w / 2, cy = h * 0.86, r = w * 0.44;
          const arco = (a0, a1, cor) => { const p = (a) => [cx + Math.cos(Math.PI + a) * r, cy + Math.sin(Math.PI + a) * r]; const [x0, y0] = p(a0), [x1, y1] = p(a1);
            return `<path d="M${cx} ${cy} L${x0} ${y0} A${r} ${r} 0 0 1 ${x1} ${y1} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="4"/>`; };
          return arco(0, Math.PI / 3, C.verm) + arco(Math.PI / 3, 2 * Math.PI / 3, C.amar) + arco(2 * Math.PI / 3, Math.PI, "#3c9a4f") +
            `<circle cx="${cx}" cy="${cy}" r="${w * 0.05}" fill="${C.tinta}"/>` + fT(cx, h * 0.99, txt, caber(txt, w * 0.9, h * 0.11), C.tinta);
        };
        // caixa de entrega com o rótulo
        const caixaN = (w, h, txt, cor = C.kraft) => recorteP(`<rect x="3" y="${h * 0.12}" width="${w - 6}" height="${h * 0.85}" rx="6" fill="${cor}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="M3 ${h * 0.12} L${w * 0.2} 3 L${w * 0.8} 3 L${w - 3} ${h * 0.12} Z" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<rect x="${w * 0.42}" y="${h * 0.12}" width="${w * 0.16}" height="${h * 0.85}" fill="${C.amar2}" opacity=".7"/>` +
          `<rect x="${w * 0.1}" y="${h * 0.45}" width="${w * 0.8}" height="${h * 0.26}" rx="5" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>` +
          fT(w / 2, h * 0.58 + caber(txt, w * 0.74, h * 0.16) * 0.36, txt, caber(txt, w * 0.74, h * 0.16), C.tinta));
        // a mesa redonda vista de cima (as cadeiras em volta são bustos coloridos)
        const mesaN = (w, h) => `<ellipse cx="${w / 2}" cy="${h / 2}" rx="${w / 2 - 6}" ry="${h / 2 - 6}" fill="${C.kraft2}" stroke="${C.tinta}" stroke-width="6"/>` +
          `<ellipse cx="${w / 2}" cy="${h / 2}" rx="${w * 0.38}" ry="${h * 0.34}" fill="none" stroke="${C.tinta}" stroke-width="3" opacity=".35"/>`;
        // o busto simples (sem rosto) para as cadeiras da mesa
        const bustoN = (s, roupa) => recorteP(`<path d="M${s * 0.1} ${s} L${s * 0.1} ${s * 0.7} Q${s * 0.1} ${s * 0.52} ${s * 0.3} ${s * 0.52} L${s * 0.7} ${s * 0.52} Q${s * 0.9} ${s * 0.52} ${s * 0.9} ${s * 0.7} L${s * 0.9} ${s} Z" fill="${roupa}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<circle cx="${s / 2}" cy="${s * 0.3}" r="${s * 0.2}" fill="${PELE[1]}" stroke="${C.tinta}" stroke-width="4"/>`);

        // ── desenhos do C44 ───────────────────────────────────────────────────
        // a semana: 7 dias, os de trabalho em vermelho e as folgas em verde (6x1 → folgas = 1; 5x2 → folgas = 2)
        function semanaN(w, h, folgas = 1) {
          const D = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"], dw = (w - 16) / 7;
          let s = `<rect x="2" y="2" width="${w - 4}" height="${h - 4}" rx="12" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>`;
          D.forEach((d, k) => {
            const folga = k >= 7 - folgas, x = 8 + k * dw;
            s += `<rect x="${x + 3}" y="10" width="${dw - 6}" height="${h - 20}" rx="8" fill="${folga ? "#3c9a4f" : C.verm}" stroke="${C.tinta}" stroke-width="3"/>` +
              fT(x + dw / 2, h * 0.36, d, caber(d, dw, h * 0.2), C.claro) +
              fT(x + dw / 2, h * 0.74, folga ? "FOLGA" : "TRAB.", caber("FOLGA", dw, h * 0.15), C.claro);
          });
          return s;
        }
        // a bateria (com a porcentagem)
        const bateriaN = (w, h, pct) => `<rect x="4" y="4" width="${w * 0.88}" height="${h - 8}" rx="12" fill="${C.claro}" stroke="${C.tinta}" stroke-width="7"/>` +
          `<rect x="${w * 0.9}" y="${h * 0.32}" width="${w * 0.08}" height="${h * 0.36}" rx="4" fill="${C.tinta}"/>` +
          (pct > 0 ? `<rect x="14" y="14" width="${(w * 0.88 - 20) * pct / 100}" height="${h - 28}" rx="6" fill="${pct < 25 ? C.verm : "#3c9a4f"}"/>` : "") +
          fT(w * 0.46, h / 2 + h * 0.13, pct + "%", h * 0.36, C.tinta);
        // a marmita (pote com tampa)
        const marmitaN = (s) => recorteP(`<rect x="${s * 0.08}" y="${s * 0.34}" width="${s * 0.84}" height="${s * 0.5}" rx="${s * 0.08}" fill="#cfd8e6" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="${s * 0.04}" y="${s * 0.22}" width="${s * 0.92}" height="${s * 0.16}" rx="${s * 0.06}" fill="${C.azul}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${s * 0.2} ${s * 0.6} Q${s * 0.5} ${s * 0.48} ${s * 0.8} ${s * 0.6}" stroke="${C.amar2}" stroke-width="${s * 0.08}" fill="none" stroke-linecap="round"/>`);
        // a enquete: o título e a barra do "a favor"
        function enqueteN(w, h, titulo, pct) {
          const ft = caber(titulo, w * 0.9, h * 0.12);
          return `<path d="${pRet(w, h, 441, 2, 30)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/><rect x="0" y="0" width="${w}" height="${h * 0.26}" fill="${C.tinta}"/>` +
            fT(w / 2, h * 0.13 + ft * 0.36, titulo, ft, C.claro) +
            fT(w * 0.06, h * 0.46, "A FAVOR", h * 0.1, C.tinta, "start") + `<rect x="${w * 0.06}" y="${h * 0.52}" width="${w * 0.88}" height="${h * 0.12}" rx="8" fill="#d8d0c0"/>` +
            (pct > 0 ? `<rect x="${w * 0.06}" y="${h * 0.52}" width="${w * 0.88 * pct / 100}" height="${h * 0.12}" rx="8" fill="#3c9a4f"/>` : "") +
            fT(w * 0.94, h * 0.46, pct + "%", h * 0.1, "#3c9a4f", "end") +
            fT(w * 0.06, h * 0.78, "CONTRA", h * 0.1, C.tinta, "start") + `<rect x="${w * 0.06}" y="${h * 0.84}" width="${w * 0.88}" height="${h * 0.12}" rx="8" fill="${C.verm}"/>` +
            fT(w * 0.94, h * 0.78, (100 - pct) + "%", h * 0.1, C.verm, "end");
        }
        // a rachadura (por cima da loja que quebra)
        const rachaN = (w, h) => `<path d="M${w * 0.5} 0 L${w * 0.42} ${h * 0.22} L${w * 0.58} ${h * 0.38} L${w * 0.44} ${h * 0.6} L${w * 0.6} ${h * 0.8} L${w * 0.5} ${h}" fill="none" stroke="${C.tinta}" stroke-width="8" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.58} ${h * 0.38} L${w * 0.78} ${h * 0.44} M${w * 0.44} ${h * 0.6} L${w * 0.24} ${h * 0.66}" fill="none" stroke="${C.tinta}" stroke-width="5"/>`;
        // o papel da lei (com a linha da assinatura)
        const leiN = (w, h) => recorteP(`<rect x="3" y="3" width="${w - 6}" height="${h - 6}" rx="6" fill="#fbf8f0" stroke="${C.tinta}" stroke-width="4"/>`) +
          fT(w / 2, h * 0.2, "LEI", h * 0.14, C.tinta) + [0.32, 0.42, 0.52, 0.62].map((f) => `<rect x="${w * 0.12}" y="${h * f}" width="${w * (0.5 + rnd(f * 99) * 0.26)}" height="${h * 0.03}" rx="3" fill="${C.tinta}" opacity=".3"/>`).join("") +
          `<path d="M${w * 0.14} ${h * 0.84} L${w * 0.86} ${h * 0.84}" stroke="${C.tinta}" stroke-width="3"/>`;
        // a assinatura que se desenha (id para o desenha())
        const assinaN = (w, h, id) => `<path id="${id}" d="M${w * 0.16} ${h * 0.8} Q${w * 0.26} ${h * 0.6} ${w * 0.32} ${h * 0.78} T${w * 0.48} ${h * 0.76} Q${w * 0.56} ${h * 0.6} ${w * 0.62} ${h * 0.8} T${w * 0.84} ${h * 0.72}" fill="none" stroke="${C.azul2}" stroke-width="5" stroke-linecap="round"/>`;

        // ── desenhos do C45 (o poder inédito, 10/10/2026) ─────────────────────
        const CINZA = "#8d8a96";
        // o plenário em meia-lua: as cadeiras vão da esquerda para a direita da tela pelo ângulo (como nos mapas de bancada).
        // grupo "base" = as cadeiras vazias e o piso; "esq", "cen" e "dir" = só as cadeiras daquela bancada, na cor dela
        // (24% esquerda, 22% centro, 54% direita: 124, 113 e 276 de 513)
        const PLEN = (() => {
          const out = [];
          [150, 202, 254, 306, 358].forEach((r) => {
            const n = Math.floor((Math.PI * r) / 33);
            for (let k = 0; k < n; k++) out.push([r, Math.PI - (Math.PI * (k + 0.5)) / n]);
          });
          return out.sort((p, q) => q[1] - p[1]);
        })();
        function plenarioN(w, h, grupo) {
          const cx = w / 2, cy = h - 16, e = Math.min(w / 2 - 20, h - 30) / 358, n = PLEN.length;
          const cor = { esq: C.verm, cen: CINZA, dir: C.azul };
          const lim = { esq: [0, Math.round(n * 0.242)], cen: [Math.round(n * 0.242), Math.round(n * 0.462)], dir: [Math.round(n * 0.462), n] };
          let s = grupo === "base" ? `<path d="M${cx - 380 * e} ${cy + 10} A${380 * e} ${380 * e} 0 0 1 ${cx + 380 * e} ${cy + 10} Z" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="5"/>` +
            `<path d="M${cx - 125 * e} ${cy + 10} A${125 * e} ${125 * e} 0 0 1 ${cx + 125 * e} ${cy + 10} Z" fill="${C.papel}" stroke="${C.tinta}" stroke-width="4"/>` : "";
          PLEN.forEach(([r, a], k) => {
            const x = (cx + Math.cos(a) * r * e).toFixed(1), y = (cy - Math.sin(a) * r * e).toFixed(1), rr = (12 * e).toFixed(1);
            if (grupo === "base") s += `<circle cx="${x}" cy="${y}" r="${rr}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="3"/>`;
            else if (k >= lim[grupo][0] && k < lim[grupo][1]) s += `<circle cx="${x}" cy="${y}" r="${rr}" fill="${cor[grupo]}" stroke="${C.tinta}" stroke-width="3"/>`;
          });
          return s;
        }
        // a xícara do cafezinho, com o pires e a fumaça
        const xicaraN = (w, h) => `<ellipse cx="${w * 0.5}" cy="${h * 0.9}" rx="${w * 0.46}" ry="${h * 0.08}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w * 0.2} ${h * 0.45} L${w * 0.8} ${h * 0.45} Q${w * 0.78} ${h * 0.86} ${w * 0.5} ${h * 0.86} Q${w * 0.22} ${h * 0.86} ${w * 0.2} ${h * 0.45} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w * 0.79} ${h * 0.52} Q${w * 0.98} ${h * 0.52} ${w * 0.94} ${h * 0.64} Q${w * 0.9} ${h * 0.74} ${w * 0.74} ${h * 0.72}" fill="none" stroke="${C.tinta}" stroke-width="5"/>` +
          `<ellipse cx="${w * 0.5}" cy="${h * 0.465}" rx="${w * 0.28}" ry="${h * 0.035}" fill="#5a3a22"/>` +
          [0.38, 0.5, 0.62].map((f) => `<path d="M${w * f} ${h * 0.38} q${w * 0.06} ${-h * 0.08} 0 ${-h * 0.16} q${-w * 0.06} ${-h * 0.08} 0 ${-h * 0.16}" fill="none" stroke="${C.kraft2}" stroke-width="4" stroke-linecap="round"/>`).join("");
        // a espada (ponta para baixo): punho, guarda dourada e lâmina
        const espadaN = (w, h) => `<rect x="${w * 0.4}" y="${h * 0.03}" width="${w * 0.2}" height="${h * 0.15}" rx="4" fill="#6b4a2e" stroke="${C.tinta}" stroke-width="3"/>` +
          `<circle cx="${w / 2}" cy="${h * 0.04}" r="${w * 0.12}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/>` +
          `<rect x="0" y="${h * 0.17}" width="${w}" height="${h * 0.05}" rx="5" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/>` +
          `<path d="M${w * 0.33} ${h * 0.22} L${w * 0.67} ${h * 0.22} L${w * 0.63} ${h * 0.9} L${w / 2} ${h} L${w * 0.37} ${h * 0.9} Z" fill="#d9dce4" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          `<path d="M${w / 2} ${h * 0.25} L${w / 2} ${h * 0.88}" stroke="#9aa0ae" stroke-width="3"/>`;
        // a cadeira da Presidência: espaldar alto de madeira, estofado vermelho e o brasão
        const cadeiraN = (w, h) => `<path d="M${w * 0.14} ${h * 0.62} L${w * 0.14} ${h * 0.12} Q${w * 0.14} 0 ${w * 0.3} 0 L${w * 0.7} 0 Q${w * 0.86} 0 ${w * 0.86} ${h * 0.12} L${w * 0.86} ${h * 0.62} Z" fill="#6b3a2a" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="M${w * 0.24} ${h * 0.58} L${w * 0.24} ${h * 0.15} Q${w * 0.24} ${h * 0.07} ${w * 0.34} ${h * 0.07} L${w * 0.66} ${h * 0.07} Q${w * 0.76} ${h * 0.07} ${w * 0.76} ${h * 0.15} L${w * 0.76} ${h * 0.58} Z" fill="${C.verm}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="${w * 0.04}" y="${h * 0.58}" width="${w * 0.92}" height="${h * 0.12}" rx="10" fill="${C.verm2}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<rect x="${w * 0.1}" y="${h * 0.7}" width="${w * 0.08}" height="${h * 0.3}" fill="#6b3a2a" stroke="${C.tinta}" stroke-width="4"/><rect x="${w * 0.82}" y="${h * 0.7}" width="${w * 0.08}" height="${h * 0.3}" fill="#6b3a2a" stroke="${C.tinta}" stroke-width="4"/>` +
          `<circle cx="${w / 2}" cy="${h * 0.24}" r="${w * 0.1}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/><path d="M${w / 2} ${h * 0.24 - w * 0.06} L${w / 2 + w * 0.05} ${h * 0.24 + w * 0.05} L${w / 2 - w * 0.05} ${h * 0.24 + w * 0.05} Z" fill="#3c9a4f"/>`;
        // a asa de papel (esq = espelhada)
        const asaN = (w, h, esq = false) => `<g transform="${esq ? `translate(${w} 0) scale(-1 1)` : ""}"><path d="M0 ${h * 0.7} Q${w * 0.2} ${h * 0.05} ${w} 0 Q${w * 0.86} ${h * 0.3} ${w * 0.96} ${h * 0.38} Q${w * 0.72} ${h * 0.52} ${w * 0.84} ${h * 0.64} Q${w * 0.54} ${h * 0.74} ${w * 0.62} ${h * 0.88} Q${w * 0.3} ${h * 0.96} 0 ${h * 0.7} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/></g>`;
        // a agenda aberta, com as páginas em branco
        const agendaN = (w, h) => `<path d="M${w / 2} ${h * 0.12} Q${w * 0.26} ${h * 0.02} 0 ${h * 0.08} L0 ${h} Q${w * 0.26} ${h * 0.92} ${w / 2} ${h} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w / 2} ${h * 0.12} Q${w * 0.74} ${h * 0.02} ${w} ${h * 0.08} L${w} ${h} Q${w * 0.74} ${h * 0.92} ${w / 2} ${h} Z" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w / 2} ${h * 0.12} L${w / 2} ${h}" stroke="${C.tinta}" stroke-width="4"/>` + fT(w * 0.26, h * 0.24, "AGENDA", caber("AGENDA", w * 0.4, h * 0.11), C.verm) +
          [0.38, 0.5, 0.62, 0.74, 0.86].map((f) => `<path d="M${w * 0.07} ${h * f} L${w * 0.43} ${h * f} M${w * 0.57} ${h * f} L${w * 0.93} ${h * f}" stroke="${C.kraft}" stroke-width="3"/>`).join("");
        // o peso de ferro, com o texto
        const pesoN = (w, h, txt) => `<path d="M${w * 0.36} ${h * 0.24} Q${w / 2} ${h * 0.02} ${w * 0.64} ${h * 0.24}" fill="none" stroke="${C.tinta}" stroke-width="${w * 0.07}"/>` +
          `<path d="M${w * 0.18} ${h * 0.24} L${w * 0.82} ${h * 0.24} L${w} ${h} L0 ${h} Z" fill="#4a4858" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` + fT(w / 2, h * 0.68, txt, caber(txt, w * 0.72, h * 0.28), C.claro);
        // a cancela: o poste e o braço listrado (o braço gira para cima a partir da esquerda)
        const posteN = (w, h) => `<rect width="${w}" height="${h}" rx="8" fill="#4a4858" stroke="${C.tinta}" stroke-width="5"/>`;
        function bracoCancelaN(w, h) {
          let s = `<rect width="${w}" height="${h}" rx="${h / 2}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>`;
          for (let x = h; x < w - h; x += h * 2) s += `<rect x="${x}" y="4" width="${h}" height="${h - 8}" fill="${C.verm}"/>`;
          return s;
        }
        // a chave
        const chaveN = (w, h) => `<rect x="${h * 0.8}" y="${h * 0.4}" width="${w - h * 0.85}" height="${h * 0.2}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<rect x="${w * 0.84}" y="${h * 0.56}" width="${h * 0.16}" height="${h * 0.26}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/><rect x="${w * 0.7}" y="${h * 0.56}" width="${h * 0.16}" height="${h * 0.18}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/>` +
          `<circle cx="${h / 2}" cy="${h / 2}" r="${h * 0.44}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/><circle cx="${h / 2}" cy="${h / 2}" r="${h * 0.16}" fill="${C.papel}" stroke="${C.tinta}" stroke-width="3"/>`;
        // a faixa presidencial (verde com a listra amarela)
        const faixaPresN = (w, h) => `<path d="M0 0 L${w * 0.32} 0 L${w} ${h * 0.7} L${w} ${h} L${w * 0.68} ${h} L0 ${h * 0.3} Z" fill="#3c9a4f" stroke="${C.tinta}" stroke-width="4" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.16} ${h * 0.02} L${w * 0.98} ${h * 0.86}" stroke="${C.amar}" stroke-width="${w * 0.08}"/>` +
          `<circle cx="${w * 0.56}" cy="${h * 0.5}" r="${w * 0.11}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="3"/>`;
        // o plano de governo: o cabeçalho e as páginas em branco
        const planoN = (w, h) => `<path d="${pRet(w, h, 8080, 1.4, 34)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<rect x="0" y="0" width="${w}" height="${h * 0.24}" fill="${C.tinta}"/>` +
          fT(w / 2, h * 0.1, "PLANO DE", caber("PLANO DE", w * 0.8, h * 0.085), C.claro) + fT(w / 2, h * 0.2, "GOVERNO", caber("GOVERNO", w * 0.8, h * 0.085), C.claro);

        // ── desenhos do C46 (o mercado sem ideologia, 10/10/2026) ───────────────
        // folha de prancheta em branco com o título em duas linhas (o planoN do C45 com outro título)
        const folhaN = (w, h, a, b = "") => `<path d="${pRet(w, h, 8080 + w, 1.4, 34)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<rect x="0" y="0" width="${w}" height="${h * 0.24}" fill="${C.tinta}"/>` +
          fT(w / 2, h * (b ? 0.1 : 0.15), a, caber(a, w * 0.8, h * 0.085), C.claro) + (b ? fT(w / 2, h * 0.2, b, caber(b, w * 0.8, h * 0.085), C.claro) : "") +
          [0.4, 0.55, 0.7, 0.85].map((f) => `<rect x="${w * 0.12}" y="${h * f}" width="${w * 0.76}" height="4" fill="${C.tinta}" opacity=".12"/>`).join("");
        // cofre de aço com o disco do segredo
        const cofreN = (w, h, txt) => `<rect x="4" y="4" width="${w - 8}" height="${h - 8}" rx="14" fill="#8d97a6" stroke="${C.tinta}" stroke-width="6"/>` +
          `<rect x="${w * 0.12}" y="${h * 0.1}" width="${w * 0.76}" height="${h * 0.62}" rx="8" fill="#a9b2bf" stroke="${C.tinta}" stroke-width="4"/>` +
          `<circle cx="${w / 2}" cy="${h * 0.41}" r="${w * 0.17}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="M${w / 2} ${h * 0.41} L${w / 2} ${h * 0.41 - w * 0.13}" stroke="${C.tinta}" stroke-width="6" stroke-linecap="round"/>` +
          fT(w / 2, h * 0.86, txt, caber(txt, w * 0.84, h * 0.13), C.claro);
        // botijão de gás
        const botijaoN = (w, h) => `<path d="M${w * 0.3} ${h * 0.2} L${w * 0.3} ${h * 0.06} L${w * 0.7} ${h * 0.06} L${w * 0.7} ${h * 0.2}" fill="none" stroke="${C.tinta}" stroke-width="6"/>` +
          `<rect x="${w * 0.08}" y="${h * 0.18}" width="${w * 0.84}" height="${h * 0.8}" rx="${w * 0.3}" fill="#c9524a" stroke="${C.tinta}" stroke-width="5"/>` +
          `<rect x="${w * 0.08}" y="${h * 0.55}" width="${w * 0.84}" height="${h * 0.07}" fill="${C.tinta}" opacity=".3"/>`;
        // moto de lado
        const motoN = (w, h) => [0.2, 0.8].map((x) => `<circle cx="${w * x}" cy="${h * 0.74}" r="${h * 0.22}" fill="${C.tinta}"/><circle cx="${w * x}" cy="${h * 0.74}" r="${h * 0.09}" fill="${C.claro}"/>`).join("") +
          `<path d="M${w * 0.2} ${h * 0.74} L${w * 0.42} ${h * 0.42} L${w * 0.7} ${h * 0.42} L${w * 0.8} ${h * 0.74}" fill="none" stroke="${C.verm}" stroke-width="${h * 0.11}" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.34} ${h * 0.36} L${w * 0.56} ${h * 0.36}" stroke="${C.tinta}" stroke-width="${h * 0.09}" stroke-linecap="round"/>` +
          `<path d="M${w * 0.7} ${h * 0.42} L${w * 0.66} ${h * 0.12} L${w * 0.8} ${h * 0.12}" fill="none" stroke="${C.tinta}" stroke-width="${h * 0.06}" stroke-linecap="round"/>`;
        // o que FALTA: só o contorno tracejado (trem, trilho, pedra das terras raras)
        const TRACO = `fill="none" stroke="${C.tinta}" stroke-width="6" stroke-dasharray="16 11" stroke-linejoin="round" stroke-linecap="round"`;
        const tremN = (w, h) => `<path d="M${w * 0.04} ${h * 0.78} L${w * 0.04} ${h * 0.32} Q${w * 0.04} ${h * 0.1} ${w * 0.22} ${h * 0.1} L${w * 0.6} ${h * 0.1} L${w * 0.6} ${h * 0.78} Z" ${TRACO}/>` +
          `<rect x="${w * 0.64}" y="${h * 0.24}" width="${w * 0.32}" height="${h * 0.54}" rx="8" ${TRACO}/>` +
          [0.14, 0.34].map((x) => `<rect x="${w * x}" y="${h * 0.24}" width="${w * 0.14}" height="${h * 0.2}" rx="4" ${TRACO}/>`).join("") +
          [0.14, 0.34, 0.72, 0.88].map((x) => `<circle cx="${w * x}" cy="${h * 0.86}" r="${h * 0.1}" ${TRACO}/>`).join("");
        const trilhoN = (w, h) => `<path d="M0 ${h * 0.3} L${w} ${h * 0.3} M0 ${h * 0.7} L${w} ${h * 0.7}" ${TRACO}/>` +
          Array.from({ length: Math.floor(w / 60) }, (_, k) => `<path d="M${30 + k * 60} ${h * 0.12} L${30 + k * 60} ${h * 0.88}" ${TRACO}/>`).join("");
        const pedraN = (w, h) => `<path d="M${w * 0.08} ${h * 0.92} L${w * 0.02} ${h * 0.55} L${w * 0.2} ${h * 0.2} L${w * 0.52} ${h * 0.06} L${w * 0.82} ${h * 0.22} L${w * 0.98} ${h * 0.6} L${w * 0.9} ${h * 0.92} Z" ${TRACO}/>` +
          [[0.36, 0.42], [0.62, 0.36], [0.5, 0.66]].map(([x, y]) => `<path d="M${w * x} ${h * y - 14} L${w * x} ${h * y + 14} M${w * x - 14} ${h * y} L${w * x + 14} ${h * y}" ${TRACO}/>`).join("");
        // fábrica de papel: os dentes do telhado, a chaminé e a porta (o carro sai por ela)
        const fabricaN = (w, h) => `<rect x="${w * 0.72}" y="${h * 0.04}" width="${w * 0.1}" height="${h * 0.4}" fill="#9a948a" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="M${w * 0.03} ${h * 0.97} L${w * 0.03} ${h * 0.42} L${w * 0.2} ${h * 0.28} L${w * 0.2} ${h * 0.42} L${w * 0.37} ${h * 0.28} L${w * 0.37} ${h * 0.42} L${w * 0.54} ${h * 0.28} L${w * 0.54} ${h * 0.42} L${w * 0.97} ${h * 0.42} L${w * 0.97} ${h * 0.97} Z" fill="${C.kraft}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          [0.1, 0.27].map((x) => `<rect x="${w * x}" y="${h * 0.52}" width="${w * 0.12}" height="${h * 0.14}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>`).join("") +
          `<rect x="${w * 0.5}" y="${h * 0.6}" width="${w * 0.38}" height="${h * 0.37}" fill="${C.tinta}" opacity=".85"/>`;
        // carro de lado, na cor pedida
        const carroN = (w, h, cor = C.verm) => `<path d="M${w * 0.04} ${h * 0.72} L${w * 0.04} ${h * 0.5} Q${w * 0.06} ${h * 0.42} ${w * 0.18} ${h * 0.4} L${w * 0.3} ${h * 0.14} L${w * 0.68} ${h * 0.14} L${w * 0.8} ${h * 0.4} Q${w * 0.96} ${h * 0.42} ${w * 0.96} ${h * 0.56} L${w * 0.96} ${h * 0.72} Z" fill="${cor}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<path d="M${w * 0.34} ${h * 0.2} L${w * 0.48} ${h * 0.2} L${w * 0.48} ${h * 0.4} L${w * 0.26} ${h * 0.4} Z M${w * 0.53} ${h * 0.2} L${w * 0.65} ${h * 0.2} L${w * 0.74} ${h * 0.4} L${w * 0.53} ${h * 0.4} Z" fill="${C.azul2}" stroke="${C.tinta}" stroke-width="4"/>` +
          [0.24, 0.76].map((x) => `<circle cx="${w * x}" cy="${h * 0.74}" r="${h * 0.17}" fill="${C.tinta}"/><circle cx="${w * x}" cy="${h * 0.74}" r="${h * 0.07}" fill="${C.claro}"/>`).join("");
        // a régua dos 10 anos, casa a casa (vazia)
        // só o 1º e o último ano escritos: os dez nomes no celular ficavam ilegíveis (fotos de 10/10)
        const anosN = (w, h, n = 10, a0 = 2027) => Array.from({ length: n }, (_, k) => {
          const cw = w / n;
          return `<rect x="${k * cw + 3}" y="3" width="${cw - 6}" height="${h * 0.6}" rx="6" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>` +
            (k === 0 || k === n - 1 ? fT(k * cw + cw / 2, h * 0.97, String(a0 + k), h * 0.3, C.tinta) : "");
        }).join("");
        // etiqueta de preço com o furo e o barbante
        const precoN = (w, h, txt) => `<path d="M${w * 0.22} 4 L${w - 4} 4 L${w - 4} ${h - 4} L${w * 0.22} ${h - 4} L4 ${h / 2} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>` +
          `<circle cx="${w * 0.2}" cy="${h / 2}" r="${h * 0.09}" fill="${C.papel}" stroke="${C.tinta}" stroke-width="3"/>` + fT(w * 0.6, h / 2 + caber(txt, w * 0.66, h * 0.5) * 0.36, txt, caber(txt, w * 0.66, h * 0.5), C.tinta);
        // o painel de cotações (fundo escuro); as linhas entram por cima, cada uma no seu tempo
        const painelN = (w, h) => `<rect x="4" y="4" width="${w - 8}" height="${h - 8}" rx="16" fill="#1e1b2e" stroke="${C.tinta}" stroke-width="6"/>` +
          `<rect x="4" y="4" width="${w - 8}" height="${h * 0.18}" rx="16" fill="${VERDE2}"/>` + fT(w / 2, h * 0.13 + 4, "BOLSA DE VALORES", caber("BOLSA DE VALORES", w * 0.8, h * 0.1), C.claro);
        // a boleta de compra: o cabeçalho verde e a quantidade em letra grande
        const boletaN = (w, h, a, b) => `<path d="${pRet(w, h, 4747, 1.3, 30)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<rect x="0" y="0" width="${w}" height="${h * 0.34}" rx="8" fill="${VERDE}"/>` + fT(w / 2, h * 0.24, a, caber(a, w * 0.85, h * 0.2), C.claro) +
          fT(w / 2, h * 0.8, b, caber(b, w * 0.85, h * 0.36), C.tinta);
        const linhaBolsa = (w, h, cod, var_) => fT(w * 0.05, h * 0.72, cod, h * 0.62, "#7be08c", "start") + fT(w * 0.95, h * 0.72, var_, h * 0.62, "#7be08c", "end");

        // ── abertura nova do C46 (o terreno da obra parada) ───────────────────
        // guindaste de treliça: a torre, a lança, o contrapeso; o cabo e o gancho vão num objeto à parte (balançam)
        const guindasteN = (w, h) => {
          const tx = w * 0.3, tw = w * 0.1, ly = h * 0.1;
          let t = `<rect x="${tx}" y="${ly}" width="${tw}" height="${h - ly}" fill="none" stroke="${C.amar}" stroke-width="7"/>`;
          for (let y = ly; y < h - 20; y += tw * 1.1) t += `<path d="M${tx} ${y} L${tx + tw} ${y + tw * 1.1} M${tx + tw} ${y} L${tx} ${y + tw * 1.1}" stroke="${C.amar}" stroke-width="4"/>`;
          t += `<rect x="0" y="${ly - 16}" width="${w}" height="20" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/>`;
          t += `<rect x="${w * 0.02}" y="${ly + 4}" width="${w * 0.14}" height="${h * 0.08}" fill="#9a948a" stroke="${C.tinta}" stroke-width="4"/>`;
          t += `<rect x="${tx - 14}" y="${ly + 4}" width="${tw + 28}" height="${h * 0.07}" rx="4" fill="${C.tinta}"/>`;
          return t + `<rect x="${tx - 30}" y="${h - 14}" width="${tw + 60}" height="14" fill="${C.tinta}"/>`;
        };
        const ganchoN = (w, h) => `<path d="M${w / 2} 0 L${w / 2} ${h - 46}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w / 2} ${h - 46} L${w / 2} ${h - 20} Q${w / 2} ${h - 2} ${w / 2 - 16} ${h - 4} Q${w / 2 - 28} ${h - 8} ${w / 2 - 24} ${h - 22}" fill="none" stroke="${C.tinta}" stroke-width="8" stroke-linecap="round"/>`;
        // placa de obra: dois postes, o cabeçalho e o quadro do projeto EM BRANCO
        const placaObraN = (w, h, txt) => `<rect x="${w * 0.12}" y="${h * 0.5}" width="14" height="${h * 0.5}" fill="${C.tinta}"/><rect x="${w * 0.84}" y="${h * 0.5}" width="14" height="${h * 0.5}" fill="${C.tinta}"/>` +
          `<path d="${pRet(w, h * 0.72, 9191, 1.2, 34)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="6"/>` +
          `<rect x="0" y="0" width="${w}" height="${h * 0.18}" fill="${VERDE2}"/>` + fT(w / 2, h * 0.12, txt, caber(txt, w * 0.86, h * 0.1), C.claro) +
          fT(w * 0.08, h * 0.3, "PROJETO:", h * 0.06, C.tinta, "start") + `<rect x="${w * 0.36}" y="${h * 0.27}" width="${w * 0.54}" height="4" fill="${C.tinta}" opacity=".35"/>` +
          fT(w * 0.08, h * 0.42, "PRAZO:", h * 0.06, C.tinta, "start") + `<rect x="${w * 0.3}" y="${h * 0.39}" width="${w * 0.6}" height="4" fill="${C.tinta}" opacity=".35"/>` +
          fT(w * 0.08, h * 0.54, "VALOR:", h * 0.06, C.tinta, "start") + `<rect x="${w * 0.3}" y="${h * 0.51}" width="${w * 0.6}" height="4" fill="${C.tinta}" opacity=".35"/>`;
        // bola de feno: os galhos enrolados (rola pelo terreno vazio)
        const fenoN = (d) => {
          // galhos soltos e tortos, de vários tamanhos (a 1ª versão, com o contorno tracejado, parecia uma engrenagem)
          const r = d / 2, cores = ["#8a6a3c", "#a5834f", "#6f5430"];
          let t = `<circle cx="${r}" cy="${r}" r="${r * 0.82}" fill="#c9ab78" opacity=".45"/>`;
          for (let k = 0; k < 16; k++) {
            const a = rnd(k * 7.1 + 3) * Math.PI * 2, b = a + 1.2 + rnd(k * 3.3) * 2.2, ra = r * (0.55 + rnd(k * 1.7) * 0.42), rb = r * (0.5 + rnd(k * 2.9) * 0.45);
            const cx = r + (rnd(k * 5.3) - 0.5) * r * 0.9, cy = r + (rnd(k * 9.1) - 0.5) * r * 0.9;
            t += `<path d="M${r + Math.cos(a) * ra} ${r + Math.sin(a) * ra} Q${cx} ${cy} ${r + Math.cos(b) * rb} ${r + Math.sin(b) * rb}" fill="none" stroke="${cores[k % 3]}" stroke-width="${3 + (k % 3)}" stroke-linecap="round"/>`;
          }
          return t;
        };
        // o verso da folha: o papel sem nada
        const versoN = (w, h) => `<path d="${pRet(w, h, 8181 + w, 1.4, 34)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>`;

        // ── desenhos do C47 (não é o que é dito, é quem disse, 10/10/2026) ──────
        // grade de cadeia: moldura e barras verticais (cai sobre os três presidentes)
        const gradeN = (w, h, n = 9) => `<rect x="6" y="6" width="${w - 12}" height="${h - 12}" rx="8" fill="none" stroke="#5d6270" stroke-width="16"/>` +
          Array.from({ length: n }, (_, k) => `<rect x="${(w / (n + 1)) * (k + 1) - 7}" y="10" width="14" height="${h - 20}" rx="6" fill="#7b8190" stroke="${C.tinta}" stroke-width="3"/>`).join("") +
          `<rect x="10" y="${h * 0.32}" width="${w - 20}" height="14" fill="#5d6270"/>`;
        // tijolo da obra do país (empilha e desaba)
        const tijoloN = (w, h, cor = "#c26a4a") => `<rect x="3" y="3" width="${w - 6}" height="${h - 6}" rx="6" fill="${cor}" stroke="${C.tinta}" stroke-width="4"/>` +
          `<path d="M${w * 0.5} 3 L${w * 0.5} ${h * 0.5} M3 ${h * 0.5} L${w - 3} ${h * 0.5} M${w * 0.25} ${h * 0.5} L${w * 0.25} ${h - 3} M${w * 0.75} ${h * 0.5} L${w * 0.75} ${h - 3}" stroke="${C.tinta}" stroke-width="3" opacity=".45"/>`;
        // troféu (ganhar a eleição)
        const trofeuN = (w, h) => recorteP(`<path d="M${w * 0.22} ${h * 0.06} L${w * 0.78} ${h * 0.06} L${w * 0.74} ${h * 0.42} Q${w * 0.5} ${h * 0.62} ${w * 0.26} ${h * 0.42} Z" fill="${C.amar}" stroke="${C.tinta}" stroke-width="5"/>` +
          `<path d="M${w * 0.22} ${h * 0.12} Q${w * 0.02} ${h * 0.14} ${w * 0.1} ${h * 0.3} Q${w * 0.16} ${h * 0.4} ${w * 0.28} ${h * 0.4} M${w * 0.78} ${h * 0.12} Q${w * 0.98} ${h * 0.14} ${w * 0.9} ${h * 0.3} Q${w * 0.84} ${h * 0.4} ${w * 0.72} ${h * 0.4}" fill="none" stroke="${C.tinta}" stroke-width="6"/>` +
          `<rect x="${w * 0.44}" y="${h * 0.56}" width="${w * 0.12}" height="${h * 0.2}" fill="${C.amar}" stroke="${C.tinta}" stroke-width="4"/><rect x="${w * 0.24}" y="${h * 0.76}" width="${w * 0.52}" height="${h * 0.18}" rx="6" fill="${C.tinta}"/>`);
        // engrenagem (a economia girando)
        const engrenagemN = (d, cor = "#9aa0ae") => {
          const r = d / 2, dentes = 10;
          let p = "";
          for (let k = 0; k < dentes; k++) {
            const a = (k / dentes) * Math.PI * 2, b = a + Math.PI / dentes;
            p += `<rect x="${r - d * 0.07}" y="2" width="${d * 0.14}" height="${d * 0.16}" rx="3" fill="${cor}" stroke="${C.tinta}" stroke-width="3" transform="rotate(${(a * 180) / Math.PI} ${r} ${r})"/>`;
          }
          return p + `<circle cx="${r}" cy="${r}" r="${r * 0.72}" fill="${cor}" stroke="${C.tinta}" stroke-width="5"/><circle cx="${r}" cy="${r}" r="${r * 0.24}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="4"/>`;
        };
        // torcida: a multidão de bustos com a camisa nas cores dadas (as duas bases do 2º turno)
        function torcidaN(w, h, n, linhas, seed, cores) {
          let s = "";
          const porLinha = Math.ceil(n / linhas);
          for (let l = linhas - 1; l >= 0; l--) {
            const esc = 1 - l * 0.12, fw = w / porLinha, y = h - (h / linhas) * (l + 1) * 0.9;
            for (let c = 0; c < porLinha && l * porLinha + c < n; c++) {
              const i = seed + l * 31 + c, p = PELE[i % 4], cab = ["#2a1d14", "#c9c4bc", C.tinta, "#7a4a22", "#5a3a1a"][i % 5];
              const roupa = cores[(i * 7) % cores.length];
              const x = c * fw + (l % 2 ? fw * 0.45 : 0) + (rnd(i) - 0.5) * fw * 0.2, k = (fw / 50) * esc * (0.92 + rnd(i + 5) * 0.16);
              const f = `<path d="M4 90 L4 48 Q4 36 16 36 L34 36 Q46 36 46 48 L46 90 Z" fill="${roupa}"/><circle cx="25" cy="22" r="16" fill="${p}"/><path d="M9 20 Q10 4 25 4 Q40 4 41 20 Q34 12 25 12 Q16 12 9 20 Z" fill="${cab}"/>` +
                `<circle cx="20" cy="23" r="2.2" fill="${C.tinta}"/><circle cx="30" cy="23" r="2.2" fill="${C.tinta}"/><path d="M20 29 Q25 33 30 29" stroke="${C.tinta}" stroke-width="2" fill="none" stroke-linecap="round"/>`;
              s += `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${k.toFixed(3)})" opacity="${l ? 0.85 : 1}">${recorteP(f)}</g>`;
            }
          }
          return s;
        }
