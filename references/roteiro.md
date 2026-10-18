# Roteiro do corte

Ler antes de escrever qualquer roteiro (Etapa 1, que termina na ✋ aprovação 1): bloco que sai depois de animado é
trabalho jogado fora. Cada regra traz a lição e o corte de onde veio (Cnn = número do corte no histórico do canal). O
roteiro vai na conversa, para o dono do canal aprovar, e em `cortes/<slug>/ROTEIRO.md`, com o mesmo conteúdo.

## 1. O que vira corte

**A promessa:** cada corte entrega UMA coisa que muda como a pessoa enxerga o dinheiro e o país. É uma informação que
ela entende de primeira e quer mandar para alguém.

Um trecho só vira corte quando passa nos quatro testes:
- [ ] **Tem a frase de gancho**, dita pelo Raul: ela contextualiza o tema e é a mais forte do trecho.
- [ ] **Tem o que mostrar:** um número, um mecanismo ou uma cadeia de causa e efeito que a metade de cima transforma em imagem.
- [ ] **Provoca vontade de compartilhar:** "não sabia disso", "que absurdo", "vou mandar pra fulano".
- [ ] **Fecha em sentença:** a última fala é o soco, nunca uma explicação pela metade.

**Fica de fora sempre:**
- abertura de live ("hoje a gente vai"), perguntas do chat e "se inscreve";
- propaganda da AUVP ou de qualquer produto, dentro ou no fim do trecho;
- política que pede voto ou ofende alguém (ver a seção 10);
- **a vida pessoal do Raul:** o corte é para quem NÃO o conhece (C12: "quem não é público dele talvez nem conheça"). A
  experiência dele só fica quando é a porta de entrada do tema (C82: "minha vida era detestável quando eu trabalhava na 6x1");
- **a autopromoção e o público do canal** (C26: "não faz parte do roteiro essa autopromoção"). O fecho é sobre o tema.

## 2. Fonte e texto de partida (sem API)

- **Vídeo longo do Raul:** a fonte principal; o corte pode juntar trechos de pontos diferentes dele.
- **Short ou Reel dele:** só o material daquele vídeo, na ordem que quiser, mesmo mais curto que o original (02/10). Menos
  de 1 min não monetiza (C10 e C11 ficaram fora da agenda). No C24, uma frase do original entrou para passar de 1 min: é
  exceção, combinar antes.
- **Vídeo de outra conta como fonte:** evitar e achar o original (C39 pagou o pior US$ por mil; ver `ranqueamento.md`).
- **Transcrever com o Whisper local**, sempre no tempo absoluto da FONTE, nunca no clipe cortado:
  `npx --yes hyperframes@0.8.99 transcribe <fonte> -e whisper -m large-v3 -l pt --json` (ou `scripts/transcrever_local.py`).
- **O texto do roteiro é a transcrição conferida no ouvido**, palavra por palavra. Por quê: no C29, o large-v3 pôs o "Mas"
  1,4 s antes do real e escreveu "Já ganhei" no lugar de "Joga aí". O tempo fino das pontas vem do alinhador e do envelope
  (`corte-e-fala.md`), nunca do Whisper.

## 3. O raciocínio completo, nunca uma colagem de frases

**A lição (C03 e C05, 03/10):** foram escolhidas FRASES de impacto em vez de RACIOCÍNIOS; cada tema virou pedaços de 2 a
5 s ("cortou e já iniciou outro assunto e perdeu o contexto"). Os defeitos reais:

| Defeito | O que foi ao ar | O que faltou |
|---|---|---|
| Começa no meio da frase, sem sujeito | "…poderiam voltar imediatamente ao benefício" | QUEM poderia voltar |
| Uma ideia picada em fragmentos | três blocos em 10 s sobre um jantar | o "em agosto, na Faria Lima" que abre a ideia |
| Conclusão sem a premissa | "não é um plano repetível" | que venda de estatal é receita de uma vez só |
| Resposta sem a pergunta | "a resposta foi evasiva" | o que perguntaram |
| Fala de outro na boca do Raul | frases do candidato soando como opinião do Raul | o "ele chegou a dizer que…", o "abre aspas" |
| Elo cortado entre dois temas | aposentadoria → "professores não teriam reajuste" | os pisos de saúde e educação, que ligam um ao outro |
| "Mas" que leva a outro raciocínio | "tem coisas sensatas, mas, esses anos seriam instáveis" | o "tudo ao mesmo tempo", que é o motivo |
| Tema demais | 10 itens em 3:50; 8 temas em 2:00 | tempo para cada ideia fechar |

**As regras:**
1. **A unidade é o RACIOCÍNIO.** Um raciocínio tem: o que é (a proposta, o fato) → o que o Raul acha → por quê → o que
   isso causa. Ele entra INTEIRO. Dentro dele só sai o que não muda o sentido: muleta, repetição, piada lateral, palavrão.
   Nunca a premissa nem a conclusão.
2. **Poucos temas, cada um fechado.** Em 2 minutos cabem 3 ou 4 raciocínios de 15 a 40 s. Cortar um tema inteiro é melhor
   do que deixar três pela metade.
3. **Linha da história.** Os temas se encadeiam (cada um responde ou agrava o anterior) e o fecho é a CONCLUSÃO dessa linha,
   não uma frase forte qualquer. Escrever a linha em uma frase ANTES de escolher os trechos.
4. **O funil de atenção:** aos 5 s a pessoa sabe do que é o vídeo e já recebeu a informação mais forte; aos 15 s chega o
   primeiro "uau"; aos 45 s um raciocínio completo já foi entregue e o próximo está prometido.
5. **Quem fala:** fala de candidato ou documento lido pelo Raul leva o "ele disse", "o plano diz", "abre aspas".
6. **Ponta de bloco:** não começa em palavra que depende da anterior (pronome sem dono, "poderiam", "porque", "então", "mas")
   e não termina em conectivo nem no meio de lista. Termina onde a ideia fecha.
7. **Teste da leitura (obrigatório antes de mostrar):** ler SÓ o texto que vai ao ar, de ponta a ponta, em voz alta. Em cada
   bloco, quem nunca viu o vídeo longo responderia "quem?", "do quê?" e "por quê?"? Se perguntaria, o bloco está quebrado.

## 4. O gancho dos primeiros 5 s

- **É a frase que contextualiza o tema E é a mais forte**, mesmo vinda do meio ou do fim do vídeo (C21 e C22: o fecho virou
  o gancho; C49: a "legítima defesa").
- **Curta:** até ~11 palavras, cabe em 3 s, nomeia o assunto e abre uma pergunta que só o vídeo responde.
- **Direta, nada de enigma.** Por quê: no C09 o gancho do cozinheiro saiu ("enigmático, poético demais") e a metáfora foi
  para depois; no C44 o "Pô, é uma merda…" saiu porque não dizia o tema.
- **O fato com que o espectador se identifica, não a tese abstrata.** Por quê: no C26 venceu "boa parte da população
  brasileira ganha um salário mínimo", e não "quando a gente pega o Brasil e olha a renda…".
- **Sem pergunta retórica na frente do fato.** Por quê: no C47 saiu o "Você repara que eles terminaram presos?"; o vídeo abre
  em "Os últimos presidentes…".
- **Os 20 primeiros segundos levam o material mais forte, sempre completo:** quem passa dos 20 s tende a ver 70% ou mais
  (02/10; no C26, "esses primeiros 15 segundos são muito importantes"). O gancho já segura 63% a 71% aos 3 s em quase
  todos; o que separa os hits é o que vem depois (seção 5).
- **Quando a frase forte depende do que vem antes, a ordem da fala fica.** Por quê: no C58, puxar o "30 milhões" para o
  começo deixaria o "Mas tem outro ponto também" sem sentido; o bloco foi na ordem da fala, com o gancho aos 8 s.

**A pergunta no início (regra corrigida em 12/10, C68):**
- O padrão é ir DIRETO ao gancho, a fala mais forte do Raul. Cada segundo antes dele perde gente.
- A pergunta de quem entrevista só abre o corte quando a resposta não se entende sem ela: no C51, o "mito do Nordeste
  pobre" só faz sentido depois da pergunta do aluno (7 s, no cartão escuro). Nos C62 a C66 isso virou regra geral, e foi
  erro: "tem muita gente que nem fica para a resposta".
- Interjeição do apresentador no meio ("Por que está assim, cara?") também sai (C68).

## 5. A ordem dos blocos: pela retenção

**A regra (C68, 12/10):** "As falas mais fortes têm que estar no início. O final também é bom ter uma fala forte… mas é mais
relevante esse início ser bom." No C68, o fecho foi para logo depois do gancho e a explicação técnica, para o fim.

- **Ordem:** gancho → o bloco mais forte (indignação, frase de print) → os exemplos concretos e engraçados → a explicação
  técnica por último → um fim que também fecha forte.
- **A linha da história vale DENTRO de cada bloco** (seção 3); a ordem ENTRE os blocos segue a força.
- **A 2ª frase nunca vira aula ou lista:** logo depois do gancho, ela perdeu de 15% a 20% em 3 s (C32, C30, C12).
- **Nada de frase com cara de fim no meio:** "Olha que loucura", aos 92 s do C44, perdeu 20% (também C25 e C30).
- **Nada de número ou explicação técnica no meio** (C20, C22, C26, C32). Número que é o choque vai no gancho; número de
  apoio sai ou vai para o fim.
- **Ordem dada pelo dono do canal se segue à risca:** mudar só o pedido, "o restante exatamente como está" (C03); uma adição
  aceita entra onde não mexe na ordem dele (no C26, encaixar os 98 milhões "trocou a ordem inteira"). Explicar o porquê de
  cada corte e ordem: ele quer aprender e decidir junto.
- **Mudou a ordem, mudam também:** a capa (no C46 ela "não retratava o vídeo" depois que o gancho saiu), os capítulos e
  carimbos, e as emendas novas, que se medem de novo (`corte-e-fala.md`).

## 6. Duração

- **De 1 a 2 minutos.** Abaixo de 1 min o programa de recompensas do TikTok não paga (o canal foi monetizado em 05/10).
  Passe de 1:00 com folga (1:05 ou mais), acrescentando mais um raciocínio completo, nunca enchimento.
- **De preferência de 1:30 a 2:00, quando o conteúdo sustenta** (06/10), sem penalizar um 1:0x bom.
- **2 minutos é teto, não meta:** nada de ocupar os 2 minutos (no C09, o vídeo caiu de 1:56 para cerca de 1 min). Só entra
  o importante, o popular e o viralizável. Menos de 1 min, só com short ou Reel curto que entra inteiro.
- **Acima de 2 min, só quando a história segura** (C28 2:05, C84 2:05, C82 2:59). O que muda: 4 telas cheias em vez de 3
  (seção 7), e o risco diz quem sai primeiro se precisar encurtar (no C82, os blocos 7 e 5; o dono do canal ainda tirou o
  ciclo do dia para "chegar mais rápido no que muda"). Quase 4 minutos é demais (C02 e C03).

## 7. Telas cheias: o roteiro já nasce com elas

Padrão desde 16/10: a animação toma a TELA INTEIRA (o Raul some, a voz continua e a legenda fica).
- **Até 2 min: 3 vezes ou mais. Acima de 2 min: 4 vezes.** Cada uma com 5 s ou mais.
- **A 1ª logo depois do gancho;** as outras se espalham, sem colar uma na outra e sem cair no fim.
- **Caem em falas visuais** (exemplo concreto, número, cena), nunca no momento que depende do rosto do Raul.
- **Foto ou gráfico em tela inteira na fonte (o Raul some) vai para debaixo de uma tela cheia** (no C84, uma tela cheia
  mudou de bloco para cobrir duas fotos da fonte).
- No roteiro, marcar cada uma com o tempo aproximado e o que aparece: `TELA CHEIA 2 (≈0:30–0:38): …`. Por quê: o teste de
  15/10 virou padrão no C82 ("pelo menos três vezes, de pelo menos cinco segundos cada").

## 8. O texto completo por bloco e a lista do que sai

- **Cada bloco vem com o texto integral do que vai ao ar**, palavra por palavra, sem "…" e sem resumo. Por quê (C04):
  "odeio quando vc esconde palavras"; só no vídeo ele viu que um raciocínio tinha sido cortado no meio. Ele aprova lendo.
- **Os blocos mostram só o que vai ao ar**, na ordem do vídeo, sem [SAI] no meio (C48: "não entendi… faz o roteiro sem isso
  de [SAI]").
- **O que sai vai numa lista à parte, no fim ("Fica de fora")**, cada item com o texto, o tempo na fonte e o motivo
  (repete, política, propaganda, sem pausa limpa, datado, levaria o vídeo a 2:12…).
- **Palavrão no texto do roteiro já vai censurado** (P***A, C*****O), como vai na legenda.
- **Nada de editar antes do "ok" no texto completo.**

## 9. Alternativas, arco, por que compartilha e risco

- **Alternativas de abertura:** no mínimo 3, cada uma com o motivo de cair ou de vencer. No C82, "quem vai pagar por essas 4
  horas?" caiu (abre na conta e afasta quem é a favor) e venceu "minha vida era detestável quando eu trabalhava na 6x1" (quem
  está na 6x1 se vê nela, e prende os dois lados).
- **Arco:** o que abre, o que sustenta e o que fecha. O fecho é uma SENTENÇA, nunca explicação. Pode vir numa linha só, como
  a "linha da história" do C84.
- **Por que compartilha:** a reação e quem manda para quem (no C82, o trabalhador se vê no ciclo do dia e o pequeno
  empresário se vê na conta).
- **Risco:** o que pode derrubar e o que foi feito: política na janela errada, palavrão, fato contestado, fala datada,
  apresentador demais, duração, emenda sem pausa.
- **Capa:** manchete de 2 a 3 linhas com a mesma ideia do gancho, o Raul de olhos abertos e sem selo de nome; ela não acusa
  (seção 10) e muda quando o gancho muda (seção 5).

## 10. Tom, política, janelas do canal e palavrão

**O tom é a economia do PAÍS:** governo, Estado, imposto, mercado, eleição e o que isso causa no povo. Por quê: em 05/10 o C22
(dicas de consumo) saiu da noite ("pra tentar manter nosso tom"); os de país foram de 100 mil a milhões (C17: 3,8 mi), os de
dica de bolso ficaram entre 6 e 19 mil. Dica de bolso só em horário leve, de vez em quando (números em `ranqueamento.md`).

**Política entra como opinião e análise** (04/10, 1º turno: "nada do que postamos é propaganda, é opinião e análise"). A lei
proíbe propaganda nova no dia da votação; a opinião é livre, com dois limites: ofensa à honra e fato sabidamente falso. A
decisão de risco é do dono do canal: informar uma vez, com fonte, e executar.
- [ ] Sem pedido de voto; os candidatos por igual, ou é a análise do Raul (C09, C13 a C16).
- [ ] Sem ofensa e sem piada sobre escândalo: saíram o "esse velho de novo" (C50), o xingamento direto (C39) e a palavra que
  pode ser mal interpretada, o "Chupetinha" (C37).
- [ ] Nada que soe como desculpa para o lado errado (a creolina, C40) e nada de região contra região (C51).
- [ ] Acusação só no condicional e com a negação junto (C58: TERIA PAGO, SUPOSTO, a manchete da PF negando). Acusação sem nome
  sai, e a opinião ganha a etiqueta NA OPINIÃO DO RAUL (C60).
- [ ] Capa não acusa: o "ROUBOU?" ao lado do rosto lê-se como acusação (C37); a capa do placar não pende para lado nenhum (C30).
- [ ] Nunca impulsionar post político. Perto do resultado, o menos partidário (sem "se fulano ganhar").
- [ ] Opinião do Raul sobre terceiros fora do tema sai (C84: a crítica ao family office do Safra).

**As janelas que o canal adotou** (confirmar com o dono do canal qual vale hoje):
- **Outubro de 2026, até o 2º turno (25/10): política e Brasil;** casa, investimento e consumo esperam (08/10). Por quê:
  política e Estado × povo passaram de 100 mil quase sempre; casa, investimento e consumo ficaram entre 8 e 107 mil. O C34
  (investimento) saiu da agenda, e o "caminho e ordem… investir" saiu do fim do C84. Depois de 25/10, perguntar.
- **O pedido do dia vale mais que a regra de fundo** (13/10: ele mesmo pediu um dia de vídeos de bolso).
- **Pausa de política de 14 a 18/10 (teste do RPM):** saem nomes de candidatos, partidos, "esquerda/direita", votações e
  recados a candidatos; fica a crítica aos políticos em geral (C82: "isso não gera voto"). No C84, o "pessoal mais de esquerda
  dos bancos" saiu por isso. Depois, comparar o US$ por mil com o de 09 a 12/10 e perguntar se a pausa continua.

**Palavrão:** o áudio pode ter; o texto nunca. Legenda, legenda do post, etiqueta, carimbo e capa levam a 1ª letra,
asteriscos e a última: F**A, P***A, M***A, C*****O, P*U, F**A-SE (parte no hífen). Por quê (C27): palavrão por extenso faz o
TikTok restringir o alcance. Palavrão que só serve de muleta pode sair do raciocínio.

## 11. Fatos e atribuição

- **Conferir o número e o fato que o Raul afirma.** Fato errado sai, mesmo forte (no C51 saiu "o PIB de vários estados do
  Nordeste é maior que o de Goiás": só a Bahia passa).
- **Fato contestado vai no risco** (no "não tem mais gasolina no Brasil", a ANP contesta o dano ao motor).
- **Fala datada leva a data na tela ou sai** (C36: a etiqueta DITO EM ABRIL); uma Selic citada perde nota na régua.
- **Sem afirmar além da fala:** a animação e a capa não dizem o que o Raul não disse.

## 12. Quem fala (podcast e mesa)

- **Marcar no roteiro toda fala que não é do Raul**, principalmente fecho ou frase forte. Por quê: no C27, o "não tem político
  que pode indicar" era do apresentador, e saiu.
- **O mínimo de apresentador.** Por quê (C40): toda vez que ele fala de fato, mesmo 5 ou 6 s, saem de 5% a 10% das pessoas.
  Fica só o "bate e volta" rápido (uma pergunta curta, um "sim"); fica também a fala dele que dá um bom gancho para o Raul
  ("tem que fazer sentido"). Na ponta do bloco, preferir onde o close dele não aparece.
- **Interjeição de menos de 1 s:** sai se a transcrição não pega (C47, o "Verdade" de 0,4 s); se fica, vai no cartão escuro
  da legenda (C49).
- **Sem API não há diarização.** O Whisper não separa vozes, e as marcas `>>` da legenda do YouTube inverteram os trechos
  (C27). Decidir no ouvido e na imagem: folha de quadros a cada 2 a 4 s com o tempo, olhando a boca de quem fala (no C49 e no
  C41 a diarização automática trocou quem falava).
- **Fala por cima não troca a câmera:** a imagem fica em quem está no raciocínio até ele terminar (ver `corte-e-fala.md`).

## 13. O texto precisa ter onde cortar

- **Todo bloco começa e termina numa pausa real** (envelope abaixo de −40 dB, 30 ms ou mais). Frase que emenda sem pausa sai do
  roteiro ou muda de ponta, e o texto muda junto. Por quê: no C48 o gancho passou a fechar antes de um "E aí" colado; no C49
  três frases sem pausa limpa mudaram o roteiro; no C68 um bloco passou a abrir uma palavra depois.
- **Medir as pontas candidatas antes de mandar** (`corte-e-fala.md`). O tempo do Whisper não é prova: ele estica a palavra
  sobre a pausa e completa palavra cortada (C67). Corte que o editor da fonte já fez não tem pausa (C30).

## 14. O roteiro da animação, cena a cena, antes de animar

Duas camadas:
1. **No roteiro da aprovação 1**, cada bloco já traz a linha "Cena:" (o que a metade de cima mostra) e as telas cheias, como
   no C84. Assim o dono do canal aprova o texto e a ideia visual juntos.
2. **Depois do corte aprovado** (com os tempos reais), o `cortes/<slug>/ROTEIRO_ANIMACAO.md`, antes de qualquer código. Por
   quê (C27): "você mesmo vai criticar esse roteiro até ele ficar um 10/10… que faz mesmo o maior leigo do mundo entender".

**Como escrever o `ROTEIRO_ANIMACAO.md`:**
- Assistir ao vídeo cortado: quadros nos gestos e expressões do Raul (para sincronizar), quem fala e o texto com o tempo.
- O fio da história: um personagem ou objeto que atravessa o vídeo e muda com ele (a carteira de trabalho no C48).
- Cena por cena: `tempo · o que se ouve → o que se vê`, uma ação física por fala, no máximo 3 carimbos, o final em loop, e as
  telas cheias com início, fim e o que aparece.
- Pessoa citada ou subentendida aparece como personagem TIPO com etiqueta, antes da fala se o nome só vem depois (10/10: "a
  imagem da pessoa traz a imersão"); nunca o rosto real, e caricatura só a pedido (C37). Todo personagem tem papel no assunto
  (o boneco genérico foi reprovado duas vezes); o do Raul só quando a fala reage à cena (C44); boné no máximo 1 por vídeo.
- Todo termo técnico vira imagem com explicação curta em letra menor (C41: a "craca" explicada na tela). Vídeo de muita conta
  pede estilo que mostre muita coisa ao mesmo tempo (o cordel do C75 ficou "com pouca informação na tela"). Marca de
  empresa só como nome, e bolsa com código inventado (C46, C50).

**Autocrítica com nota de 0 a 10, em rodadas, até 10/10:**
- [ ] gancho: ironia ou fato visível em 2 s;
- [ ] leigo entende: todo termo técnico tem imagem e explicação;
- [ ] retenção: novidade a cada 2 a 3 s, sem buraco nas falas longas;
- [ ] fio da história e sincronia com os gestos;
- [ ] viralização: uma imagem que vira meme ou print, e o loop;
- [ ] segurança: sem rosto real, sem afirmar além da fala, sem número errado;
- [ ] leitura no celular: até 4 palavras por etiqueta.

**Quem aprova o roteiro da animação é a autocrítica**, não o dono do canal (06/10: "vai ter que ser você fazendo várias
avaliações até ficar perfeito"). Guardar as rodadas no arquivo e animar; ele aprova o vídeo animado. O motor está em
`animacao-hyperframes.md`.

## 15. Autocrítica do roteiro

Antes de mandar, dar nota de 0 a 10 ao roteiro pelo checklist do fim, dizendo o que sustenta e o que tira nota. Abaixo de 9,
refazer. C84 (9,5/10): "o gancho quebra o discurso de coach e o número do Brasil chega cedo… Tira nota: a piada da Saveiro
gasta ~7 s, mas não dá para cortar limpo ali"

## 16. O formato da entrega (modelo: C84, aprovado em 17/10)

O C84 ("Herança, sorte ou trabalho?", 2:04, 4 telas cheias) é o modelo: cabeçalho (fonte, duração, linha da história);
um título por bloco com o tempo; o texto completo em citação; a cena e as telas cheias embaixo; a capa; alternativas, por que
compartilha e risco (seção 9); a autocrítica com nota; e o "Fica de fora" no fim.

**Exemplo curto, no formato** (ilustrativo; o texto real sai da transcrição conferida; tempo da montagem e da fonte):

```markdown
# C90 · O imposto que você paga sem ver (20/10, 19h)

**Fonte:** "Quanto de imposto tem no seu mercado" (`xxxxxxxxxxx`, 410 mil views). Economia do país, sem candidato nem partido.
**Duração:** cerca de 1:34. 3 telas cheias, a 1ª logo depois do gancho.
**Linha da história:** o imposto está no preço → quem ganha menos paga mais → "você não vê, mas paga".

## Bloco 1 · Gancho (0:00–0:09 · fonte 12:10–12:19)
> Quase metade do que você paga no arroz não é arroz, é imposto. E ninguém te mostra isso no caixa.

- Cena: o pacote de arroz na balança, metade vira um carimbo IMPOSTO.
- TELA CHEIA 1 (≈0:05–0:12): o carrinho cheio; os produtos perdem metade, um por um.

## Bloco 2 · Quem paga mais (0:09–0:31 · fonte 15:42–16:04)
> Quem ganha um salário mínimo gasta tudo no mercado. Então é ele que paga mais imposto, proporcionalmente, do que quem ganha
> cinquenta mil.

- Cena: dois carrinhos iguais; a etiqueta do salário de cada um; a barra do imposto enche quase inteira só no do mínimo.

**Capa:** "METADE DO ARROZ / É IMPOSTO / E VOCÊ NÃO VÊ", com o pacote cortado ao meio.
**Gancho, alternativas:** (a) "Vamos falar de imposto": cai, não diz nada. (b) "O rico paga menos": cai, tese sem fato.
(c) **Vence:** o arroz, fato do dia a dia.
**Por que compartilha:** quem faz mercado se vê no cupom e manda para a família.
**Risco:** a "quase metade" varia por produto: a legenda do post diz que é estimativa.
**Autocrítica: 9/10.** O gancho é fato com que todo mundo se identifica e a comparação chega aos 9 s. Tira nota: a conta da
alíquota tem dois números seguidos e foi para o último bloco.

## Fica de fora
- "Isso aqui eu já falei no vídeo da reforma, quem viu sabe" (14:20): autopromoção e não fecha sozinho.
```

## 17. Aprovar antes de agendar

- **Aprovação 1 é do texto:** um "Pode seguir" (C84) libera o corte. Permissão de pular uma aprovação ("já pode fazer com
  animação", C68 e C69) vale só para aquele vídeo.
- **Todo vídeo novo, ou refeito com mudança visível, vai em prévia e PARA.** Por quê (03/10): um vídeo agendado sem aprovação
  teve de sair ("quero ver o vídeo antes de agendar"). "Faz completo" autoriza produzir até o fim, não publicar. Agendar só
  com o "pode agendar" para AQUELE vídeo; se não ficar claro se é agora ou no horário, perguntar em uma linha.

## Checklist antes de mandar o roteiro

- [ ] Quatro testes, tom e janela do dia; linha da história; 3 ou 4 raciocínios fechados ("quem? do quê? por quê?").
- [ ] Gancho em até 5 s, com tema e força, sem pergunta na frente; ordem pela força; 2ª frase sem aula; nada de cara de fim
  nem número técnico no meio; fecho em sentença.
- [ ] Texto completo conferido no ouvido, sem "…" nem [SAI]; palavrão censurado; todas as pontas com pausa real.
- [ ] De 1 a 2 min (ou mais, com motivo); 3 ou 4 telas cheias em falas visuais; cena por bloco; capa com a ideia do gancho.
- [ ] Alternativas, por que compartilha, risco e autocrítica com nota; falas de outros marcadas, apresentador no mínimo.
- [ ] Fatos conferidos, fala datada com data, acusação no condicional; "Fica de fora" com texto, tempo e motivo.
