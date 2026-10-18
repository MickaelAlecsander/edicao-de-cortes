        // ══════════════════════════════════════════════════════════════════════
        // CENAS DE EXEMPLO: 2 cenas e 1 tela cheia, com as âncoras dos 2 primeiros blocos do C84 (os assets/tempos.json e
        // assets/dados.js do modelo). No corte novo: copie para _cenas.js, troque o elenco, as cenas e as âncoras T(), e ponha
        // o nome em CENAS no montar.py. O padrão:
        //   · uma constante por bloco (o id do tempos.json) e o elenco no topo: todo personagem tem papel na história;
        //   · cada cena num bloco com cabeçalho "CENA i · O QUE É (de a b s): o que se vê";
        //   · todo tempo vem de T(palavra, bloco, n), nunca de número solto; o 1º elemento entra com a 1ª palavra;
        //   · ÁREA DE SEGURANÇA: na cena, x 40–1040 e y 45–800 (o palco: tampo 560–650, pé em ~593 = TOPO 240 com 180 de
        //     largura); na tela cheia, y 150–1700, x 40–1040, x ≤ 920 de y 900 a 1700 e a faixa 880–990 livre (legenda);
        //   · camera([...]) é a última chamada: ela faz o travelling, as janelas e a fervura.
        // ══════════════════════════════════════════════════════════════════════
        const GA = "gancho", EU = "eua";
        const VOCE = Object.assign({}, TIPO.jovem, { roupa: C.azul, calca: C.tinta, pele: PELE[2] });   // quem ouve o discurso
        const BILI = Object.assign({}, TIPO.empresario, { roupa: "#1f2a44", gravata: C.amar, pele: PELE[0] });   // o bilionário
        const [f1a, f1b] = TELAS[0];   // a tela cheia 1 (montar.py, lista TELAS)

        // ══════════════════════════════════════════════════════════════════════
        // CENA 0 · O GANCHO (0 até a tela cheia 1): o despertador às 5:00, o jovem que rala e o saco de dinheiro que foge;
        // a VERDADE é uma pizza que vira UM PEDACINHO
        // ══════════════════════════════════════════════════════════════════════
        const c0 = cena(0, 0, 0);
        const co0 = tg(c0, "co0", 250, 45, 580, "O DISCURSO DE SEMPRE", "tag tagt", 34);
        entra(co0, 0.1);                                        // o gancho nunca abre vazio
        personagem(c0, "vc0", 380, TOPO, 180, VOCE, { expr: "neutro", pose: [8, 8] });
        brotaP("#vc0", 0.15);
        const rl0 = obj(c0, "rl0", 90, 170, 170, 170, relogio(170), true, false);
        aparece(rl0, T("acordar", GA) - 0.2, 0.3, { scale: 0.3, y: 30 });
        chacoalha(rl0, T("5", GA) - 0.1, 10);
        const h50 = tg(c0, "h50", 80, 370, 200, "5:00", "tag tagv", 46);
        entra(h50, T("5", GA) - 0.1);
        expressao("vc0", "surpreso", T("acordar", GA));
        pulinho("#vc0", T("acordar", GA) + 0.1, 40);
        const td0 = tg(c0, "td0", 620, 130, 360, "TRABALHA DURO", "tag", 32);
        entra(td0, T("trabalhar", GA) - 0.15);
        suorP("vc0", T("trabalhar", GA));
        gesto("vc0", "d", 120, T("trabalhar", GA), 0.2);
        gesto("vc0", "d", 30, T("duro", GA) + 0.3, 0.25);
        sai(td0, T("conseguir", GA) - 0.25);                    // a etiqueta velha sai antes do balão
        const sc0 = obj(c0, "sc0", 680, 300, 170, 200, sacoN(170, 200, "R$"), true, false);
        aparece(sc0, T("conseguir", GA) - 0.2, 0.3, { scale: 0.3, y: 40 });
        fala("vc0", "VOU FICAR RICO!", T("conseguir", GA), 1.2, { lado: 1 });
        expressao("vc0", "feliz", T("conseguir", GA));
        tl.to(sc0, { x: 150, rotation: 12, duration: 0.6, ease: "power2.in" }, T("enriquecer", GA) + 0.2);   // o saco foge
        tl.to(sc0, { autoAlpha: 0, duration: 0.2 }, T("enriquecer", GA) + 0.65);
        expressao("vc0", "preocupado", T("enriquecer", GA) + 0.4);
        // "Isso é uma meia verdade, nem meia, é um pedacinho de verdade"
        sai(["#co0", "#rl0", "#h50"], T("Isso", GA) - 0.2);
        andaP("vc0", T("Isso", GA) - 0.2, 0.6, -250);
        const pz0 = obj(c0, "pz0", 540, 170, 320, 320, pizzaN(320, "VERDADE"), true, false);
        aparece(pz0, T("Isso", GA), 0.3, { scale: 0.3, y: 40, rotation: -40 });
        const mv0 = selo(c0, "mv0", 420, 60, 560, "MEIA VERDADE", 46);   // o rotulo alarga o selo 220 px de cada lado
        carimba(mv0, T("meia", GA) - 0.05, -4, 1);
        xis(c0, "xm0", 640, 50, T("nem", GA), 100).style.zIndex = 6;   // o selo tem z 5: o ✗ por cima dele precisa de 6
        const ft0 = obj(c0, "ft0", 620, 250, 170, 170, fatiaN(170), true, false);
        tl.set(pz0, { autoAlpha: 0 }, T("pedacinho", GA) - 0.05);
        aparece(ft0, T("pedacinho", GA) - 0.05, 0.25, { scale: 1.6, y: 0 });
        const up0 = tg(c0, "up0", 470, 450, 460, "UM PEDACINHO", "tag tagv", 38);
        entra(up0, T("pedacinho", GA) + 0.1);
        expressao("vc0", "ironico", T("pedacinho", GA) + 0.2);

        // ══════════════════════════════════════════════════════════════════════
        // TELA CHEIA 1 (TELAS[0]): DE ONDE VEM A FORTUNA? Quatro cartões, cada um na palavra dele: NASCIMENTO (a coroa),
        // CRIME (o saco), TRABALHO (o trabalhador suando) e DE TODO TIPO (?). Coordenada = tela; a fileira de baixo vai até
        // x 920 por causa dos botões, e nada fica na faixa da legenda (880–990)
        // ══════════════════════════════════════════════════════════════════════
        const k1 = telaCheia(1);
        const tt1 = tg(k1, "tt1", 140, 175, 800, "DE ONDE VEM A FORTUNA?", "tag tagt", 44);
        entra(tt1, f1a - 0.3);
        [["A", 70, 290, "NASCIMENTO", "nascimento", "tagt"], ["B", 510, 290, "CRIME", "crimes", "tagv"],
         ["C", 70, 1030, "TRABALHO", "trabalho", "tagg"], ["D", 510, 1030, "DE TODO TIPO", "todo", "taga"]].forEach(([k, x, y, nome, w, cls], i) => {
          const t = T(w, GA) - 0.3;
          const cd = obj(k1, "cd1" + k, x, y, 410, 500, cartaoP(410, 500, 70 + i * 13), true, false);
          aparece(cd, t, 0.3, { scale: 0.4, y: 60, rotation: i % 2 ? 6 : -6 });
          entra(tg(k1, "nm1" + k, x + 25, y + 405, 360, nome, "tag " + cls, Math.min(40, caber(nome, 300, 40))), t + 0.15);
        });
        const cr1 = obj(k1, "cr1", 175, 420, 200, 130, coroaN(200, 130), false, false);
        aparece(cr1, T("nascimento", GA), 0.3, { scale: 0.2, y: -60, rotation: -20 });
        brilhos(k1, "bc1", 275, 480, 150, T("nascimento", GA) + 0.2, f1b + 0.4, 5);
        const sa1 = obj(k1, "sa1", 625, 360, 180, 220, sacoN(180, 220, "R$"), false, false);
        aparece(sa1, T("crimes", GA) - 0.1, 0.3, { scale: 0.3, y: 30 });
        chacoalha(sa1, T("crimes", GA) + 0.3, 8);
        personagem(k1, "tr1", 200, pe(1400, 150), 150, TIPO.trabalhador, { expr: "feliz", pose: [8, 8] });
        brotaP("#tr1", T("trabalho", GA) - 0.2);
        suorP("tr1", T("realmente", GA));
        pergunta(k1, "pq1", 615, 1130, T("todo", GA) - 0.3, 200);

        // ══════════════════════════════════════════════════════════════════════
        // CENA 1 · BRASIL × MUNDO (bloco eua): o globo e as bandeiras; nos EUA a barra cresce até 71%, CONSTRUÍRAM A FORTUNA,
        // e as cédulas voam para o BILIONÁRIO (o personagem é quem a fala cita: os bilionários)
        // ══════════════════════════════════════════════════════════════════════
        const c1 = cena(1, 1300, 0);
        const bm1 = tg(c1, "bm1", 270, 45, 540, "BRASIL × MUNDO", "tag tagt", 40);
        entra(bm1, T("Brasil", EU) - 0.15);
        const gl1 = obj(c1, "gl1", 90, 150, 200, 200, globoN(200), true, false);   // gira o miolo: sem fervura (false)
        aparece(gl1, T("comparação", EU) - 0.2, 0.3, { scale: 0.3, y: 30, rotation: -30 });
        tl.fromTo(gl1.firstChild, { rotation: 0 }, { rotation: 360, duration: 8, ease: "none", immediateRender: false }, T("comparação", EU));
        const bb1 = obj(c1, "bb1", 100, 400, 170, 115, bandeiraBR(170, 115), true, false);
        aparece(bb1, T("Brasil", EU), 0.3, { scale: 0.3, y: 30 });
        const bu1 = obj(c1, "bu1", 330, 140, 160, 104, bandeiraEUA(160, 104), true, false);
        aparece(bu1, T("Estados", EU) - 0.2, 0.3, { scale: 0.3, y: 30 });
        entra(tg(c1, "eu1", 500, 155, 160, "EUA", "tag", 40), T("Estados", EU));
        const ba1 = obj(c1, "ba1", 330, 280, 360, 76, barraN(360, 76, C.azul, 11), true, false);
        ba1.style.transformOrigin = "0% 50%";
        cresce(ba1, T("71%", EU) - 0.15, "scaleX", 0.6);
        entra(tg(c1, "p71", 700, 286, 150, "71%", "tag taga", 44), T("71%", EU) + 0.3);
        entra(tg(c1, "cf1", 330, 400, 560, "CONSTRUÍRAM A FORTUNA", "tag tagg", 34), T("construíram", EU) - 0.2);
        personagem(c1, "bi1", 820, pe(593, 150), 150, BILI, { expr: "neutro", pose: [8, 8] });
        brotaP("#bi1", T("bilionários", EU) - 0.3);
        nomeP(c1, "bi1t", 820, T("bilionários", EU) - 0.1, "BILIONÁRIO", "tagt", 150, pe(593, 150), 240);
        cedulasVoam(c1, "cv1", 410, 190, 860, 380, T("construíram", EU), 5);
        expressao("bi1", "feliz", T("construíram", EU) + 0.4);
        gesto("bi1", "e", 70, T("construíram", EU) + 0.3, 0.25);

        // ═════════════════════════════════════════════════════════════════════
        // CÂMERA (a última chamada): a cena 1 entra atrás da tela cheia, para estar lá quando a folha descer
        // ═════════════════════════════════════════════════════════════════════
        camera([[1, f1b - 0.3]]);
