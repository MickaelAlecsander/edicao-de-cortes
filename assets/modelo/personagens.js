
        // ══════════════════════════════════════════════════════════════════════
        // BANCO DE PERSONAGENS (06/10/2026, aprovado pelo Mickael no mock-up: "tá tooooop demais, pode seguir com esses")
        // Boneco de papel recortado: rosto com 5 expressões, braços que giram no ombro, pele/cabelo/roupa por tipo, contorno
        // claro de recorte e sombra. Entra no cenas.js depois do _ajudantes.js (montar.py). Precisa de C, fT, obj, tl, S.
        //   const m = personagem(c0, "min0", x, y, 220, TIPO.ministro, { expr: "feliz" });
        //   expressao("min0", "bravo", t);  gesto("min0", "d", -95, t);  tira("min0", "toga", t);
        // Pessoa real: nunca a cara de ninguém, só o TIPO com o nome numa etiqueta. Exceções pedidas pelo Mickael: o Raul
        // (TIPO.raul, 09/10/2026), que interage com as cenas quando a fala pede, e as caricaturas que ele pedir.
        // ══════════════════════════════════════════════════════════════════════
        const PELE = ["#f3cfb0", "#dca57f", "#b37850", "#7a4c33"];
        const EXPRS = ["neutro", "feliz", "bravo", "surpreso", "preocupado", "rindo", "ironico"];   // rindo e irônico: 10/10/2026
        function rostoP(expr) {
          const e = { neutro: 6, feliz: 6, bravo: 5, surpreso: 8, preocupado: 6, rindo: 6, ironico: 5 }[expr];
          const sob = { neutro: [0, 0], feliz: [-4, 4], bravo: [14, -14], surpreso: [-10, 10], preocupado: [-14, 14], rindo: [-8, 8], ironico: [-14, 6] }[expr];
          const sy = expr === "surpreso" ? 66 : 72;
          const boca = {
            neutro: `<path d="M86 116 L114 116" stroke="${C.tinta}" stroke-width="5" stroke-linecap="round"/>`,
            feliz: `<path d="M82 110 Q100 132 118 110 Z" fill="${C.tinta}"/><path d="M90 121 Q100 127 110 121" stroke="${C.verm}" stroke-width="5" fill="none" stroke-linecap="round"/>`,
            bravo: `<path d="M84 122 Q100 110 116 122" stroke="${C.tinta}" stroke-width="5" fill="none" stroke-linecap="round"/>`,
            surpreso: `<ellipse cx="100" cy="119" rx="9" ry="12" fill="${C.tinta}"/>`,
            preocupado: `<path d="M86 120 Q93 113 100 118 Q107 123 114 116" stroke="${C.tinta}" stroke-width="5" fill="none" stroke-linecap="round"/>`,
            rindo: `<path d="M78 106 Q100 142 122 106 Z" fill="${C.tinta}"/><path d="M88 124 Q100 133 112 124" stroke="${C.verm}" stroke-width="7" fill="none" stroke-linecap="round"/>`,
            ironico: `<path d="M86 118 Q104 122 116 110" stroke="${C.tinta}" stroke-width="5" fill="none" stroke-linecap="round"/>`,
          }[expr];
          // rindo: os olhos viram dois arcos fechados (^ ^)
          const olhos = expr === "rindo"
            ? `<path d="M74 90 Q82 80 90 90" stroke="${C.tinta}" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M110 90 Q118 80 126 90" stroke="${C.tinta}" stroke-width="5" fill="none" stroke-linecap="round"/>`
            : `<ellipse cx="82" cy="88" rx="${e * 0.8}" ry="${e}" fill="${C.tinta}"/><ellipse cx="118" cy="88" rx="${e * 0.8}" ry="${e}" fill="${C.tinta}"/><circle cx="84" cy="85" r="1.8" fill="${C.claro}"/><circle cx="120" cy="85" r="1.8" fill="${C.claro}"/>`;
          return `<path d="M70 ${sy} L94 ${sy}" stroke="${C.tinta}" stroke-width="5" stroke-linecap="round" transform="rotate(${sob[0]} 82 ${sy})"/><path d="M106 ${sy} L130 ${sy}" stroke="${C.tinta}" stroke-width="5" stroke-linecap="round" transform="rotate(${sob[1]} 118 ${sy})"/>` +
            `<g class="olhosP">${olhos}</g>` +
            (expr === "feliz" || expr === "rindo" ? `<circle cx="70" cy="106" r="8" fill="${C.rosa}" opacity=".7"/><circle cx="130" cy="106" r="8" fill="${C.rosa}" opacity=".7"/>` : "") +
            `<path d="M98 96 Q94 104 100 106" stroke="${C.tinta}" stroke-width="3" fill="none" opacity=".45" stroke-linecap="round"/>` + boca;
        }
        const CABELOP = {
          curto: (c) => `<path d="M50 86 Q48 36 100 34 Q152 36 150 86 Q140 58 100 56 Q60 58 50 86 Z" fill="${c}"/>`,
          grisalho: (c) => `<path d="M50 84 Q50 40 100 38 Q150 40 150 84 Q146 66 132 60 Q100 70 70 58 Q56 66 50 84 Z" fill="${c}"/>`,
          coque: (c) => `<circle cx="100" cy="32" r="22" fill="${c}"/><path d="M48 96 Q44 34 100 34 Q156 34 152 96 Q146 62 100 56 Q56 62 48 96 Z" fill="${c}"/>`,
          careca_barba: (c) => `<path d="M58 100 Q60 150 100 152 Q140 150 142 100 Q132 128 100 128 Q68 128 58 100 Z" fill="${c}"/><path d="M84 116 Q100 110 116 116" stroke="${c}" stroke-width="7" fill="none" stroke-linecap="round"/>`,
          bone: (c) => `<path d="M48 76 Q50 32 100 32 Q150 32 152 76 Z" fill="${c}"/><path d="M100 70 L176 76 Q180 84 170 86 L100 82 Z" fill="${c}"/>`,
          // cabelo comprido e liso que cai na frente dos ombros (C37, 08/10/2026: a personagem da Erika Hilton)
          longo: (c) => `<path d="M46 104 Q38 38 100 32 Q162 38 154 104 L162 196 Q150 206 136 194 L140 104 Q132 62 100 58 Q68 62 60 104 L64 194 Q50 206 38 196 Z" fill="${c}"/>`,
          // topete com volume, jogado para o lado (C37: o Nikolas no estilo dos personagens)
          topete: (c) => `<path d="M50 90 Q42 34 102 28 Q160 30 152 88 Q148 62 128 58 Q138 48 112 46 Q96 56 80 52 Q60 60 50 90 Z" fill="${c}"/>`,
          // o Raul (09/10/2026, C44, pedido do Mickael: "um personagem parecido com o Raul"): cabelo escuro, cheio e ondulado,
          // jogado para o lado, com os cachos marcados por traços mais claros
          raul: (c) => `<path d="M48 98 Q36 70 46 46 Q52 22 76 14 Q92 2 112 8 Q136 4 150 22 Q166 40 158 70 Q156 86 152 98 Q148 76 136 66 Q124 76 108 64 Q92 78 74 66 Q60 74 56 90 Z" fill="${c}"/>` +
            `<path d="M58 40 Q70 26 86 32 M92 18 Q106 10 120 20 M126 28 Q142 30 148 46 M70 54 Q84 44 98 52 M108 44 Q122 40 132 52" stroke="#4a3626" stroke-width="4.5" fill="none" stroke-linecap="round" opacity=".85"/>` +
            `<path d="M66 70 L92 66 M108 66 L134 70" stroke="${c}" stroke-width="7" stroke-linecap="round"/>`,
        };
        // contorno de papel: a mesma forma por baixo, clara e mais grossa
        const recorteP = (s) => `<g stroke="${C.claro}" stroke-width="16" stroke-linejoin="round" stroke-linecap="round">${s.replace(/fill="(?!none)[^"]*"/g, `fill="${C.claro}"`)}</g>${s}`;
        const TIPO = {
          ministro: { pele: PELE[0], roupa: C.azul2, calca: C.tinta, camisa: C.claro, gravata: C.verm, toga: "#15131f", cabelo: "grisalho", corCabelo: "#c9c4bc", oculos: true },
          politico: { pele: PELE[1], roupa: C.azul2, calca: C.tinta, camisa: C.claro, gravata: C.verm, cabelo: "curto", corCabelo: "#2a1d14" },
          empresario: { pele: PELE[0], roupa: C.tinta, calca: C.tinta, camisa: C.claro, gravata: C.verm, cabelo: "curto", corCabelo: "#4a2f20" },
          trabalhador: { pele: PELE[1], roupa: C.azul, calca: C.azul2, capacete: true },
          aposentado: { pele: PELE[2], roupa: C.kraft2, calca: "#5b5346", cabelo: "grisalho", corCabelo: "#eeeae2" },
          cidada: { pele: PELE[3], roupa: C.rosa2, calca: C.azul2, cabelo: "coque", corCabelo: "#24160f" },
          // jovem SEM boné desde 12/10/2026 (Mickael: "você tá usando muito personagem de boné, eu não quero isso"); o boné
          // ("bone") fica para um cidadão comum, num momento oportuno, no máximo um por vídeo
          jovem: { pele: PELE[2], roupa: "#3c9a4f", calca: C.tinta, cabelo: "curto", corCabelo: "#2a1d14" },
          // o Raul: camisa preta de manga curta (12/10/2026; era manga comprida), bigode e barba rala, relógio dourado no pulso
          // esquerdo (C44)
          raul: { pele: "#e2ad86", roupa: "#17151f", calca: "#2a2838", cabelo: "raul", corCabelo: "#1f1611", bigode: true, barba: true, gola: true, relogio: true, frente: "d", mangaCurta: true },
        };
        // o boneco em 200 × 400 (ombros em 52,170 e 148,170); id prefixa as partes animáveis
        function bonecoP(id, o) {
          const p = o.pele, r = o.roupa, ca = o.calca || C.tinta;
          const bracoP = (lado, nome) => { const x = lado < 0 ? 52 : 148;
            const rel = o.relogio && lado < 0 ? `<rect x="${x - 15}" y="256" width="30" height="12" rx="3" fill="#c9a24a" stroke="${C.tinta}" stroke-width="2"/>` : "";
            // manga curta: o braço é pele e a manga (a cor da camisa, um pouco mais larga) cobre só do ombro até ~214, com a
            // barra mais escura na ponta (o Raul, Mickael 12/10/2026: "camisa de manga mais curta… sem ser manga larga")
            const braco = o.mangaCurta
              ? `<rect x="${x - 13}" y="160" width="26" height="118" rx="13" fill="${p}"/><path d="M${x - 17} 214 L${x - 17} 166 Q${x - 17} 154 ${x} 154 Q${x + 17} 154 ${x + 17} 166 L${x + 17} 214 Z" fill="${o.manga || r}"/><rect x="${x - 17}" y="206" width="34" height="8" fill="#2c2a38"/>`
              : `<rect x="${x - 13}" y="160" width="26" height="118" rx="13" fill="${o.manga || r}"/>`;
            return `<g id="${id}-b${nome}">${recorteP(braco + `<circle cx="${x}" cy="284" r="15" fill="${p}"/>`)}${rel}</g>`; };
          let corpo = `<rect x="64" y="296" width="32" height="96" rx="8" fill="${ca}"/><rect x="104" y="296" width="32" height="96" rx="8" fill="${ca}"/><ellipse cx="78" cy="392" rx="22" ry="9" fill="${C.tinta}"/><ellipse cx="122" cy="392" rx="22" ry="9" fill="${C.tinta}"/>` +
            `<path d="M40 180 Q40 150 70 148 L130 148 Q160 150 160 180 L152 306 L48 306 Z" fill="${r}"/>` +
            (o.camisa ? `<path d="M84 148 L100 188 L116 148 Z" fill="${o.camisa}"/>` : "") + (o.gravata ? `<path d="M96 156 L104 156 L108 206 L100 216 L92 206 Z" fill="${o.gravata}"/>` : "") +
            `<rect x="88" y="128" width="24" height="26" fill="${p}"/><circle cx="52" cy="94" r="10" fill="${p}"/><circle cx="148" cy="94" r="10" fill="${p}"/><circle cx="100" cy="90" r="50" fill="${p}"/>`;
          const toga = o.toga ? `<g id="${id}-toga">${recorteP(`<path d="M44 178 Q44 150 72 148 L128 148 Q156 150 156 178 L170 392 L30 392 Z" fill="${o.toga}"/><path d="M84 148 L100 192 L116 148 Z" fill="${C.claro}"/>`)}<path d="M92 150 L100 172 L108 150" fill="none" stroke="${C.kraft2}" stroke-width="2"/></g>` : "";
          const cabeca = (o.cabelo ? CABELOP[o.cabelo](o.corCabelo || C.tinta) : "") +
            (o.oculos ? `<circle cx="82" cy="88" r="13" fill="none" stroke="${C.tinta}" stroke-width="4"/><circle cx="118" cy="88" r="13" fill="none" stroke="${C.tinta}" stroke-width="4"/><path d="M95 88 L105 88" stroke="${C.tinta}" stroke-width="4"/>` : "") +
            (o.capacete ? `<path d="M46 74 Q48 26 100 26 Q152 26 154 74 Z" fill="${C.amar}"/><rect x="40" y="70" width="120" height="12" rx="5" fill="${C.amar2}"/><rect x="96" y="28" width="8" height="44" fill="${C.amar2}"/>` : "");
          const rostos = EXPRS.map((e) => `<g id="${id}-e-${e}" opacity="${e === (o.expr || "neutro") ? 1 : 0}">${rostoP(e)}</g>`).join("");
          const gola = o.gola ? `<path d="M78 148 L100 172 L122 148 L112 148 L100 162 L88 148 Z" fill="#2c2a38"/><circle cx="100" cy="182" r="3" fill="#3a3848"/><circle cx="100" cy="196" r="3" fill="#3a3848"/>` : "";
          const barba = o.barba ? `<path d="M54 98 Q58 142 100 144 Q142 142 146 98 Q140 122 122 128 Q100 136 78 128 Q60 122 54 98 Z" fill="${o.corCabelo || C.tinta}" opacity=".32"/>` : "";
          const bigode = o.bigode ? `<path d="M82 109 Q91 101 100 106 Q109 101 118 109 Q110 113 100 110 Q90 113 82 109 Z" fill="${o.corCabelo || C.tinta}"/>` : "";
          // o.frente = "d" (ou "e"): esse braço vai por cima do corpo e da cabeça, para a mão no rosto (o Raul, C44)
          const be = o.frente === "e" ? "" : bracoP(-1, "e"), bd = o.frente === "d" ? "" : bracoP(1, "d");
          const fr = o.frente === "e" ? bracoP(-1, "e") : o.frente === "d" ? bracoP(1, "d") : "";
          // boca de fala (pisca aberta/fechada enquanto o balão está na tela) e o grupo vivo (respiração), 14/10/2026
          const bocaFala = `<g id="${id}-fala" opacity="0"><ellipse cx="100" cy="118" rx="11" ry="10" fill="${C.tinta}"/><path d="M93 123 Q100 127 107 123" stroke="${C.verm}" stroke-width="4" fill="none" stroke-linecap="round"/></g>`;
          return `<g id="${id}-vivo" filter="url(#sombraP)">${be}${bd}${recorteP(corpo)}${gola}${toga}${barba}${rostos}${bocaFala}${bigode}${recorteP(cabeca)}${fr}</g>`;
        }
        const OMBRO = { e: "52 170", d: "148 170" };
        // cria o personagem no mundo: w é a largura do boneco; a caixa tem folga para os braços
        function personagem(pai, id, x, y, w, tipo, extra = {}) {
          const o = Object.assign({}, tipo, extra), k = w / 200;
          const el = obj(pai, id, x - 80 * k, y - 40 * k, 360 * k, 460 * k,
            `<svg width="${360 * k}" height="${460 * k}" viewBox="-80 -40 360 460" style="overflow:visible"><defs><filter id="sombraP" x="-30%" y="-20%" width="160%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="5" flood-color="#1e1b2e" flood-opacity=".35"/></filter></defs>${bonecoP(id, o)}</svg>`, false);
          const [ae, ad] = o.pose || [8, 8];
          tl.set("#" + id + "-be", { rotation: ae, svgOrigin: OMBRO.e }, 0);
          tl.set("#" + id + "-bd", { rotation: -ad, svgOrigin: OMBRO.d }, 0);
          vidaP(id);
          return el;
        }
        // ── VIDA (14/10/2026, Mickael: "trazer esse aspecto mais animado… personagens mais interativos, movimentos mais
        // fluidos, olhos piscando… para os próximos vídeos padrões"; o nível das vertentes de gibi e caderno) ──────────────
        // piscar a cada 2,5–4,5 s, o olhar que muda de lado de vez em quando e a respiração (o corpo sobe 1,2% devagar, pés
        // parados). Tudo com semente do id: sai igual a cada render.
        function vidaP(id) {
          const sem = [...id].reduce((a, c) => a + c.charCodeAt(0), 0) * 7.3;
          const olhos = "#" + id + " .olhosP";
          for (let t = 0.8 + rnd(sem) * 2, k = 0; t < DUR; t += 2.5 + rnd(sem + ++k) * 2) {
            tl.to(olhos, { scaleY: 0.1, transformOrigin: "50% 50%", duration: 0.07, yoyo: true, repeat: 1, ease: "power2.in" }, t);
            if (rnd(sem + k * 3) < 0.25) tl.to(olhos, { scaleY: 0.1, transformOrigin: "50% 50%", duration: 0.06, yoyo: true, repeat: 1, ease: "power2.in" }, t + 0.22);
          }
          for (let t = 2 + rnd(sem + 50) * 3, k = 0; t < DUR; t += 3.5 + rnd(sem + 60 + ++k) * 3) {
            const dx = (rnd(sem + 70 + k) - 0.5) * 8;
            tl.to(olhos, { x: dx, duration: 0.16, ease: "power2.out" }, t);
            tl.to(olhos, { x: 0, duration: 0.2, ease: "power2.inOut" }, t + 1.1 + rnd(sem + 80 + k));
          }
          const per = 1.5 + rnd(sem + 90) * 0.5;
          tl.fromTo("#" + id + "-vivo", { scaleY: 1 }, { scaleY: 1.012, svgOrigin: "100 400", duration: per, yoyo: true,
            repeat: Math.ceil(DUR / per), ease: "sine.inOut", immediateRender: false }, rnd(sem + 95) * per);
        }
        // ang em graus a partir do braço pendurado; positivo = para fora do corpo (os dois lados)
        function gesto(id, lado, ang, t, dur = 0.25) {
          tl.to("#" + id + "-b" + lado, { rotation: lado === "e" ? ang : -ang, svgOrigin: OMBRO[lado], duration: dur, ease: S(dur, "back.out(1.6)") }, t);
        }
        function expressao(id, expr, t) {
          EXPRS.forEach((e) => tl.set("#" + id + "-e-" + e, { opacity: e === expr ? 1 : 0 }, t));
          if (t > 0.05) tl.fromTo("#" + id, { scale: 1.05 }, { scale: 1, transformOrigin: "50% 92%", duration: 0.32, ease: "back.out(2.2)", immediateRender: false }, t);
        }
        // ── INTERAÇÃO DENTRO DA CENA (Mickael, 10/10/2026: "personagem interagindo de fato com outro personagem… pode ser
        // que algum texto saia do próprio personagem… caixinha de texto, de fala") ──────────────────────────────────────────
        // a cabeça do personagem, em px do pai (o boneco tem viewBox -80 -40 360 460; a cabeça fica em torno de 100,34–150)
        const cabecaP = (id) => {
          const el = document.getElementById(id), k = parseFloat(el.style.width) / 360;
          return { x: parseFloat(el.style.left) + 180 * k, y: parseFloat(el.style.top) + 74 * k, k, pai: el.parentNode };
        };
        // o balão de fala: rabicho para baixo, apontando para a boca; lado 1 = balão à direita da cabeça, -1 = à esquerda
        const falaN = (w, h, lado, cor) => {
          const r = 16, b = h - 26, px = lado > 0 ? w * 0.18 : w * 0.82, tx = lado > 0 ? 4 : w - 4;
          return `<path d="M${r} 0 L${w - r} 0 Q${w} 0 ${w} ${r} L${w} ${b - r} Q${w} ${b} ${w - r} ${b} L${px + 14} ${b} L${tx} ${h} L${px - 14} ${b} L${r} ${b} Q0 ${b} 0 ${b - r} L0 ${r} Q0 0 ${r} 0 Z" fill="${cor}" stroke="${C.tinta}" stroke-width="5" stroke-linejoin="round"/>`;
        };
        let nFala = 0;
        // fala(id, "CORRUPTO!", t, 1.6, { lado: -1, cor: C.claro, tinta: C.verm }): o texto sai da boca do personagem;
        // "\n" quebra a linha; o.fs fixa o tamanho da letra
        function fala(id, txt, t, dur = 1.6, o = {}) {
          const { x, y, k, pai } = cabecaP(id), lado = o.lado || 1, fs = o.fs || Math.max(26, Math.round(56 * k));
          const linhas = String(txt).split("\n"), maior = Math.max(...linhas.map((l) => l.length));
          const w = Math.max(120, Math.round(maior * fs * 0.62) + 44), h = Math.round(linhas.length * fs * 1.12 + 56);
          const bx = lado > 0 ? x + 20 * k : x - 20 * k - w, by = y - h - 6 * k;
          const txtSvg = linhas.map((l, i) => fT(w / 2, 22 + fs * 0.86 + i * fs * 1.12, l, fs, o.tinta || C.tinta)).join("");
          const b = obj(pai, id + "-fala" + ++nFala, bx, by, w, h, falaN(w, h, lado, o.cor || C.claro) + txtSvg, true, false);
          b.style.zIndex = 30;
          b.style.transformOrigin = lado > 0 ? "0% 100%" : "100% 100%";
          aparece(b, t, 0.2, { scale: 0.2, y: 20 });
          tl.to(b, { autoAlpha: 0, scale: 0.8, duration: 0.15 }, t + dur);
          for (let q = 0, k = 0; q < dur - 0.1; q += 0.1 + rnd(nFala * 13 + ++k) * 0.06) tl.set("#" + id + "-fala", { opacity: k % 2 }, t + q);
          tl.set("#" + id + "-fala", { opacity: 0 }, t + dur);
          return b;
        }
        // risada: cara de riso, o corpo pula de leve e "HA HA" sobe da cabeça
        function risada(id, t, dur = 1.2) {
          expressao(id, "rindo", t);
          const n = Math.max(2, Math.round(dur / 0.16));
          tl.fromTo("#" + id, { y: 0 }, { y: -10, duration: 0.08, yoyo: true, repeat: n * 2 - 1, ease: "none", immediateRender: false }, t);
          const { x, y, k, pai } = cabecaP(id);
          ["HA", "HA"].forEach((h, i) => {
            const e = obj(pai, id + "-ha" + ++nFala, x + (i ? 40 : -90) * k, y - 30 * k, 90 * k + 30, 50, fT(45 * k + 15, 40, h, 34, C.verm), false, false);
            e.style.zIndex = 30;
            tl.set(e, { autoAlpha: 0 }, 0);
            tl.set(e, { autoAlpha: 1 }, t + i * 0.15);
            tl.to(e, { y: -60, rotation: i ? 12 : -12, duration: dur, ease: S(dur, "power1.out") }, t + i * 0.15);
            tl.set(e, { autoAlpha: 0 }, t + i * 0.15 + dur);
          });
        }
        // anda dentro da cena: o papel recortado dá pulinhos de passo e balança, em movimento contínuo; dx em px do pai
        function andaP(id, t, dur, dx) {
          const passos = Math.max(1, Math.round(dur * 2.4));
          const onda = (q) => (q >= 1 ? 0 : Math.abs(Math.sin(Math.PI * passos * q)));
          tl.to("#" + id, { x: "+=" + dx, duration: dur, ease: "none" }, t);
          tl.fromTo("#" + id, { y: 0 }, { y: -14, duration: dur, ease: onda, immediateRender: false }, t);
          tl.fromTo("#" + id, { rotation: -3 }, { rotation: 3, duration: dur / passos, yoyo: true, repeat: passos - 1, ease: "none", immediateRender: false }, t);
          tl.set("#" + id, { rotation: 0, y: 0 }, t + dur);
        }
        function tira(id, parte, t, dur = 0.35) {
          tl.to("#" + id + "-" + parte, { opacity: 0, y: 80, duration: dur, ease: S(dur, "power2.in") }, t);
        }
