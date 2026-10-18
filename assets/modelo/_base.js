        // ══════════════════════════════════════════════════════════════════════
        // BASE DO CORTE (o _c84_base.js generalizado). Entra no cenas.js depois do _cab48.js e antes das cenas (montar.py).
        // Precisa do motor (tl, obj, aparece, cena, vai, camS, ferve, fervura, rnd, DUR), dos bancos (personagens.js,
        // elementos.js, _ajudantes.js, _desenhos.js, _cab48.js) e da const TELAS, que o montar.py escreve no cabeçalho.
        //   telaCheia(n)            a folha que cobre a tela inteira na janela TELAS[n - 1] e devolve a folha de dentro
        //   camera([[1, t], ...])   o travelling entre as cenas, as janelas JAN (fervura e respiração) e a fervura
        // ══════════════════════════════════════════════════════════════════════
        const pe = (yChao, w = 180) => yChao - 392 * (w / 200);   // o y do personagem com os pés em yChao (tela cheia: 1600–1620)
        const estrelaN = (r, cor) => estrela(r, cor).replace("/>", ` stroke="${C.tinta}" stroke-width="2.5" stroke-linejoin="round"/>`);
        const vistoA = (c, id, x, y, t, s = 70) => { const v = obj(c, id, x, y, s, s, vistoN(s), false, false); aparece(v, t, 0.2, { scale: 2, y: 0, rotation: -15 }); return v; };
        // cresce no eixo (barra, pódio, pilha): ponha o transformOrigin no pé antes ("0% 50%" na barra, "50% 100%" no pódio)
        const cresce = (el, t, eixo = "scaleY", dur = 0.4) => {
          tl.set(el, { autoAlpha: 0 }, 0);
          tl.fromTo(el, { autoAlpha: 1, [eixo]: 0.05 }, { [eixo]: 1, duration: dur, ease: S(dur, "back.out(1.6)"), immediateRender: false }, t);
        };
        // cartão de papel com borda irregular (o fundo de um item numa tela cheia)
        const cartaoP = (w, h, seed) => `<path d="${pRet(w, h, seed, 1.3, 30)}" fill="${C.claro}" stroke="${C.tinta}" stroke-width="5"/>`;
        // o Raul personagem (TIPO.raul): SÓ quando a fala reage à cena (indignação, ironia, "que loucura"); nasce do chão
        const raulF = (c, id, x, y, t, expr = "neutro", w = 180) => {
          const p = personagem(c, id, x, y, w, TIPO.raul, { expr, pose: [8, 8] });
          brotaP("#" + id, t);
          return p;
        };

        // ── atuação (a do C72) ────────────────────────────────────────────────
        // flutua: o miolo sobe e desce até o fim do vídeo (objeto leve, balão, nuvem)
        const flutua = (el, t0, amp = 6, per = 2.4) => {
          const b = (typeof el === "string" ? document.querySelector(el) : el).firstChild;
          tl.fromTo(b, { y: 0 }, { y: -amp, duration: per / 2, yoyo: true, repeat: Math.max(1, Math.ceil((DUR - t0) / per) * 2), ease: "sine.inOut", immediateRender: false }, t0);
        };
        // pulinho de alegria ou susto: sobe, desce e amassa no chão
        const pulinho = (sel, t, alt = 30) => {
          tl.to(sel, { y: -alt, duration: 0.17, ease: "power2.out" }, t);
          tl.to(sel, { y: 0, duration: 0.21, ease: "power2.in" }, t + 0.17);
          tl.fromTo(sel, { scaleX: 1.09, scaleY: 0.91 }, { scaleX: 1, scaleY: 1, transformOrigin: "50% 95%", duration: 0.4, ease: "elastic.out(1, 0.4)", immediateRender: false }, t + 0.38);
        };
        // balança a cabeça (o corpo todo) dizendo "não"
        const nega = (id, t, n = 3) => {
          tl.fromTo("#" + id, { rotation: -4 }, { rotation: 4, transformOrigin: "50% 90%", duration: 0.13, yoyo: true, repeat: n * 2 - 1, ease: "sine.inOut", immediateRender: false }, t);
          tl.to("#" + id, { rotation: 0, duration: 0.12 }, t + n * 0.26);
        };
        // o olhar vai para (dx, dy) e volta no instante "volta"
        const olha = (id, dx, dy, t, volta) => {
          tl.to("#" + id + " .olhosP", { x: dx, y: dy, duration: 0.2, ease: "power2.out" }, t);
          if (volta) tl.to("#" + id + " .olhosP", { x: 0, y: 0, duration: 0.25, ease: "power2.inOut" }, volta);
        };
        const aceno = (id, lado, t, vezes = 2) => {
          const s = lado === "e" ? 1 : -1, braco = "#" + id + "-b" + lado;
          gesto(id, lado, 150, t, 0.22);
          tl.to(braco, { rotation: s * 120, svgOrigin: OMBRO[lado], duration: 0.13, yoyo: true, repeat: vezes * 2 - 1, ease: "sine.inOut" }, t + 0.24);
          gesto(id, lado, 8, t + 0.26 + vezes * 0.26, 0.3);
        };
        // duas gotas de suor descem da testa (esforço, nervoso)
        const suorP = (id, t) => {
          const { x, y, k, pai } = cabecaP(id);
          [0, 1].forEach((i) => {
            const g = obj(pai, id + "-suor" + i, x + (i ? -46 : 40) * k, y - 18 * k, 16, 24, gota(16, 24), false, false);
            g.style.zIndex = 8;
            tl.set(g, { autoAlpha: 0 }, 0);
            tl.fromTo(g, { autoAlpha: 1, y: 0, scale: 0.4 }, { y: 46, scale: 1, duration: 0.7, ease: "power1.in", immediateRender: false }, t + i * 0.35);
            tl.to(g, { autoAlpha: 0, duration: 0.15 }, t + i * 0.35 + 0.62);
          });
        };
        // estrelinhas que piscam em volta de (cx, cy) entre t0 e t1 (o que vale ouro, o que é desejado)
        const brilhos = (c, id, cx, cy, raio, t0, t1, n = 6) => {
          for (let k = 0; k < n; k++) {
            const r = 9 + rnd(k * 4.4 + 1) * 10, a = (k / n) * Math.PI * 2 + 0.4;
            const e = obj(c, id + k, cx + Math.cos(a) * raio - r, cy + Math.sin(a) * raio * 0.7 - r, 2 * r, 2 * r, estrelaN(r, k % 2 ? C.amar : C.claro), false, false);
            e.style.zIndex = 7;
            const per = 0.8 + rnd(k * 2.9) * 0.6, rep = Math.max(1, Math.floor((t1 - t0) / per));
            tl.set(e, { autoAlpha: 0 }, 0);
            tl.fromTo(e, { autoAlpha: 1, scale: 0, rotation: 0 }, { scale: 1, rotation: 90, duration: per / 2, yoyo: true, repeat: rep * 2 - 1, ease: "sine.inOut", immediateRender: false }, t0 + rnd(k * 6.1) * per);
            tl.set(e, { autoAlpha: 0 }, t1);
          }
        };
        // cédulas que voam em arco de (x0, y0) até (x1, y1), uma atrás da outra
        function cedulasVoam(c, id, x0, y0, x1, y1, t, n = 5, cor = C.azul) {
          for (let k = 0; k < n; k++) {
            const d = obj(c, id + k, x0, y0, 70, 46, cedulaN(70, 46, "", cor), true, false);
            d.style.zIndex = 6;
            const tk = t + k * 0.14, dx = x1 - x0 + (rnd(k * 3.3) - 0.5) * 120, dy = y1 - y0 + (rnd(k * 7.1) - 0.5) * 60;
            tl.set(d, { autoAlpha: 0 }, 0);
            tl.fromTo(d, { autoAlpha: 1, x: 0, y: 0, rotation: -20, scale: 0.6 }, { x: dx, rotation: 25, scale: 1, duration: 0.7, ease: "power1.inOut", immediateRender: false }, tk);
            tl.fromTo(d, { y: 0 }, { y: dy, duration: 0.7, ease: "back.in(1.2)", immediateRender: false }, tk);
            tl.to(d, { autoAlpha: 0, scale: 0.3, duration: 0.15 }, tk + 0.68);
          }
        }
        // curtidas saindo do celular, como num vídeo que viralizou
        const curte = (c, id, x, y, t, n = 7) => {
          for (let k = 0; k < n; k++) {
            const s = 34 + rnd(k * 9.1 + 3) * 20, h = obj(c, id + k, x + (rnd(k * 3.7) - 0.5) * 130, y, s, s, coracao(s, [C.verm, "#ff7a8a", C.rosa2][k % 3]), false, false);
            const tk = t + k * 0.3;
            h.style.zIndex = 7;
            tl.set(h, { autoAlpha: 0 }, 0);
            tl.fromTo(h, { autoAlpha: 1, scale: 0.2, y: 0, x: 0 }, { scale: 1, y: -170 - rnd(k) * 90, x: (rnd(k * 2.2) - 0.5) * 90, duration: 1.4, ease: "power1.out", immediateRender: false }, tk);
            tl.to(h, { autoAlpha: 0, duration: 0.35 }, tk + 1.05);
          }
        };

        // ── TELA CHEIA ────────────────────────────────────────────────────────
        // Uma folha do tamanho da tela sobe por baixo (0,52 s, a partir de t0 − 0,5) por cima do Raul e da folha de cima, e
        // desce de volta em t1 (0,46 s). A legenda fica por cima dela (#leg z 25) e a marca some enquanto ela está na tela.
        // As coisas de dentro usam o mesmo motor (obj, tg, personagem), com a origem no canto da TELA (coordenada = tela).
        // A janela vem da lista TELAS do montar.py, que também grava o assets/tela_cheia.json para o finalizar.py.
        // O que é criado depois dela ferve no grupo 49 + n (cenaAtual 50, 51…), até o próximo cena().
        const raiz = document.querySelector("#root");
        const CHEIAS = [];   // [t0, t1] de cada tela cheia, para o camera() tirar essas janelas das cenas
        const JAN = {};      // cena → [[a, z], ...]: quando ela está na tela (fervura aqui; respiração no _vida.js)
        function telaCheia(n, t0 = TELAS[n - 1][0], t1 = TELAS[n - 1][1]) {
          cenaAtual = 49 + n;
          const f = document.createElement("div");
          f.id = "cheia" + n; f.className = "cheia"; f.dataset.layoutAllowOverflow = "";
          f.innerHTML = `<div class="cheia-papel"></div><div class="cheia-grao"></div>`;
          // a borda de cima rasgada, como a da folha de cima
          const P = [];
          for (let x = 0; x <= 1080; x += 27) P.push(`${x}px ${(5 + rnd(x * 1.7 + n * 31) * 15).toFixed(1)}px`);
          f.style.clipPath = `polygon(${P.join(", ")}, 1080px 1920px, 0px 1920px)`;
          raiz.insertBefore(f, document.querySelector("#leg"));
          const dentro = document.createElement("div");
          dentro.className = "cheia-dentro"; dentro.dataset.layoutAllowOverflow = "";
          f.appendChild(dentro);
          tl.set(f, { autoAlpha: 0, y: 1980 }, 0);
          tl.set(f, { autoAlpha: 1 }, t0 - 0.5);
          tl.fromTo(f, { y: 1980, rotation: 1.4 }, { y: 0, rotation: 0, duration: 0.52, ease: "power3.out", immediateRender: false }, t0 - 0.5);
          tl.to(f, { y: 1980, rotation: -1.2, duration: 0.46, ease: "power2.in" }, t1);
          tl.set(f, { autoAlpha: 0 }, t1 + 0.47);
          tl.to("#marca", { autoAlpha: 0, duration: 0.2 }, t0 - 0.45);
          tl.to("#marca", { autoAlpha: 0.8, duration: 0.3 }, t1 + 0.42);
          CHEIAS.push([t0, t1]);
          JAN[cenaAtual] = [[t0 - 0.5, t1 + 0.5]];
          return dentro;
        }

        // ── CÂMERA: o travelling lateral, as janelas e a fervura (a ÚLTIMA chamada das cenas) ────────────────
        // paradas = [[cena, t], ...] na ordem: em t a câmera vai até a cena (vai(): 0,82 s, começa 0,32 s antes de t). A
        // cena 0 abre em 0 com a câmera em 1,0 (ponto (x, y) da cena → tela (x, y + 155)). Atrás de uma tela cheia, a troca vai
        // em t1 − 0,3: quando a folha desce, a cena nova já está lá. As janelas de cada cena saem das paradas, sem os trechos
        // cobertos pelas telas cheias; cada objeto ferve só na janela da sua cena (± 0,8 s).
        function camera(paradas) {
          camAtual = camS(0, 540, 1.0);
          tl.set(mundo, camAtual, 0);
          paradas.forEach(([i, t]) => vai(i, 540, t));
          const marcos = [[0, 0], ...paradas];
          marcos.forEach(([i, a], k) => {
            let pedacos = [[a, k + 1 < marcos.length ? marcos[k + 1][1] : DUR]];
            CHEIAS.forEach(([c0, c1]) => {
              pedacos = pedacos.flatMap(([x, z]) => (c1 <= x || c0 >= z ? [[x, z]] : [[x, c0], [c1, z]]));
            });
            (JAN[i] = JAN[i] || []).push(...pedacos.filter(([x, z]) => z - x > 0.1));
          });
          Object.keys(fervura).forEach((k) => {
            const i = +k;
            fervura[k].forEach((el, n) => {
              const amp = 0.45 + rnd(i * 50 + n) * 0.5, seed = i * 100 + n;
              (JAN[i] || []).forEach(([a, z], m) => ferve(el.firstChild, amp, seed + m * 7, Math.max(0, a - 0.8), Math.min(DUR, z + 0.8)));
            });
          });
        }
