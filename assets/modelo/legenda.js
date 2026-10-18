        // ── LEGENDA v3 (10/10/2026; a v2 era de 06/10, C27; o montar.py põe no lugar da legenda do motor) ──────────
        // v3, pedido do Mickael: "não quero ele serrilhado mais, eu quero ele mais normal… um pouco mais branco o fundo…
        // bordas levemente arredondadas… uma característica nossa, sem ficar tão padrão". É um cartão branco com borda de
        // tinta, cantos de 14 px e a sombra dura deslocada (o recorte de papel do canal), quase reto (±1°) e parado (sem a
        // fervura). A letra é menor, para não chegar nos botões do TikTok. Aparece direto (sem crescer, sem fita: 06/10). A palavra dita ganha o marca-texto amarelo; as que ainda vão ser ditas ficam
        // apagadas (o olho lê junto com a fala). Destaque (número, dinheiro, palavrão censurado, "destaques" do
        // cortes.json) em vermelho e com um soquinho na etiqueta. A fala do APRESENTADOR vem em papel escuro, para não
        // confundir com o Raul. O palavrão já chega censurado do legendas.py (F**A).
        (function () {
          const st = document.createElement("style");
          st.textContent = `
            #leg .etq { background: none; box-shadow: none; padding: 0; border-radius: 0; filter: none; }
            #leg .pp { position: relative; padding: 14px 28px 13px; background: #fffdf8; border: 4px solid #1e1b2e; border-radius: 14px;
              box-shadow: 6px 7px 0 #1e1b2e;
              font-family: "Archivo Black", sans-serif; color: #1e1b2e; line-height: 1; white-space: nowrap; letter-spacing: -0.01em; }
            #leg .fita { position: absolute; top: -14px; left: -20px; width: 86px; height: 30px; z-index: 2; background: rgba(214, 195, 160, 0.92); transform: rotate(-24deg); }
            #leg .fita.d { left: auto; right: -20px; transform: rotate(22deg); }
            #leg .w { display: inline-block; position: relative; }
            #leg .w b { position: relative; z-index: 1; font-weight: normal; }
            #leg .mk { position: absolute; left: -7px; right: -7px; top: 46%; bottom: -5px; background: #e9b23a; transform-origin: 0 50%; z-index: 0; border-radius: 3px; }
            #leg .forte b { color: #e5432d; }
            #leg .host .pp { background: #1e1b2e; color: #f8f2e4; border-color: #1e1b2e; box-shadow: 6px 7px 0 #e9b23a; }
            #leg .host .mk { background: #2c56a0; }
            #leg .host .forte b { color: #e9b23a; }
          `;
          document.head.appendChild(st);
        })();
        const leg = $("#leg");
        D.legenda.forEach((c, i) => {
          const host = c.quem && c.quem !== "raul";
          const e = document.createElement("div");
          e.className = "etq" + (host ? " host" : "");
          const txt = c.palavras.map((p) => p.w).join(" ");
          // menor desde 10/10/2026 (era até 92 px em 900; depois 72 em 720, que ainda chegava nos botões e na foto de perfil
          // do TikTok, à direita): até 58 px em 620
          const fs = Math.min(58, Math.floor(620 / (txt.length * 0.74)));
          e.innerHTML = `<div class="pp" style="font-size:${fs}px">` +
            c.palavras.map((p) => `<span class="w${p.forte ? " forte" : ""}"><i class="mk"></i><b>${p.w}</b></span>`).join(" ") + "</div>";
          leg.appendChild(e);
          const rot = (rnd(i + 3000) - 0.5) * 2;
          tl.set(e, { xPercent: -50, yPercent: -50, autoAlpha: 0 }, 0);
          // entra direto, já no tamanho final (Mickael, 06/10: a entrada que crescia roubava tempo de leitura)
          tl.set(e, { autoAlpha: 1, scale: 1, rotation: rot }, c.ini);
          tl.set(e, { autoAlpha: 0 }, c.fim);
          const ws = e.querySelectorAll(".w"), mks = e.querySelectorAll(".mk");
          c.palavras.forEach((p, k) => {
            const t = Math.max(c.ini, p.s - 0.03);
            tl.set(ws[k], { opacity: 0.3 }, 0);
            tl.set(mks[k], { scaleX: 0 }, 0);
            tl.set(ws[k], { opacity: 1 }, t);
            tl.fromTo(mks[k], { scaleX: 0 }, { scaleX: 1, duration: 0.1, ease: "power2.out", immediateRender: false }, t);
            if (k > 0 && p.forte) tl.fromTo(e, { scale: 1.05 }, { scale: 1, duration: 0.12, ease: S(0.17, "power2.out"), immediateRender: false }, t);
            if (k + 1 < c.palavras.length) tl.set(mks[k], { scaleX: 0 }, Math.max(t + 0.1, c.palavras[k + 1].s - 0.03));
          });
        });

