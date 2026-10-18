# Áudio do corte: fonte, volume e sonoplastia

A voz do Raul é o produto: ela chega ao celular limpa, no volume certo e sem efeito por cima. Cada regra traz o porquê
(a lição e o corte de onde veio). `$S` = a pasta `scripts/` desta skill. Os comandos rodam de dentro da pasta do corte.

## A cadeia

```
Opus do YouTube + vídeo do .mp4 → <id>_opus.mkv → cortar.py → raul_bruto.wav (PCM) → raul.wav (PCM, −15 LUFS)
→ sonoplastia.py → sfx_mix.wav + som_mix.wav (voz + efeitos, PCM) → render (só a imagem) → --mux (FLAC)
→ finalizar.py → etapa3.mp4 (AAC 256k, −14 LUFS, −1 dBTP) e a prévia com o MESMO áudio
```

Só há duas compressões com perda: a da fonte (o Opus) e a do `finalizar.py`. Toda mudança na cadeia mantém isso.

## 1. A melhor faixa da fonte

- [ ] **Usar o Opus do YouTube (`.webm`, formato 251), nunca o AAC de 128k de dentro do `.mp4`.** Por quê: no C23
  (05/10/2026) a voz soou "meio vibrada, como um áudio estourado que a gente diminui e ainda fica a sensação de estouro".
  Não havia clipagem: o AAC de 128k é a pior faixa (difere do Opus em −20 dB), e o limitador forte da gravação do Raul faz
  cada perda soar como estouro.
- [ ] **Juntar o vídeo do `.mp4` com o Opus num `.mkv`, sem recomprimir, e cortar desse `.mkv`:**
  ```bash
  ffmpeg -i <id>.mp4 -itsoffset 0.0353 -i <id>_audio.webm -map 0:v -map 1:a -c copy <id>_opus.mkv
  ```
  Os 35,3 ms são o atraso do AAC do `.mp4` em relação ao `.webm` nos vídeos do Raul. Conferir por correlação em cada fonte
  (no C23 sobrou 0,3 ms). Vídeo do DASH, só imagem, começa em 0 junto com o Opus: sem atraso (C68).
- [ ] **Medir as pontas no MESMO arquivo que o `cortar.py` corta.** Por quê: no C20 os vales foram medidos no `.webm` e o
  corte saiu do `.mp4`; todas as pontas caíram 35 ms dentro da palavra vizinha. Transcreveu no áudio separado? Somar o
  atraso nas janelas e nas palavras (o `DESVIO` do `cortes_gerar.py` do C20).
- [ ] **Medir o fim no arquivo inteiro.** Ler um AAC com `-ss` antes do `-i` erra ~60 ms e parece palavra cortada (C44).
- [ ] **Outra fonte (TikTok, Instagram, podcast de outro canal):** pegar a faixa de maior qualidade e contar quantas
  compressões com perda o áudio atravessa. O ideal é uma só além da fonte: a do `finalizar.py`.

**Em aberto.** Na noite do C23 o dono do canal não sentiu diferença grande com o Opus ("vamos manter assim por
enquanto"). Então: vídeo novo vai com Opus e PCM até o render (é barato e não piora nada); corte já aprovado não tem o
áudio refeito ("se passou por mim já estava bom"); e a causa da voz "vibrada" pode ser outra (o limitador da gravação, o
volume dos efeitos), o que pede um teste A/B com ele quando houver tempo.

## 2. A voz em PCM até o render

- [ ] **O `cortar.py` grava o `raul_bruto.wav` direto do filtro, em PCM 48 kHz.** Nunca extrair a voz de um MP4
  intermediário. Por quê: no C23 a voz era recomprimida mais três vezes (no AAC do `raul.mp4`, no render e na prévia), e
  cada vez ficava mais metálica. O `sonoplastia.py` para se a voz não estiver em 48 kHz.
- [ ] **Saída em AAC 256k, a prévia inclusive.** O `finalizar.py` grava o `etapa3.mp4` em 256k, e a prévia de 720p COPIA
  esse áudio. Por quê: com a prévia em 128k, a aprovação seria feita ouvindo um áudio pior que o que vai ao ar.
- [ ] **Normalização linear, em duas passadas, e nada de compressor na voz.** Por quê: a voz já vem com o limitador da
  gravação, e mais compressão soa como estouro.

## 3. Loudness: −15 no corte, −14 na entrega

| Ponto | Alvo | Quem faz | Medido no C84 |
|---|---|---|---|
| `raul_bruto.wav` | o da fonte | `cortar.py` | −17,2 LUFS |
| `raul.wav` | **−15 LUFS** (2 passadas) | `cortar.py` | −15,0 LUFS, pico −3,5 dBFS |
| voz + efeitos | ~−15 | `sonoplastia.py` | −14,9 LUFS |
| render | o do mixer (a regra antiga diz ~−17) | HyperFrames | −15,0 LUFS, AAC ~192k |
| `etapa3.mp4` | **−14 LUFS, −1 dBTP, LRA 11** | `finalizar.py` | −14,0 LUFS, pico −1,9 dBFS |

- [ ] **Voz em −15 LUFS no corte.** Por quê: com os efeitos por baixo, a mixagem fica perto de −14, e o `finalizar.py` quase
  não mexe na voz. O relatório mostra isso em "no −14 do finalizar a voz desce X dB" (C84: 0,0).
- [ ] **Não confiar no nível do render.** A regra antiga dizia ~−17 LUFS; no C84 saiu −15,0. O `finalizar.py` mede antes de
  corrigir, a cada vídeo. Nunca acertar volume à mão nem no `data-volume`: o `<audio id="sfx-mix">` fica com `1`.
- [ ] **Entregar em −14 LUFS e pico de −1 dBTP:** `python $S/finalizar.py .` mede na 1ª passada e aplica um ganho único
  na 2ª (`linear=true`), só no áudio, com o vídeo copiado. A linha impressa termina com o tipo: tem de ser `linear`. O
  loudnorm só fica linear quando o pico, depois do ganho, cabe em −1 dBTP e a LRA da mixagem é de no máximo 11. Saiu
  `dynamic`? Ele comprimiu: procurar o pico (estalo, plosiva) ou o trecho muito mais baixo que o resto.
- [ ] **Pico dos efeitos em −9 dBFS** (o `sonoplastia.py` limita). Por quê: o estalo do carimbo empurrava o pico da mixagem
  e travava o loudnorm linear.
- [ ] **Nada abaixo de 70 Hz nos efeitos** (o `sonoplastia.py` corta). Por quê: o celular não reproduz esse grave, mas o
  loudnorm o conta; a mixagem parecia "mais alta" e o `finalizar.py` baixava a voz junto.

## 4. A sonoplastia profissional (`som.json` → `sonoplastia.py`)

Padrão em todo vídeo desde 14/10/2026. Antes eram 13 arquivos repetidos, 28 dB abaixo da voz, e o `papel.wav` estava mudo
(−61 dBFS de pico). O pedido: "estamos usando muito pouco efeito sonoro… os efeitos sonoros acrescentam muito à imersão…
ainda com a regra de não sobrepor o áudio da fala… cria uma lógica profissional". Aprovado no C77 ("é pra ter por padrão
em todos os vídeos"); o C75, o C76 e o C78 foram refeitos com ela.

```bash
python gera_som.py && python $S/sonoplastia.py .
```

Lê `som.json`, `assets/tempos.json` e `assets/raul.wav`. Escreve `assets/sfx_mix.wav` (a trilha numa faixa só, que o
`index.html` toca por baixo da voz), `renders/som_mix.wav` (voz + efeitos, para o `--mux`) e `som_relatorio.txt`. No fim
roda o `erros_js.mjs` e o `zona_segura.mjs`: o render só sai com os dois ✓.

### Os princípios

1. **A voz é a rainha.** Nunca é processada aqui; tudo se ajusta em volta dela.
2. **Ponto de sincronia.** O instante que importa (o contato do carimbo, o pico do whoosh, o "ching") cai no quadro do
   movimento (seção 7).
3. **Nível-alvo por camada.** Cada som é medido em loudness (filtro K da BS.1770, 50 ms) e posto num nível contra o
   percentil 95 da voz. Nada de "volume no olho": assim o papel mudo do C24 não se repete.
4. **Ducking.** A camada abaixa enquanto o Raul fala e volta nos respiros. A fala é detectada pela loudness de 20 ms da
   voz, com 15 ms de antecipação: sobe em ~10 ms e desce em ~200 ms.
5. **Faixa da inteligibilidade.** As consoantes ficam entre 300 Hz e 4,5 kHz. Durante a fala, os efeitos perdem mais 2 dB
   só nessa faixa (`CARVE`); o grave da batida e o brilho da moeda continuam.
6. **Variação.** Cada deixa tem semente própria, ±1 semitom e ±1 dB. Por quê: repetição idêntica denuncia efeito barato.
7. **Espaço.** Pan pela posição na tela, até ±0,6, para o celular em mono não perder nada; uma sala curta e única cola
   tudo no mesmo lugar. A voz fica no centro, seca.
8. **Paleta do estilo.** Foley físico (papel, madeira, moeda, carimbo de borracha) e o clássico do desenho animado (apito
   de queda, boing, pop, pizzicato). Nada eletrônico (glitch, riser) que não exista na cena; o bipe da maquininha existe.

### As camadas

| Camada | Nível contra a voz | Ducking | Sala | Para quê |
|---|---|---|---|---|
| `destaque` | −4 dB | 1 dB | 0,16 | carimbo, BUM, PLAFT, o ka-ching |
| `acao` | −6 dB | 3 dB | 0,12 | o que acontece: corte, moeda, porta, prensa |
| `transicao` | −9 dB | 4 dB | 0,06 | página virando, quadro entrando, whoosh |
| `miudo` | −10 dB | 2 dB | 0,10 | pop de onomatopeia, bipe, gota |
| `musica` | −11 dB | 4 dB | 0,20 | pizzicato, brilho |
| `textura` | −16 dB | 4 dB | 0,06 | passos, tiques, caneta, rolagem |

O `db` da deixa soma sobre a camada. No C84, os miúdos foram de −2 a −6 e as ações de −3 a −7.

### A proteção da fala

- **Folga de 7 dB:** a cada 10 ms com fala, se os efeitos chegam a menos de 7 dB da voz entre 300 Hz e 4,5 kHz, essa faixa
  deles abaixa o que falta. Se o grave ou o agudo ainda vazam, o efeito inteiro desce o resto. Ataque imediato, volta em
  ~80 ms.
- **Destaque com folga de 3 dB e o grave livre:** é a pancada combinada com a palavra (o carimbo no "delírio", o BUM no
  "buraco").
- **Teto de −3 dB contra a voz, até nos respiros:** nenhum efeito fica mais alto que a fala, nem quando ela para (por
  quadro de 10 ms, volta em ~150 ms).
- **Filtros:** passa-alta em 70 Hz (24 dB por oitava), passa-baixa em 16 kHz e limitador de pico em −9 dBFS.
- **Guarda da mixagem:** se voz + efeitos passam de 0,89 de pico, o `som_mix.wav` desce inteiro; o volume final é do
  `finalizar.py`.

### Os sons

- **Gravado primeiro.** `assets/foley/` desta skill tem quatro pacotes CC0 do Kenney (impact, RPG, casino e interface,
  cada um com o seu `LICENSE.txt`) e a biblioteca do HyperFrames. O script acha a pasta pelo próprio caminho.
- **Síntese só no que é desenho animado** (apito de queda, mola, motor, vapor, bipe, pizzicato) ou para engrossar o
  gravado (subgrave, migalha de casca). Por quê: no teste às cegas de 14/10, objeto sintetizado (moeda, papel, carrinho)
  soou falso.
- **O banco:**
  - composições: `quadro`, `carimbo`, `soco`, `bum`, `plaft`, `corte`, `mordida`, `mastiga`, `moeda`, `moedas`,
    `saco_moedas`, `registradora`, `cofrinho`, `guarda_chuva`, `toc_tecido`, `squish`, `obturador`, `carrinho`, `adesivo`,
    `papelao`, `medalha`, `dun`;
  - síntese: `boing`, `pulo`, `catraca`, `bip`, `bip_erro`, `motor`, `vapor`, `pluck`, `apito`, `globo`, `caneta`
    (`args: {"larga": true}` = marca-texto), `tremor`;
  - gravado simples: cada grupo do `GRUPO` no script (`pagina`, `pousa`, `desliza`, `whoosh`, `pop`, `tique`, `madeira`,
    `metal_leve`, `vidro`, `passo`, `tecla`, `gota`, `brilho`, `notificacao`, `grave` e outros).
- **Ouvir antes de escolher:** `python $S/sonoplastia.py --catalogo <pasta>` grava um `.wav` de cada som.
- **Caderno:** `caneta` (`larga` no marca-texto) em toda escrita e todo traço. **Trecho sensível** (morte, doença): só
  caneta baixa, sem gag.

### Ler o `som_relatorio.txt`

O do C84, aprovado e no ar, é a régua:

```
NÍVEL: voz −18,2 dB · efeitos mediana −44,8 · p90 −37,4 · máx −25,9 dB
  pico: voz −3,6 dBFS · efeitos −9,3 dBFS
  loudness integrada: voz −15,0 · voz + efeitos −14,9 LUFS → no −14 do finalizar a voz desce 0,0 dB
DEIXAS: 130 sons de 32 tipos · miudo 62 · acao 31 · transicao 21 · textura 10 · destaque 6
  por 10 s (sem textura): 12 8 10 10 7 14 7 6 9 9 12 10 6
MASCARAMENTO: 1 palavras abaixo de 10 dB  (124,70 s «do» 8,4 dB)
AUDIBILIDADE: acao 58% · destaque 100% · miudo 55% · textura 50% · transicao 76%
  abafado: 45,84 s pulo acao −33,2 dB …
```

- [ ] **Nível:** o máximo dos efeitos fica bem abaixo da voz (C84: 7,7 dB abaixo), e o pico deles perto de −9 dBFS.
- [ ] **"A voz desce":** até ~0,5 dB. Mais que isso é efeito ou grave demais inflando a loudness.
- [ ] **Densidade:** de 6 a 14 sons por 10 s no papel recortado. Muito efeito pode; trecho mudo perde a imersão.
- [ ] **Mascaramento:** palavra em que a voz fica menos de 10 dB acima dos efeitos. Palavra de ligação ("do", "e") passa.
  Número, nome ou a palavra do soco não: mover a deixa para o respiro ou baixar o `db` dela.
- [ ] **Audibilidade:** a parte das deixas que chega a 6 dB da voz em alguma oitava. O destaque fica em 100%. "Abafado" é
  ação que ninguém ouve: pode ficar como textura, mas, se importa para a história, vai para o respiro. Nunca subir o
  efeito por cima da fala.
- [ ] **O ouvido:** ouvir o `renders/som_mix.wav` de fone: "o efeito aparece por cima da voz?" Se aparece, está alto.
  Quem decide são as medidas e o ouvido do dono do canal. Por quê: no teste de 14/10, o modelo que ouvia o áudio errou
  som gravado ("rolha" para página virando) e "ouviu" efeito que não existia.

## 5. O efeito sempre por baixo da fala

A regra é anterior à sonoplastia nova e continua dentro dela:
- **C24 (05/10):** "estamos exagerando nos efeitos, esse meio transicional, um vruups… pra não ficar mais alto que o som
  da própria fala". O whoosh passava a fala em +2 dB na média (até +6,5), e o carimbo em +5 a +7.
- **C28 (06/10):** "esse som de vento nas transições… tá muito alto… um efeito sonoro mais de fundo mesmo". O whoosh de
  transição caiu 60% (0,4 → 0,16) e o resto ~2 dB ("bem de leve"); pop, clique e carimbo estavam bons.
- **C29 (07/10):** o grave de impacto é CONTÍNUO (2,1 a 2,6 s), não uma batida. No fecho ficou ~6 dB acima de uma frase
  falada baixo, e a transcrição nem pegou a frase. Perto de frase final ou fala baixa, metade do volume. Conferir com
  `highpass=f=250` (a voz) × `lowpass=f=150` (o grave) no vídeo final.
- **C29 e C31:** nada de grave no último segundo: o fim do vídeo corta o grave.
- **C45 (10/10):** 48 cliques a 0,30 passaram por cima da voz. Ficou "muito efeito pode, alto não": −2,5 dB em tudo e
  teto por tipo (miúdo 0,07; carimbo e batida 0,15; riser e rasgo 0,1).

**No padrão novo:**
- [ ] transição na camada `transicao`; whoosh que acompanha a fala com `db` −6 a −8;
- [ ] o teto de −3 dB contra a voz faz o papel dos tetos antigos;
- [ ] `grave`, `bum` e `dun` longe de frase final e de fala baixa, e nunca no último segundo;
- [ ] reclamou da transição de novo? O próximo passo é usar MENOS transições, não só baixar mais.

## 6. O par de transição de cada tela cheia

Cada tela cheia (3 ou mais em vídeo de até 2 min, 4 acima) leva "um efeito sonoro que conduza a passagem sem roubar a
fala" (pedido de 15/10). O padrão do C82 ao C84:

| Momento | Deixa | Camada e `db` |
|---|---|---|
| a folha começa a subir (`t0 − 0,5`; 0,52 s, `power3.out`) | `whoosh` | `transicao`, +1 |
| 0,1 s depois | `pagina` | `transicao`, −1 |
| a folha começa a descer (`t1`; 0,46 s, `power2.in`) | `whoosh` | `transicao`, 0 |

- [ ] **Ancorar o par na MESMA conta do `telaCheia(n, t0, t1)` e do `assets/tela_cheia.json`.** No C84,
  `t0 = T("gente", gancho, 2) − 0,05`: o whoosh vai em `"gente"` com `n=2` e −0,55; a página em −0,45.
- [ ] **Tela cheia sem o par está incompleta**, e par fora do quadro da folha soa como erro.

## 7. Escrever as deixas no `gera_som.py`

Folha escrita à mão, com números, quebra no primeiro corte refeito. O `gera_som.py` do corte (modelo:
`cortes/c84-fortunas/gera_som.py`) gera o `som.json` a partir das MESMAS palavras da cena.

- [ ] **A mesma âncora da cena.** A cena faz `carimba(el, T("herdou", SO) - 0.05)`; a deixa é
  `d("carimbo HERDOU", "herdou", SO, CARIMBO, "carimbo", "destaque")`. O `T(w, bloco, n)` conta a n-ésima ocorrência
  DENTRO do bloco, como o `W()` do motor. Por quê: palavra comum se repete ("com", "e", "vai"), e o `n` errado põe o som
  noutro instante (o C27, o C39 e o C41 erraram assim na animação).
- [ ] **O tempo vai para a folha como `["palavra", desde, desloc]`**, com `desde` = início da palavra − 0,05 s; o
  `sonoplastia.py` acha a 1ª palavra igual a partir de `desde − 0,12`. Com `w=None`, vale o início do bloco + deslocamento.
- [ ] **Copiar o deslocamento da chamada da cena**, somando o atraso só quando o contato vem depois do início. No C84,
  `entra(bm1, T("Brasil", EU) - 0.15)` virou o `pousa` em −0,15, e `entra(p71, T("71%", EU) + 0.3)` o `pop` em +0,3:

  | Movimento na cena | Onde cai o som |
  |---|---|
  | `carimba(el, t)` (0,18 s a partir de `t − 0,12`) | contato em `t + 0,06`; com `t = T − 0,05`, `CARIMBO = 0,01` |
  | `bate()` (cada corte tem o seu) | o fim do tween: `t + 0,04` no gibi do C77 (0,14 s a partir de `t − 0,1`) |
  | `entra(el, t)` (`aparece` de 0,22 s) | o mesmo `t`; o ponto exato é o meio, `t + 0,11` |
  | `aparece()`, `cresce()`, `brotaP()` | o mesmo `t` (`pousa`, `desliza`, `surge`) |
  | `bounce.out` de `d` s | `"quica": d`: um som em cada contato (36, 73, 91 e 100%), com −8, −15 e −21 dB nos quiques |
  | contador ou sequência com `ease` | `"ease": "power2.out", "n": 8, "dur": 1.2`: os tiques seguem a curva |
  | texto que aparece palavra a palavra | `"palavras": [ini, fim]`: um som em cada palavra dita no intervalo |

- [ ] **Campos da deixa:** `som`, `camada`, `pan` (−1 a 1), `db`, `p` (afinação), `varia` (0 tira a variação), `args`,
  `nota`; repetição com `rep` + `passo` (s), `sobe` (semitons por vez) e `pan_ate`; lista de instantes com `em`.
- [ ] **Uma deixa para cada coisa que acontece:** entrada, pouso, carimbo, seta, travelling (no C84, 116 deixas, 130 sons de
  32 tipos). Dois sons no mesmo instante só como camadas do mesmo objeto (o `pop` do "5:00" com os `tique` do despertador).
- [ ] **Depois de TODO `cortar.py` ou `pos_cortar.py`, rodar `gera_som.py` e `sonoplastia.py` de novo.** A folha guarda
  tempos absolutos e envelhece quando o corte muda.

## 8. O `--mux`: trocar o som sem novo render

```bash
npx --yes hyperframes@0.8.99 render . --fps 24 -q standard -w 6 -o renders/etapa3_bruto.mp4
python $S/sonoplastia.py . --mux
python $S/finalizar.py .
```

- [ ] **Depois de todo render, o `--mux`.** Ele guarda a imagem em `renders/etapa3_bruto_imagem.mp4` e regrava o
  `etapa3_bruto.mp4` com ela e o `som_mix.wav` em FLAC. Por quê: o render sai em AAC (~192k no C84); sem o mux, o AAC do
  render e o do `finalizar.py` são duas perdas, e com ele fica uma.
- [ ] **Mexeu só no som?** `gera_som.py`, `sonoplastia.py . --mux` e `finalizar.py`, sem novo render: segundos, contra
  minutos.
- [ ] **A armadilha da imagem velha (C82, 16/10):** o mux de depois de um 2º render usava a imagem do 1º. Agora o script
  decide pelo codec: o render sai em AAC e o mux grava FLAC, então um `etapa3_bruto.mp4` em AAC é render NOVO e substitui
  a imagem guardada. Por isso: nunca renomear nem copiar à mão esses dois arquivos; nunca renderizar com outro nome e
  trazer depois; na dúvida, renderizar de novo. O `finalizar.py` avisa quando o `etapa3_bruto.mp4` ainda está em AAC (o
  mux não rodou).
- [ ] **O som no `index.html`:** o `montar.py` põe uma tag só, `<audio id="sfx-mix" src="assets/sfx_mix.wav"
  data-volume="1">`, apontando para o `raul.wav` com volume 0 enquanto a trilha não existe. O mux troca o áudio do render,
  mas o render com som serve para conferir antes.

A ordem completa dos comandos está no `SKILL.md`, e o que conta como aprovado em cada passo, em
`references/conferencias.md`.
