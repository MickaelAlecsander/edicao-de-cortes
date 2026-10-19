# Conferências: o que se confere antes de cada aprovação e antes do render

Este é o checklist, na ordem em que as coisas acontecem. Cada item traz o comando e o que conta como aprovado. Item
reprovado volta para a etapa que o produziu: nada segue "para corrigir depois", porque o render leva minutos e a
correção depois dele custa o dobro.

`$S` = a pasta `scripts/` desta skill. Os comandos rodam de dentro da pasta do corte (`cortes/cNN-slug/`). Os argumentos
completos de cada script estão no `--help` dele.

| Momento | Blocos deste checklist | Sai daqui |
|---|---|---|
| antes de cortar | 1 | as janelas do `cortes.json` |
| depois do `cortar.py`, antes da ✋2 | 2, 3, 4 e 5 | a edição sem animação |
| antes do render da animação | 6, 7 e 8 | o `etapa3_bruto.mp4` |
| depois do render | 9 e 10 | o `etapa3.mp4` e a prévia |
| a entrega | 11 | a aprovação da prévia e o "pode agendar" |

## 1. Pontas: antes de cortar

- [ ] **Cada ponta pelo `pausas.py`, com o texto do roteiro.**
  ```bash
  python $S/pausas.py _fontes/<id>_opus.mkv --palavras _pesquisa/<id>_palavras.json <t>:<última>:<primeira> ...
  ```
  **Aprovado:** a janela do `cortes.json` é a `✓ janela sugerida`, a que cai num vale abaixo de −40 dB, entre a última
  palavra e a primeira do roteiro.
  - `✗ DENTRO de X`: o vale é o fechamento de uma consoante no meio da palavra ("ami|go", C67). Cortar ali come X.
  - `cortar antes`: o começo da palavra seguinte (f, s, x fracos, oclusão de p/t/k) já está no vale. A janela termina
    antes dele.
  - `??`: o alinhador não achou a palavra. Re-ouvir antes de confiar no rótulo.
  - `--perfil`: o envelope a cada 20 ms, para quando o alinhador se perde (no C84 três pontas saíram do perfil).
  - **Nunca escolher "o vale mais fundo".** No C29 ele caiu entre "te" e "pagar".
  - **Sem pausa limpa, a frase sai do roteiro**, e isso se conta ao dono do canal junto da prévia.
- [ ] **Medir as pontas no MESMO arquivo que o `cortar.py` corta** (o `<id>_opus.mkv`). No C20, medir num arquivo e cortar
  noutro jogou todas as pontas 35 ms dentro da palavra vizinha.
- [ ] **Preferir o trecho contínuo mais longo a colar pedacinhos.** A frase que emenda sem pausa ("salário | do que",
  C26) sai.

## 2. Fala: depois do `cortar.py`

- [ ] **As travas do `cortar.py` passaram.**
  ```bash
  python $S/cortar.py .
  ```
  **Aprovado:** nenhum bloco barrado, a linha `voz: X LUFS → -15.0 LUFS` impressa e o `travada.py` ✓ no `raul.mp4`. O
  corte para sozinho quando:
  - a ponta está acima de −40 dB;
  - depois do FIM vem voz curta, de menos de 220 ms, seguida de outro vale (`rabo()`): é a sílaba final da mesma palavra;
  - antes do INÍCIO há voz curta com um vale antes (`cabeca()`): é a primeira sílaba que ficou de fora (o "O" de "O meu
    conteúdo", C26).

  `"fala_ok": {"fim": "motivo"}` só entra com o motivo tirado do envelope de 5 ms, nunca do Whisper. Exemplos: a palavra
  seguinte curta ("Eu" + o "p" de "pego"), ou o corte da própria fonte, um vale de 20 a 30 ms (C30).
- [ ] **As pontas, uma a uma, no envelope.**
  ```bash
  python $S/conferir_fins.py .
  ```
  **Aprovado:** silêncio nos 20 ms de cada corte. A última e a primeira palavra ouvidas ISOLADAS são as esperadas, e todo
  ⚠ foi conferido no espectro.
  - **Vale curto antes de vogal é fechamento de consoante (t, p, k), não fim de palavra:** o "tribu|tárias" do C09 e o
    "cam|panha" de 03/10.
  - **O rabo nasal também é palavra:** depois do "bém" de "também" vinham 200 ms de murmúrio (C26). Em palavra emendada,
    cortar logo antes do ATAQUE da palavra seguinte, nunca no primeiro mínimo.
  - **Voz fraca entre duas palavras pode ser palavra:** o "Por" de "Por que" a −33/−45 dB foi tomado por estalo de boca
    (C48).
  - **O "s" final emendado no "s" seguinte é um som só:** cortar no meio dele, antes da vogal.
  - **Falsos alarmes conhecidos:** número falado ("9 mil reais" → "R$ 9.000") e o Whisper inventando conectivo no começo
    de trecho isolado ("Então", "Mas", "E"). Se há silêncio antes do corte, a palavra não está lá.
- [ ] **Mexeu numa ponta à mão? Rodar o `cortar.py` e o `conferir_fins.py` de novo** antes de mostrar. Por quê: em 03/10 o
  "campanha" saiu cortado entre as sílabas depois de um ajuste manual.

## 3. Emendas: no ouvido

- [ ] **Ouvir cada emenda da montagem.**
  ```bash
  python $S/ouvir_emendas.py .
  ```
  **Aprovado:** nenhuma emenda com palavra atravessando ou comida. Todo ⚠ foi conferido no envelope e, se era real, a ponta
  foi para a pausa e o corte foi refeito.
  - **Um ⚠ só se descarta com o envelope**, nunca porque "o vale é fundo". No C26, o "minuscu-" e o "al-" estavam em vales
    de −49 dB e eram o fechamento do "c" e do "t".
  - **O Whisper nunca é prova de palavra inteira.** Ele completa a palavra cortada pelo contexto: o "inves|tir" do C26
    passou assim.
  - **Ouvir numa janela que PASSA do corte (±1,5 s)**, não só o texto em contexto. No C25, a frase inteira escondeu o
    "cent…" de "centavos".
  - **Toda emenda de fala emendada se confere palavra a palavra, com tempo,** numa janela que passa da emenda. No C41
    sobraram o "-to" de "Exa|to" e o "Exa-" do apresentador.
- [ ] **Emenda seca é defeito.** Entre frases, menos de ~200 ms de silêncio soa colado ("Família | Cara" com 60 ms, C29).
  **Aprovado:** o início do bloco cai no começo ou no meio da pausa. Quando a pausa da fonte é curta, o bloco leva
  `"respiro"` de 0,083 a 0,15 s (C34; no C84, 0,15 s antes do "Herança"). Acima de 0,2 s, o quadro parado aparece.
- [ ] **Na dúvida, terminar um pouco depois.** O respiro curto não incomoda; a sílaba cortada, sim.

## 4. Legenda × o que foi falado

- [ ] **Gerar a legenda e ler bloco a bloco contra o `ROTEIRO.md`.**
  ```bash
  python $S/legendas.py .
  ```
  **Aprovado:**
  - toda palavra dita aparece, na ordem, sem palavra que não está no áudio;
  - o texto é o conferido no ouvido (o do roteiro, realinhado), e não o chute do Whisper;
  - número e unidade ficam juntos ("5 MILHÕES");
  - palavrão sai censurado (`F**A`, `P***A`, `F**A-SE`). A legenda animada e a do post nunca levam palavrão por extenso;
  - a 1ª legenda entra no 1º quadro;
  - a fala de outra pessoa sai no cartão escuro.

  Por quê: depois de empurrar uma ponta, o tempo da palavra seguinte pode entrar na etiqueta sem estar no áudio. E no C68
  a 1ª palavra marcada em 0,25 s abriu o gancho sem legenda.
- [ ] **Conferir a transcrição da montagem inteira com 1,5 s de folga no fim.** Sem folga, o Whisper inventa a última
  palavra. Ela serve para achar palavra faltando ou trocada, nunca para provar ponta.
- [ ] **Quem fala é quem diz a frase.** Fala de candidato ou documento lido pelo Raul leva o "ele disse" no texto, e fala
  de outra pessoa não vai na boca dele. No C05, o "é otário" era do Renan citado pelo Raul; no C27, o "não tem político que
  pode indicar" era do apresentador.

## 5. Imagem quadro a quadro: antes da ✋2

- [ ] **Folha de contato do `raul.mp4` a cada 2 s.**
  ```bash
  python $S/folha_contato.py assets/raul.mp4 --cada 2
  ```
  **Aprovado:** em TODOS os quadros, o Raul está inteiro, do cabelo ao queixo, com respiro, e o rosto tem o mesmo tamanho.
  Ninguém além de quem está falando aparece por engano.
  - No C28, o detector pegou um boneco da estante e o rosto saiu pela borda. A regra é o recorte largo, 1080 × 960.
  - No C44, a fonte cortou para o apresentador por 2,2 s e o recorte reserva escondeu a troca. Toda troca de cena dentro
    de um bloco é suspeita.
- [ ] **As trocas de câmera no quadro exato.**
  ```bash
  python $S/trocas.py <fonte> --de <s> --ate <s> [--regiao x,y,w,h]   # antes: o pts do 1º quadro novo
  python $S/trocas.py assets/raul.mp4 --tempos assets/tempos.json     # depois: em que bloco caiu cada troca
  ```
  **Aprovado:** cada troca de recorte cai no pts do 1º quadro do plano novo, sem arredondar para o quadro de 24. No C21,
  arredondada, a troca mostrava 1 ou 2 quadros da outra câmera com o recorte errado. Bloco que começa no quadro da troca
  usa o recorte do plano de DEPOIS (o `sol0` do C82 mostrou só a estante). Troca gradual (dissolve, foto entrando) se
  confere à mão.
- [ ] **O enquadramento segue as regras.**
  - **Raul sem zoom.** O rosto fica sempre do mesmo tamanho (C72: "tá ficando colado no rosto dele").
  - **Na tela dividida da fonte** (slide de um lado, Raul num painel), o painel dele PREENCHE a janela, mesmo com zoom.
    Nunca o painel no meio com laterais desfocadas (C82, reprovado).
  - **O rosto não encosta na lateral:** o "parece que tá falando com uma parede" do C46 se resolveu com o rosto perto do
    centro (~53%).
  - **O plano aberto da mesa serve** (C46).
- [ ] **A imagem é sempre a do mesmo instante do áudio.** Nada de encaixar gesto de outro momento: a boca não bate (C21,
  "tá horrível"). Quem escuta aparecer enquanto o outro fala é a edição da fonte e fica.
- [ ] **Nenhum quadro travado com fala.**
  ```bash
  python $S/travada.py assets/raul.mp4
  ```
  **Aprovado:** "✓ nenhuma imagem parada", ou seja, nenhum trecho parado de 0,35 s ou mais. Nunca `congela` nem `PARADO`
  em trecho com fala (o C44 foi ao ar com 2,2 s parado e pareceu vídeo travado: "isso não pode acontecer em hipótese
  alguma").
  - Quando a fonte troca de câmera no meio da fala, vai a imagem real: a outra pessoa bem recortada no rosto ou o plano
    aberto.
  - `"parado_ok"` só para gráfico ou slide em tela cheia, que não é o Raul.
  - Foto ou gráfico que tira o Raul da fonte vai para debaixo de uma TELA CHEIA da animação, como a Saveiro e o Saverin
    no C84.
- [ ] **Texto da fonte desfocado só onde estão as letras.**
  ```bash
  python $S/borrar_regiao.py ...    # ver o --help: região, de/até, borda esfumada
  ```
  **Aprovado:** a legenda gravada, o "deixe o like", o QR code e a faixa de propaganda ficam desfocados na caixa das
  letras, com a borda esfumada (o like do C84, a faixa do C81), e nada de rosto ou boca coberto. O que não fazer:
  - papel por cima: no C72 ele cobria a boca;
  - `removelogo` numa faixa inteira: deixa um borrão quadriculado;
  - `delogo`: a borda virou um risco claro no ombro (C30).
- [ ] **Podcast: quem aparece embaixo é quem fala.**
  **Aprovado:**
  - a câmera fica em quem está no raciocínio; fala por cima não troca a câmera;
  - a troca só acontece no plano aberto;
  - o apresentador aparece o mínimo: cada fala dele de 5 a 6 s derrubou de 5% a 10% da retenção (C40);
  - os rótulos de quem fala se conferem pela imagem, numa folha a cada 4 s com o tempo escrito (no C41 a separação de vozes
    trocou os rótulos).
- [ ] **✋ Aprovação 2.** Mandar o vídeo editado sem animação, com a legenda e a marca do canal, mais a lista das frases que
  saíram por falta de pausa limpa. Esperar a aprovação.
- [ ] **Antes de animar, parar e pedir o esforço extra.** Sem prazo, perguntar e esperar. Com prazo curto ("faz completo",
  hora marcada), avisar em uma linha e seguir. Por quê: a animação do C01 só chegou ao nível dela com muitas rodadas de
  conferência quadro a quadro.

## 6. Animação: antes do render

- [ ] **O script da página não tem erro de sintaxe.**
  ```bash
  python -c "import re; s=open('index.html',encoding='utf-8').read(); open('_check.js','w',encoding='utf-8').write(max(re.findall(r'<script>(.*?)</script>', s, re.S), key=len))" && node --check _check.js
  ```
  **Aprovado:** sem saída (apagar o `_check.js` depois). Por quê: no C39, um nome repetido no escopo do motor
  (`const cai`) matou o script inteiro, e o vídeo saiu sem animação e sem legenda. O `hyperframes check` disse "0 errors".
- [ ] **Zero erro de JavaScript na página aberta.**
  ```bash
  node $S/erros_js.mjs index.html
  ```
  **Aprovado:** "✓ sem erro de JavaScript". Os dois avisos de sempre do arquivo local ("setting 'main'" e o grão por CORS)
  já são ignorados. Por quê: no C47 um `W()` que não achava a palavra quebrou a linha do tempo, e o render saiu com a
  cena 0 parada até o fim. Erro de execução ("palavra não encontrada") deixa o vídeo em branco, e o `hyperframes check`
  não acusa.
- [ ] **Área de segurança.**
  ```bash
  node $S/zona_segura.mjs .            # [--passo 0.25]
  ```
  **Aprovado:** "✓ tudo dentro da área de segurança". Nasceu em 17/10, depois de o C80 e o C83 vazarem: etiqueta embaixo
  da busca do TikTok, carimbo saindo pela lateral e perna embaixo do texto do post.
  - **Folha de cima (50/50):** com a câmera em 1,0, o ponto (x, y) da cena cai na tela em (x, y + 155). Tudo fica entre
    x 40 e 1040 e entre y 45 e 800 da cena. O conferidor mede na tela: de y 150 a 955.
  - **O zoom de 3,5% da respiração** (`_vida.js`) puxa o topo da cena ~15 px para cima. Por isso a etiqueta começa em y 45
    da cena (tela 200), e não em 10.
  - **Tela cheia** (coordenada = tela): y de 150 a 1700, x de 40 a 1040, e de y 900 a 1700 nada passa de x 920 (a coluna de
    botões do TikTok). O pé de personagem fica em 1600–1620, nunca em 1740 (embaixo do nome e do texto do post).
  - **O que o conferidor não pega:**
    - a faixa da legenda (~880–990) livre na tela cheia: conferir na foto;
    - a altura do pé dos personagens (1600–1620): conferir na foto. O limite dos botões (x 920) ele pega desde 17/10;
      antes acusava só a partir de 936.
  - **Como o conferidor mede:** pelo que cada peça desenha (o `<span>` da etiqueta, as formas do SVG), não pela caixa. Ele
    ignora o que está inteiro fora do quadro (outra cena do chão) e os papeizinhos do carimbo (`pz…`), e só acusa o que
    fica fora 0,75 s ou mais.
  - **Peça de fundo larga de propósito:** `el.dataset.fundo = ""`.
- [ ] **Fotos de todas as cenas, nos instantes de cada entrada.**
  ```bash
  npx --yes hyperframes@0.8.99 snapshot . --at 0.5,3.2,7.8,... --describe false -o snapshots
  ```
  O `--describe false` deixa a análise por API desligada. **Aprovado:**
  - o texto fica dentro da caixa, com o tamanho calculado pela largura (`caber()`);
  - desenho de várias partes forma um corpo só;
  - a etiqueta velha sai quando a nova entra;
  - carimbo ao lado de carimbo não vira frase ("NÃO SÃO" + "O PROBLEMA", C09);
  - objeto que saiu andando não aparece na borda da cena vizinha (C41);
  - nada que entra subindo passa pela faixa da legenda (C44: a loja e a cabeça por cima da legenda; o remédio é o
    `clip-path` da `.cena`);
  - o gancho não tem tela vazia, o 1º elemento de cada cena entra junto com a 1ª palavra do bloco, e nenhum trecho de
    folha vazia passa de ~2 s;
  - o 1º quadro não está vazio;
  - objeto de ação (tesoura, moeda, mão) some depois da ação, e o contato acontece (C86, C87);
  - nada cobre o título da tela cheia, a cabeça de um personagem ou outra palavra; nada fica escondido atrás de um balão
    (C86); ✗ e ✓ não batem nas palavras (C85: o ✗ foi para x 940);
  - nenhum carimbo cai entre t0 − 0,5 e t0 de uma tela cheia (fotografar esse instante);
  - cada tela cheia tem peça nova em cada fala, do t0 ao t1 (C87);
  - o carimbo final pousa a 1 s ou mais do fim (fotografar o último segundo).
- [ ] **Âncoras das palavras certas.** TODA `T(palavra, bloco, n)` tem o `n` contado no `tempos.json` (o `batidas.md` do
  `roteirista.py` já traz o n certo). Não só as curtas ("com", "e", "vai", "Aí"): palavra de conteúdo também se repete no
  bloco ("história" e "construiu" no C87), e com o n errado o elemento entra segundos antes da fala, às vezes escondido
  atrás de uma tela cheia.
  - O `W()` acha a palavra dentro de outras frases: o "Aí" pegou o "E aí" no C39.
  - Em bloco longo, o `sai()` pode cair antes do `entra()` e deixar a etiqueta para sempre na tela (C41).
  - A deixa de câmera vai em palavra rara.
- [ ] **Telas cheias no padrão.**
  ```bash
  python -c "import json; j=json.load(open('assets/tela_cheia.json')); print(len(j), [(a, round(b-a-1, 1)) for a, b in j])"
  ```
  **Aprovado:**
  - desde 19/10: depois do gancho, telas cheias de 15 a 30 s alternando com o Raul por 5 a 10 s; somando, a tela cheia
    ocupa mais tempo que o Raul;
  - dentro de cada tela cheia, o palco com câmera: nenhum trecho de ~1,5 s sem acontecimento, gritos fora da faixa da
    legenda, rosto dos personagens acima de y 880; depois de cada tela cheia, o Raul na tela inteira por 2–3 s;
  - cada uma em fala visual (exemplo, número, cena), nunca onde o rosto do Raul importa;
  - cada uma com o par de sons de transição (ver `references/audio.md`).
  O C84 tem 4, de 8,7 a 12,8 s.
- [ ] **A legenda fica do começo ao fim, por cima da tela cheia.** Nenhum `tl.set("#leg", {autoAlpha: 0})` no
  `index.html`:
  ```bash
  grep -nE '("#leg"|\bleg\b)[^;]*autoAlpha: *0[^.0-9]' index.html
  ```
  **Aprovado:** nenhuma linha (no C84, nenhuma). Por quê: no C49 a faixa sumiu no gancho, e "não foi um texto
  estruturalmente para ser lido em uma ordem".
- [ ] **A marca do canal** (foto redonda e o @ do canal) está parada à esquerda na metade do Raul, some durante a tela
  cheia e volta depois. A capa não leva a marca.
- [ ] **Movimento fluido.** Nada em degraus (`Math.floor(q * n) / n`), e o grão do papel fica parado. Por quê: o grão que
  pulava inflava o vídeo ~3,5 vezes (C45: de 250 MB para 72 MB).

## 7. Áudio: antes do render

- [ ] **A trilha de efeitos e o relatório.**
  ```bash
  python gera_som.py && python $S/sonoplastia.py .
  ```
  **Aprovado:** o script termina com "✓ sem erro de JavaScript" e "✓ tudo dentro da área de segurança", e o
  `som_relatorio.txt` fica dentro da régua do C84:
  - a voz desce no máximo ~0,5 dB no −14 do finalizar;
  - o pico dos efeitos fica perto de −9 dBFS;
  - de 6 a 14 sons por 10 s;
  - no mascaramento, só palavras de ligação abaixo de 10 dB, nunca número, nome ou a palavra do soco;
  - o destaque fica em 100% de audibilidade;
  - nenhuma ação importante para a história fica "abafada".
  Como ler cada linha está em `references/audio.md`.
- [ ] **O ouvido.** Ouvir o `renders/som_mix.wav` de fone. **Aprovado:**
  - nenhum efeito aparece por cima da voz, e a transição fica de fundo;
  - nenhum grave contínuo perto de frase final ou de fala baixa (C29), nem no último segundo (C29, C31);
  - cada tela cheia tem o par de transição.
- [ ] **A voz está em −15 LUFS:** a linha "loudness integrada: voz −15,0" do relatório, ou a linha do `cortar.py`.

## 8. Render e mux

- [ ] **Renderizar só com os ✓ das seções 6 e 7.**
  ```bash
  npx --yes hyperframes@0.8.99 render . --fps 24 -q standard -w 6 -o renders/etapa3_bruto.mp4
  python $S/sonoplastia.py . --mux
  ```
  **Aprovado:** o render termina com "Render complete", e o mux imprime "com o som novo (imagem do render, áudio sem perda)".
  Depois de um render novo, o `etapa3_bruto_imagem.mp4` tem de ser o do render NOVO: o mux decide pelo codec (render =
  AAC, mux = FLAC). Por quê: no C82 o mux usou a imagem do render anterior.
- [ ] **Mudou só o som?** Rodar `gera_som.py`, `sonoplastia.py . --mux` e `finalizar.py`, sem renderizar de novo.

## 9. Finalizar

- [ ] **Volume, travada e prévia.**
  ```bash
  python $S/finalizar.py .
  ```
  **Aprovado:**
  - `volume: X → -14.0 LUFS, pico ≤ -1 dBTP (linear)`. A normalização tem de ser `linear`; `dynamic` quer dizer
    compressão, e aí se procura o pico ou o trecho muito mais baixo que o resto (LRA acima de 11);
  - `✓ nenhuma imagem parada na metade do Raul`. Trecho parado inteiro dentro de uma janela do `assets/tela_cheia.json`
    sai como "dentro da tela cheia: ok";
  - a prévia `renders/<cNN>_previa.mp4` em 720p, com o mesmo áudio AAC 256k do final;
  - sem o aviso "o áudio do etapa3_bruto.mp4 é aac", que quer dizer que o mux não rodou;
  - o `etapa3.mp4` bem abaixo de 240 MB (o C84 saiu com 133,5 MB na conta do `finalizar.py`).
- [ ] **Medir o arquivo final por conta própria.**
  ```bash
  ffmpeg -hide_banner -nostats -i renders/etapa3.mp4 -vn -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:"
  ```
  **Aprovado:** I = −14,0 LUFS (±0,3) e pico ≤ −1,0 dBFS. O C84 deu −14,0 e −1,9.
- [ ] **Duração:** passa de 1:00, porque o programa de recompensas só paga a partir de 1 minuto.
- [ ] **Aprimoramento da imagem (Real-ESRGAN) só com pedido explícito.** Nunca por iniciativa própria nem "para adiantar".

## 10. O vídeo pronto, antes de mandar

- [ ] **Folha de contato do vídeo pronto a cada 3 s.**
  ```bash
  python $S/folha_contato.py renders/etapa3.mp4 --cada 3
  ```
  **Aprovado:** olhar quadro por quadro e não achar nenhum destes:
  - **cena vazia:** folha sem nada por mais de ~2 s, gancho vazio, cena que espera a palavra para mostrar o 1º elemento;
  - **palavra coberta:** etiqueta, carimbo ou balão por cima de outro texto, ou por cima da legenda;
  - **etiqueta cortada:** texto passando da caixa ou da borda, peça embaixo da busca do TikTok, dos botões ou do texto do
    post;
  - **legenda faltando** em qualquer quadro, inclusive no gancho e na tela cheia;
  - **o Raul** cortado, com zoom, travado ou trocado por quem não fala;
  - **a marca** fora do lugar ou visível por cima da tela cheia;
  - **texto da fonte** sem desfoque.
- [ ] **Assistir à prévia inteira com som,** do começo ao fim, de fone, como quem vai assistir: emendas, efeitos, legenda
  e imagem juntos.

## 11. A prévia e a aprovação

A prévia é a aprovação da animação e do som e, sem pedido de mudança, a do render final.

- [ ] **Mandar a prévia de 720p e a capa, com o resumo:**
  - as telas cheias;
  - o que foi conferido (área de segurança, travada, loudness);
  - o que foi corrigido depois do 1º render;
  - o que saiu do roteiro e por quê;
  - a legenda do post.
- [ ] **Nada é agendado sem o "pode agendar" para AQUELE vídeo.** Por quê: em 03/10 um vídeo foi agendado direto e o dono
  do canal pediu para tirar: "quero ver o vídeo antes de agendar". Também vale:
  - "faz completo" autoriza produzir até o fim, não publicar;
  - vídeo refeito com mudança visível volta para a aprovação;
  - quando a resposta não deixa claro se é agora ou no horário combinado, perguntar em uma linha antes de rodar;
  - o pedido que já diz "agendado" ("quero pronto, tudo perfeito, agendado", C85 a C87) vale como o "pode agendar"
    daqueles vídeos; "faz completo" sem "agendado" não vale;
  - "subir público" é publicar AGORA (no C17 o agendamento das 21h foi desfeito); "pode postar" perto do horário foi
    "agendar no horário";
  - reagendar ou remarcar um vídeo já aprovado, a pedido do dono, não pede nova prévia;
  - um "pode agendar" vale para as três redes no mesmo horário, sem aprovar de novo em cada uma.
