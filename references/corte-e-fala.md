# Corte e fala: cortar sem comer palavra e conferir som e imagem

Etapa 2 inteira: da transcrição ao `raul.mp4` conferido quadro a quadro. Cada regra traz o porquê e o corte (C) que a
ensinou. Os comandos rodam da pasta `cortes/cNN-slug/`; `$S` é a pasta `scripts/` desta skill. Nenhum passo usa API.

## Ordem da etapa (checklist)

- [ ] Transcrever os trechos da fonte com `transcrever_local.py` (tempo absoluto na fonte).
- [ ] Conferir o texto no ouvido e corrigir nomes, números e siglas (`--texto`).
- [ ] Achar as trocas de câmera e de layout (`trocas.py`) e olhar a folha de contato de cada plano.
- [ ] Medir cada ponta com o `pausas.py` e escrever o `cortes_gerar.py`, que gera o `cortes.json`.
- [ ] Rodar o `cortar.py` e resolver cada ponta barrada.
- [ ] Desfocar o texto do canal dele, se houver (`borrar_regiao.py`).
- [ ] Rodar o `pos_cortar.py` (o TEXTO do roteiro realinhado) e o `legendas.py`.
- [ ] Ouvir as emendas (`ouvir_emendas.py`) e as pontas (`conferir_fins.py`), e resolver cada ⚠.
- [ ] Olhar a folha do `assets/raul.mp4` a cada 2 s e conferir as trocas com `trocas.py --tempos`.
- [ ] Confirmar que o `travada.py` passou (ele roda sozinho no fim do `cortar.py`).

O `cortar.py` regrava o `raul.mp4` e o `tempos.json`. Por isso, tudo o que lê a montagem (borrão, `pos_cortar.py`,
legenda, conferências) roda de novo depois de CADA corte.

## 1. Transcrição local, em tempo absoluto na fonte

```bash
python $S/transcrever_local.py ../../_fontes/<id>_opus.mkv ../../_pesquisa/<id>_palavras.json 07:50-10:15 20:54-21:30
```

- **Transcrever na FONTE, nunca no clipe cortado.** O `pausas.py` e o `cortar.py` trabalham em segundos da fonte.
- **Usar o Whisper só para o TEXTO.** No C29, o large-v3 pôs o "Mas" 1,4 s antes do real e o "Família" antes de ser
  dito, e escreveu "Já ganhei" no lugar de "Joga aí". Cada erro virou uma ponta errada. O tempo fino vem do alinhador
  MMS_FA e do vale de energia.
- **Conferir o texto no ouvido e corrigir.** No teste de 17/10 sobre o áudio do C84, o large-v3:
  - escreveu "Marcos Quebeco" no lugar de "Mark Zuckerberg";
  - trocou "Poderia se dizer" por "Poderia escrever";
  - inventou um "né?" no gancho.

  Com o texto certo num arquivo, `--texto arquivo.txt` mantém a escrita do arquivo e o tempo do Whisper. Assim o
  alinhador recebe a palavra que foi dita; palavra errada sai com "??".
- **Transcrever só os trechos candidatos.** Na CPU, 30 s de áudio levaram 81 s, contando a carga do modelo. O
  `--modelo medium` serve para uma 1ª leitura; o texto final sai do large-v3.
- **Outra opção:** `npx --yes hyperframes@0.8.99 transcribe <arq> -e whisper -m large-v3 -l pt --json`, com o tempo
  relativo ao arquivo (somar o início do trecho).
- **Medir as pontas no MESMO arquivo que o `cortar.py` corta: o `.mkv` com o Opus.**
  - No C20, o AAC do `.mp4` vinha 35,3 ms atrasado em relação ao áudio separado. Todas as pontas caíram 35 ms dentro da
    palavra vizinha.
  - No C23, a voz do AAC de 128k soou "vibrada, com cara de estourada".
  - Juntar o vídeo do `.mp4` com o Opus atrasado no mesmo tanto que o AAC, medido por correlação:
    `ffmpeg -i <id>.mp4 -itsoffset <atraso> -i <id>_audio.webm -map 0:v -map 1:a -c copy <id>_opus.mkv`. O atraso muda
    de fonte para fonte (35,3 ms no C20, 36,3 ms no C86): o `baixar.py opus` mede e junta sozinho.
  - Antes do roteiro aprovado, o `.mkv` ainda não existe: transcrever o `<id>_audio.webm` e somar o atraso medido.
- **Trecho embolado sai do roteiro.** Se a transcrição muda a cada leitura ou o ouvido não fecha o texto (C81: os dois
  modelos ouviam coisas diferentes; C83: o "Cadê, coadibe"), o trecho vai para o "Fica de fora". Sem o texto certo, o
  alinhador não confere a ponta e a legenda sai errada.
- **Com fonte AAC, medir o fim no arquivo inteiro.** No C44, ler o AAC com `-ss` antes do `-i` errou ~60 ms e fez
  parecer palavra cortada.

## 2. Medir as pontas com o `pausas.py`

```bash
python $S/pausas.py ../../_fontes/<id>_opus.mkv --palavras ../../_pesquisa/<id>_palavras.json 851.7:fortuna:quando --perfil
```

`t:antes:depois` = o instante aproximado da ponta, a última palavra que fica e a primeira que vem depois. Para cada t,
o script faz duas coisas:
1. lista as pausas reais a até 0,8 s (abaixo de −40 dB, 30 ms ou mais). Pausa no meio da frase não é fim de frase (no
   C01 o "desaparece" veio depois da pausa de "simplesmente…"): antes de fechar um bloco numa pausa, ouvir o que vem
   depois e conferir que a ideia fechou. Quando a palavra seguinte começa em p, t ou k, a ponta pode ficar na oclusão do
   1º som DELA, nunca na de um som do meio (C80: no vale do "q" sobrava um "Por-"; o corte foi para a oclusão do "P");
2. passa o texto da janela pelo alinhador forçado, que diz se cada vale cai ENTRE palavras ou DENTRO de uma.

| Marca | Significado | O que fazer |
|---|---|---|
| `·` / `=` | vale entre palavras / entre as palavras esperadas | candidato / o certo |
| `✗ DENTRO de X (entre 'g' e 'o')` | fechamento de consoante no meio da palavra | nunca cortar ali |
| `'p' de pai já em 78.372 (cortar antes)` | a palavra seguinte (f, s, x, p/t/k) já começa no vale | a janela termina antes |
| `?? não achou: X 0.00` | palavra não dita, dita diferente, engolida ou de outra voz | re-ouvir antes de confiar |
| `✓ janela sugerida: [a, b]` | a janela para o `cortes.json` | usar |
| `⚠ nenhuma pausa bate` | nenhum vale tem as palavras esperadas | ler os rótulos: a vizinha pode ter saído trocada |
| `✗ nenhuma janela` / `nenhuma pausa abaixo de −40 dB` | sem pausa limpa | `--perfil`; sem pausa, a frase sai |

**Regras da ponta:**
- **A ponta é o VALE, nunca o fim de palavra do alinhador.** O fim que ele dá é o começo do último som; a vogal final
  segue 0,1 a 0,3 s (teste do C67).
- **Não escolher "o vale mais fundo".** No C29, ele caiu entre "te" e "pagar".
- **Vale curto antes de vogal é consoante, não fim de palavra.** Já aconteceu com "tribu|tárias" (C09, 50 ms),
  "cam|panha" (C03), "Nun|ca" (C45, 140 ms: o vídeo abria em "…ca na história"), "ami|go" (C67) e "Exa|to" (C41, o `✓`
  estava na palavra do vizinho).
- **Cortar logo antes do ATAQUE da palavra seguinte, não no 1º mínimo depois do fim.** No C26, depois do "bém" de
  "também" vinham 200 ms de murmúrio nasal (−26 a −38 dB), e o corte no mínimo comeu a palavra.
- **Voz fraca entre duas palavras pode ser palavra.** No C48, o "Por" de "Por que eu tenho 200" estava a −33/−45 dB e
  passou por estalo de boca.
- **O "s" final emendado no "s" seguinte é um som só.** No C09 ("tributárias Se"), o corte foi no meio dele, antes da
  vogal. No espectro, energia acima de 4 kHz é "s" ou "x".
- **O "h" inicial é mudo e a letra dobrada é uma só.** O `alinhar.py` já trata os dois casos. No C84, o "h" de "Herança"
  caiu na pausa e deu um falso "DENTRO de Herança". No teste de 17/10, o 2º "n" de "Lemann" foi parar depois da pausa (o
  CTC exige um branco entre letras iguais), outro falso ✗.
- **Quando o alinhador se perder, decidir pelo envelope de 20 ms (`--perfil`).** Foi assim no C84, em 777,8, 794,6 e
  606,8. Exemplo na emenda "tipo. | Aqui": `21.48:-28 21.50:-41 21.52:-51 21.54:-180 … 21.74:-42 21.76:-17`. A fala cai
  abaixo de −40 dB em 21,50 e o "Aqui" ataca em 21,76; a ponta fica entre os dois.
- **Palavra engolida derruba o alinhador.** No C84 ("fortuna. | Quando"), o "Quando" saiu com score 0,00, todo vale virou
  ✗ e não houve janela. O perfil mostrou a pausa de −56 dB, e o bloco levou um `fala_ok` explicando isso.
- **Separar duas vozes emendadas pela altura.** No C21, o Raul ficava em 130–200 Hz e a Carol em 220–420 Hz.
  - Fala sobreposta não tem emenda limpa: cortar antes dela.
  - Começar sem o "ããã" arrastado.
- **Sem pausa limpa, a frase sai do roteiro e se avisa junto da prévia.** Foi assim no C48, no C49, no C67, no C81 e no
  C84 (o Harvard). Preferir o trecho contínuo mais longo a colar pedacinhos (C26).
- **Ponta de bloco:** não começar em palavra que depende da anterior ("porque", "então", "mas", pronome sem dono) nem
  terminar em conectivo ou no meio de lista.
- **Short ou Reel já editado:** o silêncio digital (−120 dB) entre trechos é a ponta mais segura. Sem pausa nenhuma, o
  vídeo vai inteiro num bloco (C08, C10, C11).
- **Ponta em cima de um corte da própria fonte não tem pausa** (C30: "fazer | Aí"). A fronteira é o vale de 20 a 30 ms
  desse corte, com `fala_ok` dizendo isso.
- **Mexeu numa ponta à mão? Medir de novo.** No C03, o vale curto entre "pa" e "nha" parecia fim de palavra e cortou o
  "campanha".

## 3. Cortar com o `cortar.py`

```bash
python cortes_gerar.py && python $S/cortar.py .
```

- Em cada ponta, ele pega o ponto mais quieto (RMS de 10 ms) dentro da janela do bloco.
- O ÁUDIO é cortado nesse ponto exato. Só o VÍDEO arredonda para o quadro, sempre para fora (início para trás, fim para
  frente), e a sobra vira silêncio.
- No C05, o áudio seguia o quadro e vários fins caíram no meio da palavra. No C01, arredondar para o quadro mais
  próximo jogou o início para dentro do ataque.

Ele grava em `assets/` o `raul.mp4` (24 qps, com o número exato de quadros por pedaço: no C21 a imagem atrasou 8
quadros em 110 s), o `raul_bruto.wav` (PCM, sem outro AAC: C23), o `raul.wav` (−15 LUFS) e o `tempos.json`.

**As travas (desde o C26).** O "inves|tir", o "minús|culo" e o "al|ta" saíram comidos: os cortes caíram em vales de 10 a
70 ms, um a −49 dB, que eram consoantes dentro da palavra. Agora o corte para com ⛔ quando:
- a ponta está acima de −40 dB;
- depois do FIM vem voz curta (menos de 220 ms) e outro vale (`rabo()`): é a sílaba final comida. No teste de 17/10, um
  fim dentro de "for|tuna" parou com "voz de 145 ms logo depois do corte";
- antes do INÍCIO há voz curta com um vale antes (`cabeca()`): é a 1ª sílaba que ficou de fora. No C26, o "O" de "O meu
  conteúdo" vinha antes de um "hum" a −40 dB.

**`fala_ok`.** A trava só se libera com `"fala_ok": {"ini" | "fim": "motivo"}`. O motivo sai do envelope e do alinhador,
nunca do Whisper. Exemplos reais do C84:
- `"a voz antes do corte é o fim de 'fortunas aqui.' (alinhador: 'aqui.' | 'Poderia'); vale de −51 dB"`;
- `"a voz depois do corte é o 'Então caminho' seguinte (o 'E' em 1288,39); vale de −72 dB"`;
- `"o 'h' de herança é mudo: a pausa de −60 dB de 606,54 a 606,80 é o vão antes da palavra"`.

A saída preferida é mover a ponta para a pausa antes da palavra seguinte. Nunca para o 1º vale depois do fim que o
Whisper marca: ele marca o fim cedo.

**Emenda seca e `respiro`.** Entre frases, menos de ~200 ms de silêncio soa colado (C29: "Família | Cara", com 60 ms).
- Pôr o início do bloco no começo ou no meio da pausa.
- Com a pausa da fonte curta demais, usar `"respiro": 0.083` a `0.15` no bloco de antes: silêncio e o último quadro
  parado. Nasceu no C34; no C84, foram 0,15 s antes do "Herança" (60 ms de emenda).
- Até 2 ou 3 quadros parados não se notam. Acima de 0,2 s, nota-se; a partir de 0,35 s, o `travada.py` barra.

**`fade_fim`.** Fim emendado sem pausa leva fade maior que os 15 ms padrão (C82: 0,035 em "trabalhar. | Você"). Fim sem
pausa limpa pode ser cortado no respiro, com fade, antes da palavra seguinte (C57, C61). Para juntar dois vídeos, o bloco
leva `"fonte"` e `"palavras"` próprios (C17).

## 4. O `cortes.json`

Escrever pelo `cortes_gerar.py`, com o porquê de cada ponta em comentário, nunca à mão. Trecho real do C84:

```json
{"fonte": "../../_fontes/z99ri8YcCsY_opus.mkv", "palavras": "../../_pesquisa/z99_palavras_mkv.json",
 "janela": [1080, 960], "recorte": {"w": 1215, "y": 0}, "correcoes": {}, "destaques": ["71%", "Saverin"],
 "blocos": [
  {"id": "top", "ini": [468.040, 468.430], "fim": [488.580, 488.795], "x": [1186, 734, 0],
   "trocas": [[479.333, [353, 1215, 0]]]},
  {"id": "lemann2", "ini": [564.675, 564.740], "fim": [575.140, 575.220], "x": [353, 1215, 0], "respiro": 0.15,
   "fala_ok": {"ini": "a voz antes do corte é o fim de 'Eduardo Saverin.'; vale de −62 dB"}}]}
```

| Campo | O que é |
|---|---|
| `janela` / `recorte` | a janela do Raul (`[1080, 960]`) e a largura e o y padrão; a altura sai da janela |
| `ini`, `fim` | janelas de BUSCA de cada ponta (a `✓ janela sugerida`) |
| `x` | `353` (x com a largura padrão), `[x, w]` (painel estreito, C03), `[x, w, y]` (plano completo, C09) ou `"cheio"` (o quadro inteiro sobre ele desfocado, C20) |
| `trocas: [[t, x], …]` | a fonte troca de plano no meio do bloco: o recorte muda em t (segundos da fonte); o áudio segue |
| `respiro`, `fade_fim`, `fala_ok` | ver a seção 3 |
| `parado_ok` | libera o `travada.py` num bloco que não é o Raul (gráfico em tela cheia) |
| `tapar: [[máscara.png, desde], …]` | texto da fonte que invade o recorte (C30) |

- **Pôr `trocas` no quadro exato, sem arredondar.** O t é o pts do PRIMEIRO quadro novo, como o `trocas.py` dá. No C21, a
  troca arredondada mostrava 1 ou 2 quadros da outra câmera com o recorte errado.
- **Bloco que começa em cima de uma troca leva o recorte do plano de DEPOIS.** No C82, o `sol0` mostrou só a estante.
- **Nunca usar `de` com pessoa.** O `de` põe a imagem de outro instante, e no C21 a boca e o gesto não batiam com o
  áudio. A imagem é sempre a do mesmo instante.
- **Nunca usar `congela` com fala.** Quadro parado com voz andando parece vídeo travado (C25, C42, C44; seção 11).
- **`tapar`:** a máscara tem o tamanho da fonte, com branco = letras, e é uma por pedaço que entra em hora diferente.
  Pegar os pixels de texto na INTERSEÇÃO de vários quadros (a mão que passa fica de fora) e alargar 5 px.
  - Nunca `delogo`: no C30, deixou um risco do pescoço no ombro.
  - Nunca `removelogo` numa faixa inteira: no C72, deixou um borrão quadriculado.

## 5. Enquadramento do Raul

- **Embaixo, sempre que possível, fica o Raul:** o produto é a animação de cima (C25). Na tela dividida entra só a faixa
  dele; slide, gráfico ou manchete só vão para baixo quando o Raul some da fonte.
- **A imagem é sempre a do mesmo instante do áudio** (C21: "tá horrível"): nada de `de` (imagem de outro instante) nem
  `congela` com pessoa. O `cortar.py` ainda aceita os dois campos, mas eles só servem para plano sem gente.
- **Raul INTEIRO, do cabelo ao queixo, em todos os quadros.** O `cortar.py` usa recorte FIXO por bloco (`[x, largura, y]`
  no `cortes_gerar.py`; no estúdio dele, `[353, 1215, 0]`, que a janela de 1080 × 960 escala). No C28, um detector
  automático de rosto pegou o boneco da estante e apertou o recorte para 776 px: por isso o recorte é largo e fixado à mão
  depois de olhar a folha (o neon do C48 `[450, 1080, 60]`, a mesa do C40, a TV e o boneco do C49). Só o `reenquadrar.py`
  detecta rosto, e só para short vertical.
- **Sem zoom, rosto sempre do mesmo tamanho** (C72: "tá ficando colado no rosto dele… não deixa o rosto dele ficar
  cortado"). O proibido é o zoom que VARIA ao longo do vídeo e o rosto colado; uma ampliação fixa para centrar ou para
  o painel preencher a janela (1,32× no C46, 1,47× no C82) pode. Fonte que é short vertical com os zooms do editor passa pelo `reenquadrar.py`:
  1. rodar o `cortar.py` numa subpasta (`_alto/cortes.json` com `"janela": [1080, 1920]`, `"recorte": {"w": 1080, "y": 0}`
     e `"x": [0, 1080, 0]` em cada bloco, sem trocas nem `tapar`); refazer o `_alto/` sempre que o corte mudar;
  2. rodar `python $S/reenquadrar.py . _alto/assets/raul.mp4 --base <linha acima da legenda> --legenda <faixa> --fixo a-b:y`.

  Ele afasta a imagem quando o rosto cresce, segue a cabeça e desfoca SÓ a caixa das letras da legenda gravada. As
  laterais desfocadas existem só aí. Depois de um `cortar.py` novo, mover para `_lixeira/` o
  `raul_antes_reenquadrar.mp4` antes de reenquadrar de novo (senão o script usa o áudio antigo) e rodar o `travada.py`
  outra vez no fim.
- **Na tela dividida, o painel do Raul PREENCHE a janela** (C82, zoom de 1,47×). O painel no meio com laterais
  desfocadas foi reprovado: "ele é para ocupar a parte de baixo inteira".
  - Medir onde o painel começa: no C25 era x = 1249, e com 1236 sobrava uma borda preta.
  - No estúdio dele (C82, C84): plano aberto `[353, 1215, 0]`, painel `[1186, 734, 0]`.
  - No painel, o cabelo chega perto do topo: conferir na folha.
- **Centrar o rosto.** No C46, o Raul a 64% da largura parecia "falando com uma parede". A janela de 816 px ampliada
  1,32× levou o rosto a ~53%.
- **Deixar o logo de outro canal fora do recorte** (C45: x ≤ 1190, por causa do neon).
- **Foto ou gráfico em tela inteira (o Raul some) vai para debaixo de uma TELA CHEIA da animação.** No C84, a foto do
  Saverin entra em 485,25 (e a da Saveiro, por cima, em 480,75). Nunca o último quadro congelado: revogado em 10/10,
  depois do C25.
  - Modo `"cheio"` no lugar da tela cheia: só quando a manchete ou o gráfico da fonte PRECISA ser lido inteiro e a
    animação não o substitui (C20, C61). No resto, a tela cheia da animação cobre a foto ou o gráfico.
- **Flash ou transição gráfica da própria fonte** se cobre com uma passagem de papel da animação ou com a tela cheia,
  nunca com quadro congelado (o `travada.py` barra).
  - No C52 e no C55, o recorte de 1215 cortava a manchete do terço de baixo; o plano inteiro foi `"cheio"`.
- **Desfocar texto ou overlay do canal dele** (C84: "Deixe o like na CONFIANÇA", de 8,9 a 13,0 s), depois do `cortar.py`,
  nos pixels e tempos da montagem: `python $S/borrar_regiao.py assets/raul.mp4 --regiao 0,670,520,220,8.8,13.0`.
  - A borda sai esfumada; o lado que encosta na tela não esfuma.
  - Ele não passa duas vezes.
  - Serve também para faixa de propaganda (C81: a da AUVP com QR code, y 688–960, de 56,5 a 65,8 s).
- **Legenda queimada na fonte em vários blocos:** recortar acima dela ou desfocar a faixa numa cópia da fonte, antes do
  `cortar.py` (C06, C10, C19, C39).
- **Corte seco de zoom do editor** (o mesmo plano, mais perto ou mais longe; no C84, em 14,29 e 18,88): o `trocas.py`
  mostra. Não pede recorte novo se o Raul continua inteiro.

## 6. Podcast com duas pessoas

- **Pôr a imagem em quem fala** (C27). Com a imagem no Raul e a voz do apresentador, parece que a voz não é de quem está
  na tela.
  - A câmera fica em quem está no raciocínio.
  - Ela vai para o outro quando ele fala DEPOIS que o primeiro terminou, e volta quando o primeiro retoma.
  - Fala por cima não troca: trocar a cada palpite picota a imagem.
- **Trocar só no plano aberto,** com os dois na mesa: o recorte vai para o outro e volta, por `trocas` (no Flow,
  `[0, 760, 395]`). No close de um só, fica a edição do próprio podcast.
- **Manter quem escuta quando a fonte mostra quem escuta,** bem recortado no rosto: é a edição da fonte (C21). Exemplos:
  o Vilela no C44, o Igor por 0,25 s no C49, ~4 s no C79.
- **Deixar o mínimo de apresentador.** No C40, a retenção mostrou que cada fala dele de 5 a 6 s tira de 5% a 10% das
  pessoas. Fica só o bate e volta rápido, salvo a fala que dá o gancho do que o Raul vai dizer ("tem que fazer sentido").
- **Pergunta no começo só quando a resposta não se entende sem ela** (C68; a do Nordeste, no C51, era indispensável).
- **Marcar no roteiro a fala que não é do Raul** (C27: o fecho "não tem político que pode indicar" era do apresentador).

**Quem fala, sem API (método manual). Obrigatório em todo corte com 2 pessoas ou mais**, logo depois do `cortar.py` e
antes da legenda:
1. Fazer a folha do trecho da fonte a cada 2 a 4 s (`folha_contato.py --de --ate --cada 2`): quem está na tela, de quem a
   boca mexe.
2. Ouvir cada troca de voz: o Whisper local dá o texto, o ouvido diz a voz, e a altura ajuda (o Raul fica em
   130–200 Hz). A boca decide: no C49, o "Acho que para o Brasil" que a diarização deu ao apresentador era do Raul.
3. Marcar no `pos_cortar.py`, no `OUTRO`, as palavras de quem não é o Raul: elas ganham `"quem": "apresentador"` e vão
   para o cartão escuro da legenda. É o caminho que vale: o `pos_cortar.py` grava `"quem"` em TODA palavra, e o
   `assets/quem_fala.json` (`[{"quem": "apresentador", "s": 12.4, "e": 14.1}]`) só é lido para palavra sem `"quem"`.
   Qualquer voz que não é a do Raul (apresentador, convidado, aluno) leva o rótulo `"apresentador"`, o único que vai
   para o cartão escuro; com dois convidados (C87), os dois entram assim.
4. Nunca usar as marcas `>>` da legenda do YouTube: no C27, elas inverteram os trechos. A diarização também troca rótulos
   em trecho longo (C41), então toda separação se confere na imagem.

- **Opção local:** o speechbrain (`spkrec-ecapa-voxceleb`) compara cada trecho, por cosseno, com uma amostra de 5 a
  10 s de cada voz. Rodou offline em 17/10 (Raul × Raul: 0,78–0,82; no Windows, `local_strategy=LocalStrategy.COPY`),
  mas não foi testado com duas vozes: é palpite, conferido na folha.
- O alinhador é fraco na voz do apresentador (C67: score 0,02 no "alto" do Vilela). Perto da troca de voz, o rótulo do
  `pausas.py` vale menos.
- Fala do apresentador por cima embaralha as palavras da fonte. Aí a legenda sai da transcrição da própria montagem
  (C35, C36, C46).

## 7. `pos_cortar.py`: o TEXTO do roteiro realinhado

A transcrição erra o tempo das palavras em até 0,4 s (C79–C84: o "né?" 0,39 s antes, o "senador" 0,28 s depois) e perde
palavras nas pontas (o "Ou" de "Ou Gustavo Lima", o "Se" de "Se aqui na empresa"). Então o texto de cada bloco vem do
roteiro, e o tempo de cada palavra vem do alinhador sobre o áudio do bloco.

Usar o `pos_cortar.py` que vem com o modelo (`assets/modelo/`, copiado para a pasta do corte) e preencher:
- **TEXTO:** a escrita certa, o que o Raul disse ("Marcos Quebeco" → "Mark Zuckerberg");
- **FALA:** como se pronuncia, só para o alinhador (`"6x1"` → `"6 por 1"`; sem isso, vira o token "seisxum"). Sigla
  soletrada vai como se fala; número com algarismo vai por extenso sozinho. A legenda fica com a escrita do TEXTO;
- **OUTRO:** os índices das palavras do apresentador (`"quem": "apresentador"`).

O fim de cada palavra é o começo da seguinte, no máximo 0,9 s, porque o alinhador só marca o começo do som. O script é
idempotente: rodar depois de cada `cortar.py`. Se a pasta `scripts/` não estiver em `~/.claude/skills/edicao-de-cortes`,
apontar `EDICAO_CORTES` para a pasta da skill.

## 8. Legenda (`legendas.py` → `assets/dados.js`)

```bash
python $S/legendas.py .
```

- **De 1 a 3 palavras, até 15 caracteres, sempre em linha única.** A legenda curta já troca rápido; qualquer coisa a mais
  rouba tempo de leitura (C27: "mal dá pra ler").
- **Fechar o bloco** na pontuação, numa pausa de mais de 0,35 s, na troca de bloco e na troca de quem fala. Nunca
  terminar em palavra fraca ("de", "o", "e", "que").
- **Número junto da unidade** ("5 MILHÕES") e da palavra que o anuncia.
- **A 1ª legenda entra no 1º quadro.** No C68, a 1ª palavra marcada em 0,25 s abriu o gancho sem legenda; no C10, o
  "O QUE" sumia nos primeiros 0,6 s.
- **Nunca duas etiquetas na tela:** a próxima entra e esta sai.
- **Vermelho** em número, dinheiro, palavrão censurado e na lista `"destaques"` do `cortes.json`.
- **Palavrão nunca por extenso** (C27: "pra não sofrer restrição"). O `censura()` deixa a 1ª e a última letra (FODA →
  F\*\*A, CARALHO → C\*\*\*\*\*O) e parte no hífen: no C44, o "foda-se" passou inteiro até a correção.
  - Palavra nova que escapar vai para a lista `PALAVROES`.
  - Vale também para a legenda do post e as etiquetas da animação.
  - As `palavras` ficam cruas, para a animação e o som acharem a palavra.
- **Legenda do começo ao fim, sem sumir no gancho** (C49). Lá a faixa sumiu nos 10 primeiros segundos, e a fala na cena
  "não foi um texto estruturalmente para ser lido em uma ordem". Nunca `tl.set("#leg", {autoAlpha: 0})`; a cena pode
  brincar com palavras-chave, só como complemento.
- **`correcoes`** troca palavra a palavra na legenda; o caminho principal é o TEXTO do `pos_cortar.py`. O visual (cartão
  branco, até 58 px em 620 de largura, marca-texto na palavra dita) é da animação.

## 9. Conferir as emendas no ouvido

```bash
python $S/ouvir_emendas.py .        # depois do cortar.py e do pos_cortar.py, antes de qualquer render
python $S/conferir_fins.py .        # as pontas de cada bloco, na fonte
```

**O `ouvir_emendas.py`:**
- prende a janela de ±2,5 s de cada emenda numa pausa de verdade (sem isso, ele acusava a palavra que o ARQUIVO cortou na
  ponta da janela: C26, C27);
- transcreve a janela com o Whisper local e compara com as palavras esperadas (número por extenso dos dois lados);
- faz a 2ª conferência, que decide: o silêncio na emenda (abaixo de −40 dB) e o alinhador com o texto esperado. Palavra
  com som dos dois lados do silêncio ATRAVESSA a emenda.

| Saída | O que fazer |
|---|---|
| `✅` | segue |
| `REAL: «x» atravessa a emenda` | mover a ponta para a pausa antes da palavra seguinte, cortar e ouvir de novo |
| `voz na emenda (só N ms abaixo de −40 dB)` | conferir no envelope |
| `provável FALSO ALARME` | o Whisper ouviu diferente, mas há silêncio e nada atravessa: segue |
| `?? o alinhador não achou` | re-ouvir (palavra engolida, dita diferente, outra voz) |
| `emenda seca (N ms)` | início no meio da pausa ou `respiro` |

Validação de 17/10: no C84 (aprovado), 0 REAL; num teste com o fim dentro de "for|tuna", o Whisper ouviu "fortuna"
inteira, e o alinhador deu REAL. O código de saída é 1 quando há REAL.

- **Nunca aceitar o ✅ do Whisper sozinho.** Ele completa palavra comida: no C26, "confirmou" o "inves|tir" que foi ao ar
  comido. O ✅ vale junto com as travas do `cortar.py` e com o alinhador.
- **Descartar um ⚠ só com o envelope, nunca "porque o vale é fundo".** No C26, o "minús|culo" foi cortado a −49 dB.
- **Falsos alarmes conhecidos:**
  - número falado × escrito ("9 mil reais" × "R$ 9.000");
  - conectivo inventado no começo do trecho ("Então", "Mas", "E") com silêncio antes;
  - palavra cortada pela ponta da janela;
  - erro de escuta longe da emenda.
- **Achados REAIS de antes:** o "inves|tir" e o "também" (C26), o "Nun|ca" (C45), o "ami|go" (C67), o "Exa|to" do
  vizinho (C41), o "Por" (C48), o "cen|to" e os "4,96 cent…" (C25).
- **Tirar a dúvida** com `python $S/pausas.py assets/raul_bruto.wav <t> --perfil` ou
  `python $S/alinhar.py assets/raul_bruto.wav <a> <b> "texto" --letras --pausas`.
- **Conferir o fim com uma janela que PASSA do corte (±1,5 s).** No C25, o Whisper da frase inteira escreveu "R$ 4,96" e
  escondeu o "centavos" cortado.

**O `conferir_fins.py`** confere cada ponta na fonte, de três jeitos:
- mede os 20 ms de energia da ponta;
- ouve isolado o fim e o começo do bloco;
- marca ⚠ em corte num vale curto (menos de 80 ms abaixo de −40 dB) com fala forte a até 60 ms.

No teste de "for|tuna", o Whisper isolado deu ✓, e quem pegou foi o ⚠ do vale curto. Todo ⚠ se confere no perfil.

## 10. Folha de contato e conferência quadro a quadro

```bash
python $S/folha_contato.py assets/raul.mp4 --cada 2                                   # depois do cortar.py
python $S/folha_contato.py ../../_fontes/<id>_opus.mkv --de 468 --ate 489 --cada 2    # o recorte de cada plano
python $S/trocas.py assets/raul.mp4 --tempos assets/tempos.json                       # as trocas no quadro certo
```

As folhas saem com 320 px por quadro e o tempo escrito, em lotes de até ~2400 px de altura, para dar para ler.

**O que procurar:**
- [ ] O Raul inteiro, do cabelo ao queixo, com respiro (C28, C72).
- [ ] Quem está no quadro. No C44, 2,2 s do Vilela ouvindo passaram por "Raul". Toda troca DENTRO de um bloco é suspeita
      até a folha mostrar quem está ali.
- [ ] Borda preta (C25) e laterais desfocadas na tela dividida (C82).
- [ ] Texto, manchete ou logo do canal dele à vista ou cortado (C45, C52, C84).
- [ ] O detector preso no boneco da estante ou na TV (C28, C49).
- [ ] Foto ou gráfico em tela inteira: anotar o intervalo para a tela cheia (no C84, de 52 a 58 s).

**Quadro a quadro, em volta de cada troca e de cada emenda:**
1. Rodar o `trocas.py --tempos`. Ele dá cada troca com o bloco e o tempo na fonte. No C84, achou a troca do bloco top
   (`49.708 … fonte 479.334`), a emenda do bloco eua (`21.542`) e as três do bloco fundadores (1257,750, 1285,625 e
   1287,542). Na fonte:
   - `--regiao x,y,w,h` pega a troca de layout pelo brilho de uma área (o slide escuro × a estante); escolher uma área
     onde a mão não passa;
   - `gradual` é dissolve ou foto entrando por cima.
2. Extrair o último quadro velho e o 1º novo: `ffmpeg -ss 49.667 -i assets/raul.mp4 -frames:v 1 a.png` e o mesmo em
   49.708. O 1º quadro novo já tem que estar com o recorte novo.

## 11. `travada.py`: o Raul nunca travado

⛔ "Isso não pode acontecer em hipótese alguma" (10/10). O `PARADO` do C44 (2,2 s com o Vilela ouvindo) e os congelados
do C37, do C38 e do C42 (0,5 a 0,7 s) foram ao ar e pareceram vídeo travado, o mesmo erro do C25.

- **Detecção:** o `cortar.py` roda o `travada.py` no fim e para com ⛔ em 0,35 s ou mais de quadro parado (freezedetect a
  −70 dB). O `finalizar.py` repete no vídeo final, com `--raul` (só o rosto). A −60 dB, a mesa quase parada do C46
  virava "travada"; o respiro de até 0,2 s fica abaixo do mínimo.
- **Solução:** a imagem real daquele instante: a outra pessoa bem recortada ("não tem problema dessa pessoa aparecer por
  alguns segundos"), o plano aberto da mesa (C46) ou, se a fonte congela ou some com o Raul, uma tela cheia por cima.
- **Exceção:** só um gráfico ou slide em tela cheia, que não é o Raul, passa, com `"parado_ok": "motivo"`. As janelas
  de tela cheia da animação são ignoradas no final.
- **Teste avulso:** `python $S/travada.py assets/raul.mp4` (sai com 1 e lista os trechos).

## Antes de mostrar a etapa 2

- [ ] Nenhuma ponta barrada sem `fala_ok` com motivo do envelope.
- [ ] `ouvir_emendas.py` sem REAL; cada ⚠ e cada `??` conferido no perfil.
- [ ] `conferir_fins.py`: cada ⚠ de vale curto conferido.
- [ ] Nenhuma emenda seca entre frases (ou `respiro` posto).
- [ ] Na folha do `raul.mp4`: o Raul inteiro, sem borda, sem texto do canal dele e com a pessoa certa em cada quadro.
- [ ] Trocas no quadro exato; fotos em tela inteira anotadas para as telas cheias.
- [ ] `travada.py` passou; a legenda vai do 1º ao último quadro, com palavrão censurado.
- [ ] A lista do que saiu por falta de pausa limpa, para contar junto da prévia.

**A ✋2 (aprovação do corte, quando o dono pede para ver antes da animação):** montar com o `montar.py` do modelo e um
`_cenas.js` só com o `camera([...])` (o Raul embaixo, a folha vazia em cima, a legenda e a marca), renderizar em
`renders/etapa2.mp4` e mandar com a lista do que saiu por falta de pausa limpa. Depois, PARAR. Quando o dono libera
seguir sem esperar ("depois daí já pode ir para a animação"), a etapa 2 vai para ele do mesmo jeito, em paralelo.
