# Animação no HyperFrames: a metade de cima

Ler antes da Etapa 3. A animação é o produto do canal: o público ama os personagens e as edições. Cada regra abaixo traz
o porquê (a lição e o corte de onde veio). O projeto para começar está em `assets/modelo/` (ver o `LEIA-ME.md` dele); o
exemplo de cenas é o `_cenas_exemplo.js`, e o corte mais limpo de referência foi o C84.

## 1. O layout 50/50 e a janela do Raul

- **Manter sempre metade/metade:** animação de 0 a 960 px e Raul de 960 a 1920, num quadro de 1080×1920. Por quê: o
  dono do canal voltou ao 50/50 em 03/10 (de 01 a 02/10 o Raul ocupava 60%) e, em 13/10, vetou outro formato ("vi um de
  círculo, não quero assim"): nada de janela redonda, bastidor ou Raul pequeno. A única exceção é a TELA CHEIA (seção 6).
- **A folha de cima termina numa borda de papel rasgado** em ~960 (o `clip-path` do `#topo`), com a fibra clara e a
  sombra por baixo. A legenda fica centrada na divisória (`#leg`, top 890). O `montar.py` faz essas contas.
- **Deixar a janela do Raul sem zoom:** o `montar.py` tira o 1,00/1,08 por bloco do motor. Por quê: no C72 (14/10) o
  zoom colou no rosto e cortou a cabeça ("tá ficando colado no rosto dele"). O enquadramento vem pronto da Etapa 2:
  cabeça inteira, rosto sempre do mesmo tamanho. Na tela dividida da fonte, o painel do Raul preenche a janela (C82).
- **Nunca deixar o Raul parado com a fala andando.** Por quê: o `PARADO` de 2,2 s do C44 foi ao ar e pareceu vídeo
  travado. Quando a fonte tira o Raul da tela (foto, manchete, gráfico), cobrir o trecho com uma tela cheia (C84).

## 2. O mundo de papel recortado

A folha de cima é um mundo de papel recortado sobre uma mesa. Cada ideia vira um objeto de papel, com camada, sombra
dura, contorno claro de recorte e duas tintas, como uma risografia. Por quê: dinheiro do dia a dia é concreto, e o papel
o torna tátil. É o oposto da cara padrão de IA (fundo preto, linha fina e texto).

- **Vetado (13/10):** estilo jornal, degradê, glow/neon, emoji, ícone vetorial perfeito, vidro fosco, Inter/Roboto/
  Poppins, sombra suave borrada, interface de app genérica, infográfico corporativo. Vale material feito à mão, traço
  irregular, sombra dura e movimento fluido.
- **Cores (o objeto `C` do motor):** papel `#efe6d3`, claro `#f8f2e4`, kraft `#d6c3a0`/`#bfa77d`, tinta `#1e1b2e`,
  vermelho `#e5432d` (o que cai, alerta, número), azul `#2c56a0`, amarelo `#e9b23a`, rosa `#f2a7a0`; verde `VERDE`
  `#3c9a4f` (no `_desenhos.js`). Pele: `PELE[0]` a `PELE[3]`.
- **Fontes:** Archivo Black (etiqueta, carimbo, número grande) e IBM Plex Mono (rótulo miúdo). O HyperFrames as embute.
- **Texto dentro de desenho:** calcular a fonte com `caber(txt, w, max)` (~0,78 em por letra), nunca tamanho chutado.
  Por quê: no C18 o texto passava da caixa e ficava grande demais.
- **Desenho de várias partes num SVG só**, com coordenadas que fecham; peças separadas só quando se mexem, e com a mesma
  origem. Por quê: o telhado da casinha saiu fora do lugar (C18).
- **A mão é sempre a `maoBoa(w, h, pose)`** (aberta, pega, punho, aponta, caneta): entra do canto, faz uma ação clara e
  sai. Por quê: "a mão tá horrível… nem sabia que era uma mão" (C44); a mão solta parecia uma bota (C27). Onomatopeia
  ("PÁ!") ajuda a ler a ação.
- **Computador é `computadorN`, conta é `calculadoraN`.** A `maquina` do `_ajudantes.js` parece máquina de lavar (C39).
- **Uma ideia nova de elemento a cada vídeo**, sem copiar a cena do anterior (C18). Os bancos: `personagens.js`,
  `elementos.js` (nomes com N), `_ajudantes.js`, `_desenhos.js` e `_cab48.js`. Desenho novo que serve a outros cortes
  vai para o banco da skill, não só para a cópia do corte.
- **Mais movimento que etiqueta:** número que conta (`quadros(...)`, quadros trocados por `tl.set`, seguro no render),
  traço que se desenha (`desenha(sel, t, dur, comp)`, pelo `stroke-dashoffset`), o que se revela (`revela(el, t, dur)`),
  objeto que reage à fala. Cada cena tem uma ação física por fala (a porta de aço desce, a mala estoura: C72).

## 3. O motor

O `motor.html` é o index.html do C02. O `montar.py` corta as cenas dele (do marcador `// CENA 0` até
`// ── RAUL: enquadramento`) e põe no lugar: o cabeçalho com a `const TELAS`, `_ajudantes.js`, `personagens.js`,
`elementos.js`, `_desenhos.js`, `_cab48.js`, `_base.js`, as cenas do corte e `_vida.js`. A legenda do motor dá lugar
à `legenda.js`. Não editar o `motor.html`: o `montar.py` procura trechos exatos dele e para se não achar.

O que o `montar.py` muda no motor, e por quê:
- **50/50:** janela do Raul em 960, folha até 990, `VY = 555` (03/10).
- **Câmera inicial nas cenas:** sai o `tl.set(mundo, camAtual, 0)` do motor, que ganhava no quadro 0 (C27).
- **`W()` só dentro do bloco:** a busca para na 1ª palavra de outro bloco (C40).
- **Chão fixo:** `cena(i)` ignora x e y e põe a cena em `x = i * 1300, y = 0`; `vai()` vira o travelling (12/10).
- **Raul sem zoom** (14/10), **a folha da tela cheia** (16/10), **o pouso com amassado e balanço** do `aparece()` e a
  **poeira de papel** do `carimba()` (C72), e **uma faixa só de efeitos** (`assets/sfx_mix.wav`, 14/10).
- **`node --check`** do script montado, porque nome repetido mata o script inteiro e o `hyperframes check` diz
  "0 errors" (C39: `const cai` já existia no motor; C59: `ST` também).

**Não redeclarar nomes do motor nem dos bancos:** `cai`, `ST`, `cam`, `cena`, `obj`, `pessoa`, `moeda`, `documento`,
`cartao`, `chama`, `casinha`, `congresso`, `B`, `T`, `W`, `D`, `C`, `DUR`. O `_base.js` do modelo também já declara `pe`,
`cresce`, `cartaoP`, `raulF`, `flutua`, `pulinho`, `nega`, `olha`, `aceno`, `suorP`, `brilhos`, `cedulasVoam`, `curte`,
`estrelaN`, `vistoA`, `telaCheia`, `camera`, `JAN`, `CHEIAS` e `raiz`: cena copiada de corte antigo que declara algum deles
(o C87 declarava `cresce` e `JAN`) quebra. O `montar.py` acusa no `node --check`; apagar a declaração e usar a do `_base.js`.

**Câmera e cenas:**
- A câmera fica sempre em zoom 1 e na mesma altura. Com ela em 1,0, o ponto (x, y) de uma cena cai na tela em
  (x, y + 155). Zoom dentro da cena desalinha o palco (12/10).
- As cenas ficam lado a lado, a cada 1300 px, na ordem em que aparecem. Trocar a ordem dos blocos é trocar o índice da
  `cena(i)` e as paradas do `camera()` (C68).
- `vai(i, 540, t)` é um travelling lateral de 0,82 s (`power2.inOut`) que começa 0,32 s antes de t. Por quê: o recuo
  antigo pela mesa mostrava cada chão solto, em alturas diferentes ("cada cena foi criada individualmente", 12/10).
- **O chão é um palco só** (`#piso` do `_cab48.js`): tampo claro de 560 a 650, pé dos bonecos em ~593, borda de tinta e
  frente em kraft, só com traço horizontal, para ficar parado na troca. O `chao()` das cenas não desenha nada.
- **Cada cena é cortada abaixo do palco** (`.cena { clip-path: inset(-700px -700px 150px -700px) }`): nada aparece
  abaixo de y 650. O que sobe nasce do chão. Por quê: no C44 uma loja que entrava subindo passou por cima da legenda.
- **`camera([[1, t1], [2, t2], ...])` é a última chamada das cenas** (`_base.js`): põe a câmera na cena 0 em 0, faz os
  travellings, calcula as janelas `JAN` de cada cena (sem os trechos cobertos pelas telas cheias) e liga a fervura.
  Sem ele a câmera fica fora do lugar e nada ferve; o `montar.py` para se não o achar.
- **Objeto que sai andando** vai para longe (+1000) e leva `tl.set(el, { autoAlpha: 0 }, t)` logo depois. Por quê: o
  mundo é um só, e ele aparecia na borda da cena vizinha (C27, C41).
- **Objeto de ação** (a tesoura que corta, a moeda que voa, a mão que bate) faz a ação INTEIRA e some logo depois, com
  `tl.to(el, { autoAlpha: 0, duration: 0.15 }, fim)`. No C87 a tesoura ficava parada na cena depois do corte; no C86 a mão
  do tapa parava antes do rosto: o contato tem de acontecer.
- A aba de capítulo (`capitulo(num, titulo, t0, t1)`, no HUD a partir de y 150) ainda existe; `TOTAL` fica no
  `_ajudantes.js`.

## 4. A API das cenas

Todo tempo vem de `T(palavra, bloco, n)`; `B[bloco]` é o início do bloco e `DUR` a duração. Ids únicos no vídeo inteiro.

**Peças:**
- `obj(pai, id, x, y, w, h, svgInterno, sombra = true, ferver = true)`: a peça de papel. `pai` é a cena (`c0`) ou a
  folha da tela cheia. Com `ferver = true` ela entra na fervura da cena atual. Peça cujo miolo você gira
  (`el.firstChild`) vai com `ferver = false`, porque a fervura também gira o miolo (o globo do exemplo).
  ```js
  const sc0 = obj(c0, "sc0", 680, 300, 170, 200, sacoN(170, 200, "R$"), true, false);
  ```
- `tg(c, id, x, y, w, txt, cls, fs)`: etiqueta de papel rasgado com fita. Classes: `tag` (clara), `tag tagt` (tinta),
  `tag tagv` (vermelha), `tag taga` (azul), `tag tagg` (verde), `tag tagc` (cinza). A cor é o `::before` do span:
  `background` no span não aparece (C38). A letra mínima é 28 px (o CSS ignora o `fs` menor): o `caber()` abaixo disso
  não vale (C48). O texto é centrado em `w`; se passar de `w`, ele vaza para a direita a partir de x (C27).
- `selo(c, id, x, y, w, txt, fs, cls = "selo")` + `carimba(el, t, rot, big = 1)`: o carimbo de borda dupla com
  estrelas (`"selo seloa"` = azul). Ele bate no papel em t + 0,06, treme a folha e solta papel picado. O selo tem
  z-index 5: o que vai por cima dele (o ✗) precisa de 6. Carimbo só nos SOCOS do raciocínio (o C84 teve 5 e o C87, 6;
  carimbo em toda frase vira ruído), e nunca dois lado a lado: "NÃO SÃO" + "O PROBLEMA" virou frase (C09). **O carimbo
  final pousa a 1 s ou mais do fim do vídeo**, para dar tempo de ler (no C87 ele saía a 0,4 s do fim e foi para o 2º
  "construiu", a 1,5 s do fim).
  ```js
  const mv0 = selo(c0, "mv0", 420, 60, 560, "MEIA VERDADE", 46);
  carimba(mv0, T("meia", GA) - 0.05, -4, 1);
  ```
- `entra(el, t)` / `sai(els, t)`: a etiqueta que pousa em 0,22 s / o que cai e some. A etiqueta velha sai quando a nova
  entra (C18).
- `aparece(el, t, dur = 0.42, de = { scale: 0.4, y: 40 })`: esconde a peça desde o 0 (`tl.set` em 0), a faz pousar em t
  e a deixa em x 0, y 0, escala 1 e rotação 0, com o amassado e o balanço do pouso. O que ele NÃO reseta: a cara e os
  braços do personagem (`expressao`/`gesto` continuam como estavam), o miolo `.b` (fervura, `flutua`), o `scaleX`/
  `scaleY` de um `pulinho`, e o que um `tl.to` posterior fizer. E, como esconde desde o 0, chamá-lo numa peça já visível
  antes a apaga para trás.
- `cresce(el, t, eixo = "scaleY", dur = 0.4)`: barra, pódio, pilha. Antes, o pé: `el.style.transformOrigin = "0% 50%"`
  (barra) ou `"50% 100%"` (pódio).
- `brotaP(el, t)`: nasce do chão (sobe 420 px), o jeito de pôr personagem e prédio no palco.
- `xis(c, id, x, y, t, s)`, `pergunta(c, id, x, y, t, s)`, `vistoA(c, id, x, y, t, s)`: ✗, ? e ✓ de pincel.
- `pulsa(el, t, s)`, `chacoalha(el, t, amp)`, `flutua(el, t0)`: o soquinho do número, o tremor no lugar, o flutuar.
- `brilhos(c, id, cx, cy, raio, t0, t1, n)`, `cedulasVoam(c, id, x0, y0, x1, y1, t, n)`, `curte(c, id, x, y, t)`: o que
  brilha, o dinheiro que vai de um a outro, as curtidas que sobem.
- Outros do `_cab48.js`: `miudo` (texto pequeno), `balaoT`/`pensaT` (balão parado), `voa` (moeda em arco), `maoP`
  (onde fica a mão do boneco), `figura` (personagem + etiqueta). O `entregador()` usa boné: conta como o boné do vídeo.

**Personagens** (`personagens.js`):
- `personagem(pai, id, x, y, w, TIPO.x, { expr, pose: [8, 8] })`: boneco de 200×400 escalado para `w`, com braços que
  giram no ombro. Tipos: `ministro`, `politico`, `empresario`, `trabalhador` (capacete), `aposentado`, `cidada`, `jovem`
  e `raul`. Variar com `Object.assign({}, TIPO.empresario, { roupa: "#1f2a44", pele: PELE[0] })`. Todo boneco ganha
  sozinho a vida das vertentes (`vidaP`: piscar, olhar e respiração, 14/10).
- `expressao(id, cara, t)`: neutro, feliz, bravo, surpreso, preocupado, rindo, ironico, com pulinho de reação.
- `gesto(id, "d"|"e", ang, t, dur)`: o braço sobe `ang` graus a partir do pendurado (positivo = para fora). Braço erguido
  alcança ~118·w/200 px além do ombro: conferir perto da borda.
- `fala(id, "TEXTO!", t, dur, { lado: 1|-1, cor, tinta, fs })`: o balão sai da boca e a boca mexe ("\n" quebra a linha).
- `risada(id, t, dur)`: cara de riso, pulinhos e "HA HA". `andaP(id, t, dur, dx)`: anda em passos de papel, contínuo.
- `tira(id, "toga", t)`: tira uma peça. `nega`, `olha`, `aceno`, `pulinho`, `suorP` (o `_base.js`): a atuação do C72.
- `nomeP(c, id, x, t, txt, cls, w, y, lw)`: o nome numa etiqueta embaixo do pé (no tampo, rente ao corte em 650). Ele
  afasta o centro da borda (C48) e, desde 17/10, segura a etiqueta entre x 40 e 1040 (antes o limite era 1072). Na tela
  cheia, perto dos botões (y 900–1700), ponha o boneco mais para dentro: a etiqueta não pode passar de x 920.
- `raulF(c, id, x, y, t, expr, w)`: o personagem do Raul, que nasce do chão.
  ```js
  personagem(c1, "bi1", 820, pe(593, 150), 150, BILI, { expr: "neutro", pose: [8, 8] });
  brotaP("#bi1", T("bilionários", EU) - 0.3);
  nomeP(c1, "bi1t", 820, T("bilionários", EU) - 0.1, "BILIONÁRIO", "tagt", 150, pe(593, 150), 240);
  fala("vc0", "VOU FICAR RICO!", T("conseguir", GA), 1.2, { lado: 1 });
  ```
- **`pe()`, `pesY()` e `TOPO`:** `TOPO = 240` é o y do boneco de 180 com o pé no tampo (~593). `pesY(y, w)` diz onde
  fica o pé; `pe(yChao, w)` dá o y para o pé cair em `yChao`. Na cena, outra largura vai com `pe(593, w)`; na tela
  cheia, `pe(1600, w)` a `pe(1620, w)`.

**`T(palavra, bloco, n)`: a n-ésima vez que a palavra é DITA dentro do bloco.** A comparação é normalizada: caixa baixa,
sem pontuação, só letras (com acento), números, `%` e vírgula. Armadilhas, todas já foram ao ar:
- **O n conta dentro do bloco.** Palavra comum (que, e, com, vai, cara, só, não, gente, se) pede o n contado no
  `tempos.json`. No C48 havia três "só" no bloco e o n 2 fez os celulares entrarem 16 s antes; no C68, "Vou" era n 4.
- **A normalização acha a palavra dentro de outra frase:** o "Aí" pegou o "E aí" do começo do bloco (C39).
- **Bloco longo repete palavra curta:** o "Nem" pegou o "nem pra poder" de 8 s antes, o `sai()` caiu antes do `entra()`
  e a etiqueta ficou para sempre (C41). Conferir cada âncora curta contra o bloco inteiro.
- **Palavra que não está no bloco quebra tudo:** o `T()` lança erro, o script para e o vídeo sai sem animação e sem
  legenda, com o `hyperframes check` dizendo "0 errors" (C40, C47, em que o gancho partido em dois tirou o "Temer" do
  bloco antigo). Mudou um bloco? Revisar as âncoras dele.
- **Palavra devolvida a outro bloco** tem de ficar com o tempo dentro dele (C40).
- **Número como está no `tempos.json`:** "5", "71%", "162,9". "5:00" vira "500".
- **Deixa de câmera vai em palavra rara.** A mesma âncora serve à cena, ao `som.json` (`gera_som.py`) e à lista `TELAS`
  do `montar.py`: as três leem as mesmas palavras.

## 5. Cena a cena com interação

Padrão desde 10/10 (C46, C48). A animação contínua (a estrada do C45) foi descartada: era difícil diferenciar um vídeo
do outro e a história ficava confusa ("cena a cena tá combinando mais… e deixa uma liberdade criativa maior"). O que
faltava na cena a cena era vida dentro da cena.

- **Dar vida dentro da cena:** personagem que fala com personagem (`fala`, o balão que sai da boca), ri do outro
  (`risada`), anda (`andaP`), pega, aponta ou empurra um objeto (`gesto` + o objeto que anda junto), e texto que sai do
  personagem. Cada fala ganha um objeto que a ilustra, não só a etiqueta.
- **Todo personagem tem papel na história.** Por quê: o boneco genérico (o BRASIL todo de branco, o ANDANTE de jaqueta e
  mochila) foi reprovado duas vezes em 10/10: "ele só por ele mesmo não representa nada". No roteiro da animação,
  escrever quem ele é, o que significa e o que muda nele. As reações também têm sentido (um "!", um "?"). Se nada tem
  papel, a cena fica sem personagem.
- **Pessoa citada ou subentendida aparece ilustrada**, como TIPO com o nome na etiqueta (`nomeP`). Vale para "ele",
  "o presidente", "o cara". Se a fala só nomeia depois, a pessoa entra antes, na 1ª alusão. Por quê: a imagem traz a
  imersão e tira a sensação de desconhecimento (10/10). Grupo citado (os bilionários) vira um TIPO com a etiqueta do grupo.
- **Pessoa real nunca ganha rosto:** só o TIPO com etiqueta. Os dois lados de uma disputa com o mesmo tom de pele (C38).
  Caricatura parecida só quando o dono do canal pedir, caso a caso, com a imagem que a própria fonte mostra (C37: o
  `nikolasN` do `_desenhos.js`, corpo e caras trocadas por `tl.set`, sem fervura); avisar do risco de denúncia.
- **O Raul personagem (`TIPO.raul`, `raulF`) só quando a fala reage à cena:** indignação, ironia, "que loucura". No C44
  ele entrou cinco vezes: a mão na cara, apontando, com a lupa, de braços para cima e a ironia que vira bronca. Camisa
  preta de manga curta (12/10); `frente: "d"` põe o braço na frente do rosto. Não fica o tempo todo.
- **No máximo um boné por vídeo**, num cidadão comum, quando ajuda a história. Por quê: no C67 eram três e virou
  cacoete (12/10). O `TIPO.jovem` tem cabelo curto; apresentador que usa boné na vida real aparece sem; conferir o
  cabelo ao copiar personagem de corte antigo.
- **Não afirmar além da fala:** fonte no condicional pede etiqueta no condicional (C58: TERIA PAGO, SUPOSTO). Figura
  genérica de instituição (O ESTADO, O BANQUEIRO) sem partido (C74). Etiqueta e carimbo nunca com palavrão por extenso.
- **Detalhe errado na fala (data, prazo, valor) que não sai sem quebrar o raciocínio: a animação mostra o dado certo,
  sem desmentir o Raul.** No C87 ele ligou o fim do réis ao fim do império e pôs o confisco "30 anos atrás"; a tela cheia
  mostrou 1822 → 1942, MARÇO DE 1990, BLOQUEADO POR 18 MESES e DEVOLVIDO EM 12 PARCELAS. Fato errado que é a própria tese
  continua saindo do roteiro (C51).
- **Trecho sensível** (violência, morte, doença): a animação só sugere, sem mostrar a cena e sem gag (C86: a violência
  doméstica da fala ficou só sugerida). No som, só caneta baixa.
- **O gancho nunca abre vazio, e nenhuma cena também:** o 1º elemento de cada cena entra com a 1ª palavra do bloco. Por
  quê: no C44 o trabalhador só entrava no "trabalhador" e o bloco abriu com 1,5 s de papel em branco. Nenhum trecho de
  folha vazia passa de ~2 s (C18). **Personagem com lugar reservado na cena entra na 1ª menção dele ou na 1ª palavra do
  bloco**, nunca numa palavra tardia: até ele brotar, o espaço fica vazio e a cena parece incompleta (C87: o avô passou a
  entrar no 1º "versão", e não no "velhos").
- **No gancho, a cena pode trazer palavras-chave** (a placa, o balão, o carimbo), mas só como complemento: a legenda fica
  do começo ao fim. Por quê: no C49 a faixa sumiu e a fala virou texto espalhado, que não se lia em ordem (11/10).
- **Etiqueta com até 4 palavras**, para ler no celular.

## 6. A TELA CHEIA

Padrão desde 16/10: a animação toma a tela inteira, por cima do Raul, e a voz segue.
- **3 vezes ou mais em vídeo de até 2 min; 4 acima de 2 min; cada uma com 5 s ou mais.** A 1ª vem logo depois do gancho;
  as outras se espalham, sem colar uma na outra e sem cair no fim. Por quê: o teste de 15/10 (uma logo após o gancho e
  outra no meio) agradou, e no C82 o dono pediu mais: "pelo menos três vezes, de pelo menos cinco segundos cada… quatro
  vezes, já que tem mais de 2 minutos". O C82 teve 4 (0:15, 1:00, 1:59, 2:41); o C84, 4; o C83, 3.
- **O roteiro já nasce com elas:** cada tela cheia cai numa fala visual (exemplo concreto, número, lista, cena), nunca
  num trecho que depende do rosto do Raul. Marcar início, fim e o que aparece no roteiro da animação.
- **Usar a tela cheia para cobrir o trecho em que a fonte tira o Raul da tela.** No C84, a foto da Saveiro e a do
  Saverin ficaram debaixo da 3ª.
- **Como fazer:** a lista `TELAS` do `montar.py` tem o início e o fim de cada uma, com as mesmas âncoras das cenas:
  ```python
  TELAS = [(("gente", "gancho", 2, -0.05), ("tipo", "gancho", 1, 0.3)), ...]   # (palavra, bloco, n, desloc)
  ```
  O `montar.py` calcula os tempos, escreve a `const TELAS = [[t0, t1], ...]` no começo das cenas, avisa quando a regra
  não fecha (quantidade, duração, a 1ª depois de 20 s, coladas, no fim) e grava `assets/tela_cheia.json` com
  `[t0 − 0,5, t1 + 0,47]`. O `finalizar.py` lê esse arquivo e não acusa "Raul parado" ali (a folha cobre o Raul de
  propósito).
- **Nas cenas:** `const k1 = telaCheia(1);` devolve a folha de dentro. A assinatura é `telaCheia(n, t0, t1)`, com t0 e
  t1 vindos de `TELAS[n − 1]`: não passe outros tempos, senão o `tela_cheia.json` e o som não batem. Coordenada = tela. Ela sobe por baixo a partir de
  t0 − 0,5 (0,52 s, girando 1,4° → 0), desce em t1 (0,46 s) e some; a legenda fica por cima (z 25 > 20) e a marca do
  canal some enquanto ela está na tela. O que é criado depois do `telaCheia(n)` ferve no grupo `cenaAtual` 49 + n (50,
  51…) até o próximo `cena()`; para voltar a pôr peça numa cena, `cenaAtual = i`.
- **Nenhum carimbo ou soco no meio segundo em que a folha sobe** (de t0 − 0,5 a t0): ela cobre a folha de cima nesse
  tempo. Dar folga para o carimbo do gancho pousar e ser lido antes de t0 − 0,5; se não couber, empurrar o t0 (no C87 o
  "CORTOU O ZERO" sumia debaixo da subida, e a tela 1 passou a subir 0,3 s depois do "Desde"). Fotografar o instante
  t0 − 0,5 de cada tela cheia.
- **Cada fala dita com a tela cheia em cima ganha uma peça entrando:** ela nunca fica segundos só com o título. No C87
  as telas 2 e 3 ficavam vazias, e entraram PLANO COLLOR, a multidão com o dinheiro indo para o cofre, NÃO FOI BEM
  ASSIM… e EU NÃO TAVA VIVO.
- **A faixa do título fica livre** (de y 175 até o pé da etiqueta): objeto empilhado em outro (o cadeado sobre o cofre,
  no C87) começa abaixo dela, contando a entrada com `scale` ou `y` negativo.
- **A câmera troca de cena atrás dela:** a parada vai em t1 − 0,3 (`camera([[1, f1b - 0.3]])`), para a cena nova já
  estar lá quando a folha descer.
- **O par de som:** subida = whoosh + página; descida = whoosh, discretos, por baixo da fala. O `gera_som.py` do modelo
  os põe sozinho a partir do `tela_cheia.json`.

## 7. A ÁREA DE SEGURANÇA

O TikTok cobre partes da tela: a busca e as abas em cima (~120 px), os botões à direita (x > ~930, de y ≈ 900 a 1700)
e o nome e o texto do post embaixo (de ~1740 para baixo). Por quê a regra é dura: em 17/10 o C80 e o C83 vazaram
("aquela nossa área de segurança... sumiu"): etiqueta embaixo da busca, carimbo e personagem saindo pela direita, perna e
quadro-negro embaixo dos botões e do texto do post na tela cheia. A regra de 03/10 tinha se perdido quando a tela cheia
entrou.

- **Folha de cima (coordenada da cena; tela = y + 155):** x de 40 a 1040, y de 45 a 800. Por que 45 e não 10: o zoom de
  3,5% da respiração (`_vida.js`) puxa o topo ~15 px para cima. Na prática o palco já corta tudo abaixo de 650.
- **Tela cheia (coordenada = tela):** y de 150 a 1700, x de 40 a 1040, e de y 900 a 1700 nada passa de x 920 (os
  botões). Pé de personagem em 1600–1620, nunca em 1740. A faixa da legenda (y ~880 a 990) fica livre.
- **A conta da largura:** etiqueta (`tag`): span ≈ letras × fs × 0,78 + 48, centrado em `w` se couber; senão vaza
  para a direita. Carimbo (`selo`): o `rotulo` alarga a caixa 220 px de cada lado (440 no total, por causa da máscara do
  grão), então a caixa não diz nada: o texto fica centrado em x + w/2 e o span mede ≈ (letras × 0,78 + 1,4) × fs + 84.
  Na dúvida, medir o span no navegador, com a linha do tempo no instante:
  ```js
  window.__timelines.main.seek(12); document.querySelector("#mv0 > span").getBoundingClientRect()
  ```
- **Peça larga de propósito** (a multidão, uma faixa de fundo): `el.dataset.fundo = ""` para o conferidor ignorar.
- **O conferidor:** `node scripts/zona_segura.mjs <pasta do corte>` anda na linha do tempo, mede o que cada peça desenha
  (as formas do SVG, o span da etiqueta), ignora o que está inteiro fora do quadro e os papeizinhos do carimbo (`pz…`) e
  só acusa o que fica fora 0,75 s ou mais. Precisa dar "✓ tudo dentro da área de segurança" antes de todo render; o
  `sonoplastia.py` também o roda no fim.

## 8. Movimento, grão, fervura, legenda e marca

- **Movimento fluido, sem degraus.** O `S()` do motor devolve a curva inteira, a 24 quadros; o `andaP` é contínuo.
  Nada de `Math.floor(q * n) / n` nas cenas, e trocas de bloco suaves. Por quê: "por mais que ela aconteça em blocos, as
  coisas têm que acontecer de uma maneira fluida… natural" (10/10). A versão antiga da linha do canal falava em stop-motion de 12 qps:
  vale o fluido (o comentário antigo do `motor.html` sobre degraus também). Usar os 12 princípios (antecipação, comprimir e esticar, arcos, entrar e sair devagar) e reação na
  palavra (13/10).
- **O grão do papel fica parado.** O motor não anima o `#grao`. Por quê: o grão que pulava a cada 2 quadros era ruído
  novo em todo quadro; no C45 o vídeo caiu de 250 MB para 72 MB parado, com a mesma qualidade, e no TikTok esse ruído
  roubava os bits do desenho e do texto (10/10). O vídeo final fica bem abaixo de 240 MB.
- **A fervura é só um tremor do papel:** cada peça com `ferver = true` gira 0,45–0,95° a 6 Hz, só enquanto a cena dela
  está na tela (a janela `JAN` ± 0,8 s, que o `camera()` calcula). Peça fora da janela não ferve: menos trabalho no
  render.
- **A vida do `_vida.js`:** as etiquetas das cenas balançam presas pela fita, cada uma no seu ritmo; a câmera aproxima
  3,5% devagar dentro de cada janela e volta antes do travelling (14/10, o nível das vertentes de gibi e caderno).
- **A legenda v3** (`legenda.js`; o texto vem pronto do `legendas.py`):
  - cartão branco (`#fffdf8`), borda de tinta de 4 px, cantos de 14 px, sombra dura deslocada (6 px, 7 px), girado só
    ±1° e parado. Por quê: "não quero ele serrilhado mais… bordas levemente arredondadas" (10/10);
  - letra até 58 px em 620 de largura, de 1 a 3 palavras, linha única. Por quê: a de 92 px e depois a de 72 chegavam nos
    botões e na foto de perfil do TikTok;
  - aparece direto no tamanho final, sem escala e sem fita: "mal dá pra ler" (06/10);
  - marca-texto amarelo na palavra dita e as próximas apagadas ("o ritmo está bom"); destaques (número, dinheiro,
    palavrão censurado) em vermelho com um soquinho de 1,05; a fala do apresentador num cartão escuro. Se vier
    reclamação de "fita amarela", a dúvida é o marca-texto: perguntar antes de tirar;
  - a faixa nunca some: nada de `tl.set("#leg", { autoAlpha: 0 })` (11/10). A 1ª legenda entra no 1º quadro (C68).
- **A marca do canal** (`scripts/marca.py`, chamado pelo `montar.py`): a foto de perfil redonda de 56 px e o @ do canal
  em Archivo Black 25 px, parados em left 30 e top 1076, com opacidade 0,8. Por quê: outros perfis repostam os cortes, e o
  nome vai junto (07/10). Fica longe do texto do post e dos botões; some na tela cheia; a capa não leva.

## 9. A capa

Um quadro do próprio vídeo, com o Raul olhando para a câmera de olhos abertos e o rosto livre (nenhuma mão na frente; no
C86 o quadro de 3,9 s tinha as mãos no rosto e a capa foi para o de 30 s), a folha de papel com uma cena da animação
e a manchete em etiquetas de papel (Archivo Black, palavra-chave na etiqueta vermelha). O modelo é o `capa/index.html`.

- **Manchete de 2 a 3 linhas, a mesma ideia do gancho**, de y 250 a ~600. Por quê: o rosto inteiro do Raul precisa
  caber no recorte 3:4 do centro (y 240 a 1680), que é o que a grade do perfil mostra; no C01 a manchete cobria a
  divisória e o Raul ficou escondido; no C48 o título desceu para baixo de y 250 para caber.
- **Sem selo de nome** ("RAUL SENA · INVESTIDOR SARDINHA" saiu em 01/10; o crédito vai na legenda do post) e sem a marca.
- **Capa não acusa:** "ROUBOU?" parado ao lado do rosto lê-se como acusação (C37).
- **A capa segue o estilo do vídeo** (13/10): no papel recortado, etiqueta branca e vermelha.
- **Montar:** `capa/assets/raul.jpg` é um quadro do `raul.mp4` (1080×960); `capa/assets/mundo.png` é um pedaço da
  animação, tirado com `snapshot --zoom x,y,600,317 --zoom-scale 1 --describe false` (coordenada da tela); papel e grão o `montar.py`
  copia. Depois, `npx --yes hyperframes@0.8.99 snapshot capa --at 0.5 --no-end --describe false -o _capa` e o PNG vira
  `renders/cNN_capa.jpg`. Conferir o recorte 3:4: o rosto do Raul inteiro e a manchete inteira dentro dele.

## 10. O fluxo da Etapa 3

1. **Esforço:** as etapas até a animação rodam com esforço médio. Antes de animar, parar e pedir o esforço extra. Por
   quê: a animação do C01 só chegou ao nível dela com muitas rodadas de conferência quadro a quadro (01/10). Com prazo
   curto ("faz completo"), avisar em uma linha e seguir (04/10).
2. **Observar o vídeo:** rodar `python $S/roteirista.py batidas .` (grava o `batidas.md`: cada frase com o tempo, os
   gatilhos já com a âncora `T("palavra", "bloco", n)` certa e as alusões sem nome, como "ele" e "o presidente", que
   pedem a pessoa ilustrada com etiqueta); quadros nos momentos-chave (os gestos e as expressões do Raul, para sincronizar), quem fala e o
   texto com o tempo de cada palavra.
3. **Escrever o roteiro da animação ANTES de animar** (`ROTEIRO_ANIMACAO.md`): o fio da história (personagem ou objeto que
   atravessa o vídeo), os personagens (quem é, o que significa, o que muda), cena por cena ("tempo · o que se ouve → o
   que se vê"), as telas cheias com início, fim e o que aparece, carimbo só nos socos e o final em loop. Por quê: "antes
   de animar vai acontecer o processo de criação de roteiro… essa parte do roteiro é muuuuito importante" (06/10, C27).
   Autocrítica com nota de 0 a 10, em rodadas, até 10/10:
   - gancho (ironia ou fato visível em 2 s);
   - leigo entende (todo termo técnico vira imagem e uma explicação curta);
   - retenção (novidade a cada 2 a 3 s, sem buraco nas falas longas);
   - fio da história;
   - viralização (uma imagem que vira print, e o loop);
   - sincronia com os gestos do vídeo;
   - segurança (sem rosto de pessoa real, sem afirmar além da fala, sem número errado);
   - leitura no celular (até 4 palavras por etiqueta).
   Quem aprova o roteiro da animação é a própria autocrítica: o dono do canal não quer avaliar roteiro ("vai ter que ser
   você fazendo várias avaliações até ficar perfeito"); ele aprova o vídeo animado.
4. **Copiar o modelo** e escrever o `_cenas.js` (a partir do `_cenas_exemplo.js`) e a lista `TELAS` do `montar.py`.
5. **`python montar.py`:** monta o `index.html`, avisa da regra da tela cheia e roda o `node --check`.
6. **Erro de JavaScript:** `node scripts/erros_js.mjs index.html` abre a página no Chrome sem tela e lê o `pageerror`.
   Por quê: um `T()` sem a palavra ou um nome repetido deixa o vídeo sem animação e sem legenda, e o `hyperframes check`
   não acusa (C06, C39, C40, C47).
7. **Fotos de todas as cenas, nos instantes de cada entrada,** antes do render
   (`npx --yes hyperframes@0.8.99 snapshot . --at t1,t2,... --no-end --describe false -o snapshots`). Olhar: texto fora
   da caixa, etiqueta cobrindo outra, desenho desalinhado, peça escondida atrás de outra (z-index), etiqueta velha que não
   saiu, folha vazia, boné demais, personagem sem papel. Por quê: os erros pequenos se repetiam (C18).
8. **Som:** `python gera_som.py && python scripts/sonoplastia.py .` (regras em `references/audio.md`). O efeito fica
   sempre por baixo da fala.
9. **Área de segurança:** `node scripts/zona_segura.mjs .` com "✓". Só então renderizar:
   `npx --yes hyperframes@0.8.99 render . --fps 24 -q standard -w 6 -o renders/etapa3_bruto.mp4`.
10. **Depois do render:** `sonoplastia.py --mux`, `finalizar.py` (−14 LUFS, Raul travado, prévia de 720p) e a folha de
    contato do vídeo pronto, um quadro a cada ~3 s (`references/conferencias.md`). Olhar: o Raul nunca parado e de cabeça
    inteira, a legenda do começo ao fim, as telas cheias nos lugares do roteiro, nada vazando da área de segurança, o
    tamanho abaixo de 240 MB.
11. **Mandar a prévia e a capa** e esperar o "pode agendar".
