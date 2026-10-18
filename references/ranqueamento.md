# Ranqueamento das falas e dos cortes

Ler antes de escolher o tema do dia ou o trecho de um vídeo (Etapa 0). O ciclo é: achar candidatos → ler e dar a nota da
régua → anotar a ficha com a previsão → postar → 48 h depois, o placar compara a previsão com o resultado → corrigir a
régua. Cada regra traz, em uma linha, a lição e o corte de onde veio (Cnn = número do corte no histórico do canal).

Por que existe (10/10 e 13/10): até então o tema saía da intuição e da pesquisa de virais, e nada conferia depois se a
escolha tinha dado certo. O pedido foi "ranquear, dar uma nota de 0 a 10 de capacidade de viralização de cada trecho… ir
aprendendo com o tempo o que de fato funciona ou não, eu vou te corrigindo".

## 1. Onde achar candidatos

- **Vídeos novos e longos do Raul:** a fonte principal. Antes de ranquear, olhar as views atuais de cada um.
- **Os posts do próprio canal que mais renderam:** antes de escolher o tema do dia, olhar as views atuais dos posts do canal.
  O tema dos que foram MUITO bem é candidato forte para outro dia, com outro trecho ou outro ângulo (ver a seção 8).
- **Antes de propor um vídeo "novo", conferir no histórico (`LOG_CORTES.md`) se o argumento já foi ao ar.** Canal que
  junta trechos antigos do Raul repete o que já saiu: em 13/10 o "CLT vs PJ" caiu porque repetia o C48 e o C71, e só
  voltou no C81 com trechos que não repetiam nenhum dos dois.
- **Shorts do YouTube e Reels do Instagram dele:** um short com muita view é a prova mais forte de que o trecho funciona
  (13/10: "os shorts são ainda mais validados"). Rerankear o radar junto com os shorts que o dono do canal mandar.
- **Trecho que outra conta de cortes já viralizou e o canal nunca usou:** prova de 1 ponto, desde que a fonte seja o vídeo
  ORIGINAL do Raul. Por quê: o C67 foi escolhido porque o corte de outra conta tinha 714 mil views (o C68, 549 mil), e a
  fonte foi o podcast original, num trecho que o canal nunca tinha usado.
- **O que o dono do canal manda no direct ou pede:** entra no radar com nota como os outros.

**O ranking dos shorts (método, sem API; `python scripts/ranking_shorts.py`, da raiz do projeto, faz os passos 1 a 5 e escreve `_pesquisa/ranking_shorts.md`):**
1. Listar o canal: `yt-dlp --flat-playlist -J https://www.youtube.com/@investidorsardinha/shorts`.
2. **Viralização** de cada short = `log10(views) + 1,5 × log10(views ÷ mediana das views dos 50 vizinhos na lista)`.
   O 2º termo mede o quanto o short furou a bolha da época: o canal cresceu, então 200 mil hoje e 200 mil há dois anos não
   valem igual.
3. **Cópias:** buscar o título no YouTube (`yt-dlp --flat-playlist -J "ytsearch15:<título>"`) e contar vídeos de OUTROS
   canais com título parecido (60% ou mais das palavras em comum). Cada cópia tira 0,35 ponto; mais de 6 conta como 6. Só
   enxerga o YouTube.
4. Tirar os ids já usados (os que aparecem no histórico de cortes, o `LOG_CORTES.md` da raiz do projeto; sem ele, nenhum id sai).
5. **Buscas espaçadas, 1 a cada 8 s, e nunca antes de baixar a fonte do dia.** Por quê (02/10): 160 buscas a cada 2,5 s
   marcaram o IP, e o download da fonte das 19h levou 403 logo depois (só o formato 360p passou).

**O mapa de calor dos comentários (o que pegou dentro do short; `python scripts/analise_shorts.py`, da raiz do projeto, grava `_pesquisa/shorts_analise/relatorio.md`):**
- Baixar a legenda e os comentários com o yt-dlp, sem o vídeo: `--skip-download --write-auto-subs --write-comments
  --extractor-args "youtube:max_comments=300,all,30"` (com as regras de download de `pesquisa-e-download.md`).
- Ligar cada comentário à frase que ele cita ou à qual reage: palavras em comum sem acento, pesadas pela raridade na
  transcrição (no mínimo 2 palavras e soma de raridade 4 ou mais), e números. Cada frase soma 1 + as curtidas de cada
  comentário ligado a ela. As frases mais quentes são candidatas a gancho e a fecho.
- Thread com muita resposta é discussão ou briga (contagem parcial: o yt-dlp traz no máximo 30 respostas por short).
- Ironia, emoji e comentário sobre o Raul (e não sobre a fala) ficam sem frase. **O mapa só aponta onde olhar; quem julga
  é a leitura dos comentários.**
- Sinais por mil views para o "por que" da nota: curtidas/mil e comentários/mil (no radar: 87 curtidas/mil num hit de 331
  mil; 9,25 comentários/mil num veredito contestado; 129 curtidas/mil num short de só 84 mil).

## 2. Ranquear as falas dentro de um vídeo longo

O objetivo é achar 3 ou 4 raciocínios fechados que formem uma linha de história (ver `roteiro.md`), não frases soltas.

1. **Triagem pelo texto, sem baixar o vídeo.** Baixar só a legenda automática do YouTube (`--write-auto-subs --sub-langs
   "pt.*-orig" --skip-download`; a faixa traduzida deu 429, com as regras de download de `pesquisa-e-download.md`) e ler como texto. A legenda VTT traz o
   tempo de cada palavra (`<hh:mm:ss.mmm><c>palavra</c>`): para achar uma frase, normalizar (minúsculas, sem acento, sem pontuação) e procurar a sequência de palavras; o tempo da 1ª
   palavra dá o ponto na fonte (`python scripts/acha_frase.py <arq.vtt> "frase" ...` faz isso). O tempo da legenda serve para localizar, nunca para cortar.
2. **Transcrever os trechos candidatos com o Whisper local**, no tempo absoluto da fonte e com folga nas pontas:
   `npx --yes hyperframes@0.8.99 transcribe <áudio> -e whisper -m large-v3 -l pt --json` (ou `scripts/transcrever_local.py`).
3. **Partir em frases:** pela pontuação, ou por pausa de 0,45 s ou mais entre palavras. Listar `tempo · duração · frase`.
4. **Ler o trecho inteiro e marcar:**
   - os raciocínios: o que é → o que o Raul acha → por quê → o que isso causa (onde começa e onde fecha cada um);
   - os ganchos candidatos: contexto + força em até ~11 palavras;
   - os fechos: frase que é veredito, não explicação;
   - o que derruba: aula ou lista logo depois do gancho, frase com cara de fim no meio, número técnico no meio;
   - o que sai: fala de outra pessoa, propaganda, abertura de live, fala datada, política fora da janela do dia, ofensa.
5. **Sinais que APONTAM uma frase forte** (só apontam; a leitura decide): número absurdo, acusação, contraintuitivo, vilão
   claro (o Estado, o banco, a empresa que engana), "você" (fala com quem assiste), comparação dos dois lados, veredito.
   **Falsos fechos** que derrubam a curva quando caem no meio: "olha que loucura", "esse é o cenário", "acabou", "é isso",
   "falta agora", "que papo de doido", "simples assim".
6. **Dar a nota da régua (seção 3) a cada corte candidato**, não a cada frase: a nota mede o corte inteiro.
7. **Medir as pausas das pontas antes de fechar a escolha.** Frase que emenda sem pausa sai do roteiro ou muda de ponta
   (C48, C49, C67, C68). Varredura rápida das pausas reais de um trecho (−40 dB, 30 ms ou mais; os tempos saem absolutos):

   ```bash
   ffmpeg -hide_banner -i <fonte> -vn -af "atrim=start=812:end=830,silencedetect=noise=-40dB:d=0.03" -f null - 2>&1 | grep silence_
   ```

   - Pausa de menos de ~200 ms entre frases soa colada (C29, 60 ms): a ponta pede respiro ou outra frase.
   - Vale curto (menos de 80 ms) antes de vogal é o fechamento de uma consoante DENTRO da palavra (C09, "tribu|tárias"), não
     uma pausa.
   - O tempo de palavra do Whisper não é prova: ele estica a palavra sobre a pausa e completa palavra cortada (C67). A
     conferência fina de cada ponta está em `corte-e-fala.md`.
8. **Escolher:** a maior nota cujas pontas têm pausa limpa. Dois cortes do mesmo vídeo só com ângulos diferentes (o C83 saiu
   da mesma fonte do C80, com outro ângulo, no mesmo dia).
9. **Vídeo longo demais para uma leitura:** dividir entre leitores com a régua inteira nas instruções e normalizar as notas no
   fim (o mesmo corte não pode valer 8 para um e 6 para outro).

## 3. A régua de viralização (0 a 10)

**Como a nota é dada: LENDO o corte inteiro** (gancho, 2ª frase, meio e fecho). Contar palavra-chave não serve. Por quê: a
régua por palavras do canal de futebol (0 a 100, corte em 80) deu 85 a uma leitura de anúncio e 90 a um debate velho; "a nota
mede vocabulário; só a leitura mede o trecho". Os pesos vêm do placar de 10/10 (37 cortes) e mudam quando o placar mudar.

| item | máx. | 0 | meio | máx. |
|---|---|---|---|---|
| **gancho** | 1,5 | precisa de contexto | 0,5 só apresenta o tema · 1 pergunta forte ou promessa concreta | choque, número absurdo, acusação ou contraintuitivo em até 5 s |
| **segura** | 2,5 | a 2ª frase vira aula ou lista; frase com cara de fim no meio; número ou explicação técnica no meio | 1 a 2 conforme os tropeços | cada frase puxa a próxima e o conflito continua até o fecho |
| **tema** | 2 | — | 0,5 dica de bolso pura, consumo, comportamento · 1 mercado, economia · 1,5 bolso com um vilão claro (banco, golpe, empresa que engana) | o Estado ou o sistema pesando no bolso do povo, com indignação |
| **formato** | 1,5 | — | 0,25 aula ou lista · 0,75 história · 1 revelação ou previsão | indignação ou comparação dos dois lados |
| **prova** | 1,5 | nada, ou o Raul postou e fez menos de 300 mil | 0,5 só o vídeo longo (700 mil+) · 1 outra conta já viralizou o trecho, ou o Raul tem short de 300 mil+ do mesmo ASSUNTO com outro trecho | o Raul postou ESTE trecho (short ou Reel) e passou de 300 mil |
| **fecho** | 1 | fraco, aberto, "é isso" | 0,5 ok | veredito que fecha o raciocínio |

**Descontos:**
- **datado: −2.** Preço, taxa ou regra de uma data que pode ter mudado, "este ano", uma Selic citada, "dito em abril" (C36).
- **repete: −1,5.** O mesmo ÂNGULO postado há menos de 3 dias. Por quê: o C36 depois do C30 e o C29 depois do C21. Não vale
  para o mesmo TEMA com outro trecho e outro ângulo depois de um post que foi muito bem: o C86 repetiu, no dia seguinte, o
  tema do C80 (246 mil em 13 h, o melhor da semana), com outro raciocínio do mesmo vídeo.
- **fonte alheia: −2.** O vídeo de outra conta é a fonte. Por quê: o C39 pagou o pior US$ por mil entre os de boa retenção
  (0,04 por mil no placar de 10/10), mesmo com 41 s de tempo médio. Hipótese: o "original" pesa no programa de recompensas.
- **propaganda: −1.** Propaganda da AUVP, "se inscreve" ou merchan dentro do trecho.

**Decisão:** 7 ou mais, produzir · de 5 a 6,9, só se não houver melhor · abaixo de 5, não produzir.

**Categorias da ficha** (as mesmas do placar; servem para dar o tema, o formato e a prova):

| tema | pontos | formato | pontos | prova (faixa) | pontos |
|---|---|---|---|---|---|
| Estado | 2 | indignação | 1,5 | Raul postou 300 mil+ | 1,5 |
| eleição | 1,5 | comparação | 1,5 | outra conta postou | 1 |
| bolso com vilão | 1,5 | revelação | 1 | vídeo longo do Raul | 0,5 |
| mercado, pessoa, lógica | 1 | previsão | 1 | sem prova, Raul postou <300 mil | 0 |
| bolso, bets, sociedade | 0,5 | história | 0,75 | vídeo de outra conta (fonte) | 0 |
| | | aula | 0,25 | | |

**O que o placar já ensinou (para dar cada item):**
- **Gancho:** já funciona em quase todos (63% a 71% ficam aos 3 s). Por isso "segura" pesa mais.
- **Segura:** os hits seguram 52% ou mais aos 10 s e 38% ou mais aos 30 s; os fracos caem para ~40% e ~27%. Onde se perde
  gente: a 2ª frase que vira aula ou lista (−15% a −20% em 3 s: C32, C30, C12); a frase com cara de fim no meio (−20%:
  "Olha que loucura" aos 92 s do C44; "Falta agora o trabalho", C25; "esse é o cenário", C30); número ou explicação técnica
  no meio (o ticket do C22, a inflação do C32, os 98 milhões do C26, o 1 bilhão do C20).
- **Tema:** o Estado pesando no bolso é o que mais paga (US$ 0,34 por mil); eleição dá mais views (120 mil em 24 h); bolso puro
  fica em 19 mil em 24 h e paga 0,09.
- **Formato:** comparação dá mais views; indignação paga mais; aula segura 26 s e faz ~21 mil.
- **Prova:** com o trecho postado pelo Raul e passando de 300 mil, a mediana é 96 mil em 24 h e US$ 0,32 por mil; sem prova,
  ~19 mil. A prova 1,5 é só para ESTE trecho; um short do mesmo assunto com outro trecho vale 1.

## 4. O radar

Cada candidato vai para `_pesquisa/radar.json` com o valor de cada item; o `scripts/nota_viral.py` soma, ordena e escreve o
`RADAR.md`. A conta é dele; a nota de cada item é sua, lendo.

```json
{"_como": "…", "candidatos": [
 {"id": "BBM8-motoboy", "titulo": "9 horas por dia e não tem carne em casa", "video": "BBM8hyc2uPY (short 2:59)",
  "dur": "~1:45", "gancho": "<frase exata do gancho>", "fecho": "<frase exata do fecho>",
  "criterios": {"gancho": 1.5, "segura": 2, "tema": 2, "formato": 1.5, "prova": 1.5, "fecho": 1, "datado": false},
  "por_que": "O próprio trecho fez 331 mil, com 87 curtidas/mil e 6 comentários/mil… Sai o bloco do R$ 1 milhão (Selic, datado).",
  "data": "2026-10-13"}
]}
```

- **`por_que`** traz a evidência: views do trecho, curtidas e comentários por mil, o que os comentários dizem, o que derruba
  "segura" (quantos segundos de conta no meio), o risco (politiza, fato contestado, vendedor com voz e imagem) e o que sairia.
- **Comandos** (da pasta do projeto; `--raiz <pasta>` para rodar de fora):
  - `python scripts/nota_viral.py` — soma tudo e escreve o `RADAR.md` (cria o `radar.json` vazio se não houver);
  - `python scripts/nota_viral.py usar <id> <Cxx>` — o candidato virou o corte Cxx: a nota e os itens vão para a ficha;
  - `python scripts/nota_viral.py corrigir <id> <nota> "motivo"` — a correção do dono do canal (seção 7).
- O script para com erro quando um item sai da faixa (ex.: gancho 3, se o máximo é 1,5) ou quando o id não está no radar.

## 5. A ficha e a previsão (antes de postar)

Todo tema proposto leva uma ficha em `_pesquisa/fichas.json`, uma por corte, preenchida ao propor o tema, ANTES do roteiro.

| campo | o que é |
|---|---|
| `legenda` | trecho da legenda do post (é o que acha o vídeo no Studio) |
| `titulo`, `tema`, `formato` | categorias da seção 3 |
| `prova`, `prova_de` | as views da prova e de onde ela vem (`raul`, `raul longo`, `outra conta`) |
| `outros_falam`, `repete`, `datado`, `fonte_alheia` | verdadeiro ou falso |
| `previsao_24h`, `previsao_tma` | views nas primeiras 24 h e tempo médio assistido (s), anotados ANTES de postar |
| `nota`, `nota_criterios`, `radar` | vêm do `nota_viral.py usar` |
| `obs` | fonte, horário, estilo |
| `licao` | escrita 48 h depois (seção 6) |

- **Nunca dar nota nem previsão depois de ver o resultado.** Por quê: as fichas antigas só ganharam nota a partir do C48;
  antes disso seria nota dada sabendo o resultado.
- **Previsão de 24 h:** partir da mediana do grupo no último placar (seção 9) e ajustar pela nota. Ex.: trecho que o Raul
  postou com 300 mil+ → perto de 96 mil; sem prova → perto de 19 mil.
- **Previsão de tempo médio:** a do grupo de tempo médio parecido (aula ~26 s; hits 44 s ou mais).

## 6. O placar, 48 h depois de cada post

**Por que 48 h:** o dia da recompensa vai das 21h às 21h (horário de Brasília, que é o dia em UTC), e o valor do dia D aparece
no Studio em D+1. Um vídeo das 19h paga as 2 primeiras horas no dia em que saiu e a noite boa no seguinte. Com 48 h, o 1º dia
inteiro já foi pago.

**O que ler na página de análise de cada vídeo no TikTok Studio** (quem entra na conta é o dono do canal; nunca digitar
senha): views totais, views em 24 h, tempo médio assistido, % que assistiu até o fim, a curva de retenção nos segundos 3, 10 e
30, compartilhamentos e salvos por mil views, novos seguidores e a recompensa (US$). Anotar na própria ficha (`v24`, `tma`,
`r3`, `r10`, `r30`, `fim`, `comp`, `salv`, `seg`, `us`, `usmil`).

**O que comparar:**
- [ ] **24 h × previsão:** o erro em % (ex.: 50 mil previstos, 41 mil reais = −18%).
- [ ] **Tempo médio × previsão;** 44 s ou mais é hit, abaixo de 30 s paga pouco.
- [ ] **Retenção:** 52%+ aos 10 s e 38%+ aos 30 s é curva de hit. Onde a curva cai, achar a frase daquele segundo na
  montagem (o segundo da curva ↔ a palavra no `dados.js`/transcrição da montagem) e dizer por quê.
- [ ] **US$ por mil** (só com 48 h ou mais).
- [ ] **Agrupado** por tema, formato, prova, horário e faixa de tempo médio: mediana de views, de 24 h, de tempo médio, de
  retenção aos 30 s e o US$ por mil do grupo (soma do US$ ÷ soma das views, só vídeos com 48 h+).
- [ ] **A régua × o resultado:** correlação de postos (Spearman, −1 a +1) da nota com 24 h, tempo médio, retenção aos 30 s e US$
  por mil. Acima de +0,3, a régua acompanha o resultado. Só com 4 cortes ou mais.
- [ ] **Escrever a `licao` na ficha:** o que a previsão errou e por quê (uma frase).

**A conta, sem ferramenta especial** (Python 3.10+, só biblioteca padrão; lê as fichas com os resultados anotados):

```python
import json, statistics as st
F = {k: v for k, v in json.load(open("_pesquisa/fichas.json", encoding="utf-8")).items() if not k.startswith("_")}
rk = lambda v: [sorted(v).index(x) + 1 for x in v]  # postos (empate fica com o menor)
for y in ("v24", "tma", "r30", "usmil"):
    xs = [(f["nota"], f[y]) for f in F.values() if f.get("nota") is not None and f.get(y) is not None]
    print("nota ×", y, "%+.2f" % st.correlation(*map(rk, zip(*xs))) if len(xs) >= 4 else "–", "(n=%d)" % len(xs))
for g in ("tema", "formato"):
    G = {}
    [G.setdefault(f.get(g), []).append(f["v24"]) for f in F.values() if f.get("v24")]
    print(g, {k: st.median(v) for k, v in sorted(G.items(), key=lambda kv: -st.median(kv[1]))})
```

**Para os cortes antigos sem nota**, medir a parte da régua que a ficha tem: tema + formato + prova − descontos (máx. 5). Em
13/10, nos 25 cortes antigos, essa parcial deu +0,35 com as views em 24 h, +0,40 com o tempo médio, +0,44 com a retenção aos
30 s e +0,30 com o US$ por mil.

**Pegadinhas dos números:**
- A série de views por hora/dia do Studio conta ~15% a mais que o total; para medir as 24 h, escalar a série para o total.
- "Views qualificadas" não é corte, é atraso: o Studio só conta as dos dias de recompensa já fechados (até 21h).
- Para somar a previsão de vários vídeos, usar a média ou a ponderada, nunca a mediana (a mediana deixou um dia 8% baixo).
- **Estilo ou formato novo só se compara no MESMO dia.** Por quê: a taxa da conta inteira caiu de ~0,30 para ~0,04 US$ por mil
  entre 06 e 14/10, em todos os vídeos, inclusive os velhos. O RPM acompanhou a data de postagem (r = −0,82) e não o tema
  (r = 0,00), e nenhum vídeo estava punido: era um fator da conta. Comparar dias diferentes mistura essa queda com o efeito
  do estilo.
- **Em 15/10 a taxa do mesmo vídeo parou de cair** (×0,89 de um dia para o outro; antes, ×0,78). A queda do total
  veio das views saindo dos vídeos antigos, que pagavam mais por mil, para os posts novos. Ao comparar dias, separar o efeito
  da taxa do efeito da distribuição das views.

**Por que o `placar.py` não veio para a skill:** ele lê a coleta do TikTok Studio feita por um script de navegador com a sessão
logada do PC original (páginas internas do Studio). Sem essa coleta ele não roda. O método acima faz a mesma comparação com os
números lidos à mão, ou com qualquer coleta que grave os mesmos campos na ficha.

## 7. Corrigir a régua

1. **Correção do dono do canal:** `python scripts/nota_viral.py corrigir <id> <nota> "motivo"` guarda a nota e as palavras dele
   no candidato e acrescenta uma linha no `REGUA.md` do projeto. **Ler o `REGUA.md` antes de dar qualquer nota:** cada correção
   vale mais que a tabela da seção 3.
2. **Correção pelo placar:** quando um item erra de forma repetida (ex.: prova alta e views baixas em 4 ou mais cortes), mudar o
   peso ou a definição na tabela da seção 3 com a data e a evidência, e mudar o `MAX`/`DESCONTO` no topo do `nota_viral.py`
   junto. A régua só muda com o placar, nunca com um caso só.
3. **Regras que já vieram de correção (13/10):** "os shorts são ainda mais validados" (prova pesa a favor do short do próprio
   trecho) e a prova 1,5 só para ESTE trecho.

## 8. A grade de horários

- **Desde 15/10: 3 posts por dia, às 7h, 12h e 19h.** O melhor da régua vai às 19h, o 2º às 12h, e o pedido do dono do canal
  (ou o 3º) às 7h. Por quê: "vamos postar apenas 3 vídeos por dia… vamos tirar o vídeo das 15h".
- **Vaga sem vídeo fica vazia.** Nunca juntar posts para preencher.
- **A noite leva o tema mais forte do país.** Por quê: no placar de 13/10, a noite (18–22h) tem a maior mediana (98 mil em 24 h);
  o almoço (11–13h), 20 mil; a manhã (6–10h), 25 mil. O tema pesa mais que a hora: um dia fraco cai em todos os horários.
- **7h, e não 8h** (07/10): o 1º horário tem mais gente online às 7h.
- **O empurrão de cada post dura de 5 a 14 h;** com 3 a 4 h de intervalo um post não come o do outro.
- **1 post por hora não funciona** (11/10): os posts das 14h às 18h ficaram em ~1/3 da mediana de views na mesma idade, com tempo
  médio de 13 a 18 s.
- **No mesmo dia, os 3 posts têm assuntos diferentes** (ex.: 18/10, privilégio às 7h, a história do dinheiro às 12h, política
  às 19h). Tema que foi MUITO bem pode voltar em OUTRO dia (17/10: "tema que foi bem pode repetir entre os dias… vídeo que
  foi muuuuito bem pode repetir o tema sim no outro dia").
- **Dica de bolso nunca vai às 19h:** a noite leva o tema mais forte do país. O horário leve é o almoço (12h), o mais fraco
  do placar.
- O mesmo corte vai às três redes no mesmo horário, com o mesmo "pode agendar" (ver "Como entregar" no `SKILL.md`).

## 9. Lições de desempenho

**O tom: economia do país × dica de bolso.** Em 05/10: C17 "E se o Flávio ganhar?" 3,8 mi; C18 689 mil; C16 245 mil; C04
186 mil; C09 125 mil; lógica de debate (C19) 92 mil. Dica de bolso (C06 dívida, C01 caneta, C08 FGC): de 6 a 19 mil. O
público veio pela análise do Brasil; finanças pessoais não seguram esse público.

**O placar de 13/10 (40 cortes), por grupo:**

| grupo | views (mediana) | 24 h (mediana) | tempo médio | ficam aos 30 s | US$/mil |
|---|---|---|---|---|---|
| tema eleição (16) | 150 mil | 120 mil | 34 s | 34% | 0,18 |
| tema Estado (10) | 51 mil | 38 mil | 39 s | 37% | 0,34 |
| tema mercado (3) | 27 mil | 47 mil | 36 s | 32% | 0,29 |
| tema bolso (5) | 33 mil | 19 mil | 25 s | 26% | 0,09 |
| formato comparação (11) | 149 mil | 71 mil | 34 s | 37% | 0,23 |
| formato indignação (13) | 56 mil | 30 mil | 38 s | 35% | 0,34 |
| formato aula (11) | 54 mil | 25 mil | 26 s | 28% | 0,14 |
| tempo médio 44 s+ (3) | 342 mil | 290 mil | 46 s | 40% | 0,34 |
| tempo médio até 29 s (11) | 22 mil | 17 mil | 26 s | 26% | 0,11 |

- **Tempo médio manda no dinheiro:** em 10/10, os 4 vídeos de 44 s ou mais fizeram US$ 450 dos ~600; abaixo de 30 s pagou 0,11
  por mil.
- **Política não se penaliza** (06/10): paga menos por view, mas um viral de milhões rende muito igual. "Dinheiro do povo" paga
  mais por view; os dois entram na grade.

**Estilos de animação (1º dia, 14/10, no mesmo dia):**
- C75 em quadrinhos FLOPOU: 4,2 mil views e 16 s de tempo médio (14% assistido).
- C76 em caderno: 54 mil, US$ 0,046 por mil, 25 s (29%).
- C73 papel recortado: 29 mil, 0,033, 43% assistido. C72 papel novo: 49 mil, 0,045, 31%.
- O cordel ficou "com pouca informação na tela" num vídeo de muita conta (C75).
- Resultado: em 16/10 voltou o papel recortado padrão, com a animação tomando a tela inteira 3 ou 4 vezes por vídeo.

**O que derruba a retenção** (cada item já custou views):
- [ ] a 2ª frase que vira aula ou lista (−15% a −20% em 3 s);
- [ ] a frase com cara de fim no meio (−20%);
- [ ] número ou explicação técnica no meio;
- [ ] o apresentador falando de fato, mesmo 5 ou 6 s (−5% a −10% a cada vez, C40);
- [ ] a pergunta de quem entrevista na frente do gancho sem necessidade (C68);
- [ ] o formato solo e repetitivo (o Giro da Bolsa de hora em hora: 13 a 18 s de tempo médio);
- [ ] a legenda que some no gancho (C49: a fala virou texto espalhado na cena, e não funcionou);
- [ ] o quadro parado do Raul com a fala andando (parece vídeo travado: C25, C42, C44).

**O que não se propõe:** vídeo de outra conta como fonte, o mesmo ângulo em menos de 3 dias, o argumento que já foi ao ar,
dois posts do mesmo assunto no mesmo dia, fala datada sem a data, e tema que a janela do momento fechou (ver `roteiro.md`,
seção 10). O mesmo TEMA em outro dia, com outro ângulo, pode, quando o post anterior foi muito bem.

## Checklist do dia

- [ ] O `REGUA.md` (correções) foi lido antes de dar nota.
- [ ] Cada candidato tem os 6 itens, os descontos e o `por_que` com evidência; o `RADAR.md` foi gerado.
- [ ] As pontas dos candidatos do topo têm pausa limpa.
- [ ] A ficha de cada corte escolhido tem a nota (`usar`) e a previsão de 24 h e de tempo médio, anotadas antes de postar.
- [ ] A grade: a melhor nota às 19h, a 2ª às 12h, o pedido ou a 3ª às 7h; vaga sem vídeo fica vazia.
- [ ] Os 3 do dia têm assuntos diferentes, e nenhum repete um argumento que já foi ao ar.
- [ ] 48 h depois de cada post: resultado anotado, comparação feita, `licao` escrita, régua conferida.
