---
name: edicao-de-cortes
description: Esta skill deve ser usada para produzir um corte vertical (1080×1920) para Reels do Instagram e TikTok, do começo ao fim e sem nenhuma API (nasceu no canal de cortes do Raul Sena) — pesquisar e baixar a fonte sem tomar bloqueio, ranquear as falas, escrever o roteiro, cortar sem comer palavra, conferir fala, áudio e imagem quadro a quadro, animar a metade de cima em papel recortado no HyperFrames e renderizar. Usar também quando pedirem só uma etapa ("baixa esse vídeo", "faz o roteiro", "corta esse trecho", "confere as emendas", "anima", "renderiza", "qual corte rende mais", "faz um reels"). O app de edição é o HyperFrames e quem ouve o áudio é o Whisper local.
---

# Edição de cortes (sem API)

Esta skill reúne tudo o que o canal aprendeu editando cortes: pesquisa e download, ranqueamento,
roteiro, corte, conferências e animação. Cada regra veio de um erro que já foi ao ar ou quase foi.
Ela roda num ambiente **sem API nenhuma**:
- **Editar e renderizar:** o HyperFrames (`npx --yes hyperframes@0.8.99 …`).
- **Ler e ouvir o áudio:** o Whisper local (whisper.cpp pelo HyperFrames, ou faster-whisper).
- **Medir o tempo de cada palavra:** o alinhador forçado local (MMS_FA, torchaudio) e o envelope do áudio.

## Dois modos: escolher antes de começar

| Modo | Quando | Modelo |
|---|---|---|
| **Reels de vídeo real** | Perfil institucional ou de marca (ex.: @amigosdobem): a pessoa ou a ação na tela inteira, manchete, nome e função, imagens de cobertura, logo e legenda. Pouca ou nenhuma animação. | `assets/modelo_reels/` (ver o `LEIA-ME.md` dele) |
| **Papel recortado** | Canal de cortes de opinião (o do Raul): a metade de cima animada em papel, o apresentador embaixo e telas cheias de animação. | `assets/modelo/` e `references/animacao-hyperframes.md` |

Na dúvida, perguntar qual dos dois. Tudo o que vem antes da animação (tema, roteiro, corte sem comer palavra,
conferências de fala e de áudio, legenda, área de segurança, finalização e entrega) vale igual para os dois. No reels de
vídeo real, a Etapa 3 é o `montar_reels.py` no lugar das cenas, e as regras de personagem, papel e telas cheias de
animação não se aplicam.

## Regras de ouro (valem em toda etapa)

1. **Sem API.** Nada de chave da OpenAI ou de qualquer serviço pago. O Whisper local dá o TEXTO. O tempo fino vem do
   alinhador MMS_FA e da pausa real no envelope (`scripts/pausas.py`). **O Whisper não é prova de tempo:** no C29, o
   large-v3 pôs palavras até 1,4 s fora do lugar, e cada erro virou uma ponta errada.
2. **Aprovação antes de avançar.** Roteiro aprovado → edição → animação → prévia. Nada é agendado ou publicado sem
   o "pode agendar" do dono do canal. Quando ele pedir "faz até o final", as aprovações do meio se juntam numa só: a da prévia.
3. **Nunca cortar no meio de uma palavra.** A ponta é sempre um vale de energia abaixo de −40 dB, antes da palavra
   SEGUINTE. Toda emenda é ouvida de novo depois de montada (`scripts/ouvir_emendas.py`).
4. **O Raul inteiro, centrado, sem zoom e nunca travado.** A imagem é sempre a do mesmo instante do áudio; em podcast, ela
   fica em quem está no raciocínio, e quem fala se marca em todo corte com 2 pessoas. Cabeça nunca cortada. Na tela dividida da fonte, o painel dele
   preenche a janela de baixo; nada de laterais desfocadas. Não pode haver quadro parado com fala. Foto ou gráfico em
   tela inteira na fonte vai para debaixo de uma TELA CHEIA da animação.
5. **A legenda fica do começo ao fim**, de 1 a 3 palavras, com palavrão censurado (`F**A`).
6. **Área de segurança sempre.** Nada embaixo da busca do TikTok, nada saindo pelas laterais, nada embaixo dos botões
   ou do texto do post. `scripts/zona_segura.mjs` precisa dar ✓ antes de todo render.
7. **Tela cheia:** 3 vezes de 5 s ou mais em vídeo de até 2 min, 4 vezes acima de 2 min. A 1ª vem logo após o gancho.
8. **A melhor faixa de áudio** (o Opus do YouTube), um mínimo de recompressão e a saída em −14 LUFS. O efeito sonoro
   fica sempre por baixo da fala.
9. **Download espaçado.** Um pedido por vez, nunca em rajada, com folga entre eles (`scripts/baixar.py` já faz isso).
   Um IP marcado com 429 só volta com tempo. O cliente `web_safari,mweb` serve só para LISTAR vídeos e ler os dados deles (título, idioma, canal). Com ele a
   legenda some ("has no subtitles" em todo vídeo) e a resolução vem falsa (360p), então legenda e mídia vão no cliente padrão.
10. **Nunca apagar de vez.** O que sai vai para `_lixeira/`, e quem esvazia é o dono do canal. Nunca digitar senha nem
    token: o login é sempre a própria pessoa quem faz.

## Instalação (uma vez por máquina)

`python scripts/instalar.py` (com o Python 3.11+) prepara a máquina numa rodada só. No fim, ele diz "✓ pronto para editar"
ou lista o que faltou. Ele faz cinco coisas:
1. Confere o Python, o ffmpeg e o ffprobe, o Node 18+ com o npx e o Chrome. O que não sai por pip ou npm, ele diz como
   instalar no seu sistema.
2. Faz o `pip install` só do que falta (faster-whisper, torch e torchaudio de CPU, numpy, scipy, soundfile, opencv,
   yt-dlp). O que já está instalado não é atualizado nem rebaixado.
3. Faz o `npm install playwright-core` em `scripts/`, que é de onde o `zona_segura.mjs` e o `erros_js.mjs` o importam.
4. Baixa o Whisper large-v3 (~3 GB) e o MMS_FA (~1,2 GB) e aquece o `npx --yes hyperframes@0.8.99` e o Chrome do render.
5. Faz o autoteste: o `--help` de 3 scripts, o `node --check` dos `.mjs` e o `assets/modelo/` montado numa pasta temporária.

Ele tem três opções:
- `--so-conferir`: só confere e não instala nada.
- `--sem-modelos`: pula os modelos.
- `--modelo-whisper medium`: para máquina fraca. Depois, passe `--modelo medium` ao `transcrever_local.py`.

- **Whisper do HyperFrames** (opcional): `npx --yes hyperframes@0.8.99 transcribe <arquivo> -e whisper -m large-v3 -l pt --json`.
  Ele precisa do whisper-cpp, e o `npx --yes hyperframes@0.8.99 doctor` diz se ele está instalado.
- **O que precisa de internet** (o resto roda offline):
  - baixar as fontes (yt-dlp);
  - na 1ª vez, os modelos (o Whisper large-v3 e o MMS_FA) e o Chrome do render; o instalador já baixa os três;
  - o GSAP do CDN, em todo render;
  - as fontes do Google Fonts, na 1ª montagem (depois ficam guardadas em `~/.cache/hyperframes/fonts`).
- **Testar a máquina** a qualquer hora: `python scripts/instalar.py --so-conferir`.

## Estrutura do projeto

```
<projeto>/
  _fontes/            vídeos e áudios baixados (o <id>_opus.mkv é a fonte do corte)
  _pesquisa/          legendas, transcrições (<id>_palavras.json), radar e notas
  _lixeira/           o que sai (fontes depois de publicadas etc.)
  cortes/cNN-slug/    um corte: ROTEIRO.md, cortes_gerar.py, cortes.json, pos_cortar.py, _cenas.js, montar.py,
                      gera_som.py, som.json, capa/, post.json, assets/ (raul.mp4, raul.wav, tempos.json, dados.js),
                      renders/ (etapa3_bruto.mp4, etapa3.mp4, cNN_previa.mp4, cNN_capa.jpg)
  LOG_CORTES.md       uma entrada por corte (id da fonte, o que foi ao ar, o que o dono decidiu) e as "Lições acumuladas";
                      sem ele, o ranking_shorts.py não tira nenhum id já usado
  REGUA.md            as correções do dono à régua (ler antes de dar nota); RADAR.md é gerado pelo nota_viral.py
```

## O fluxo de um corte

Ler a referência da etapa ANTES de começá-la. Cada uma tem as regras completas e o porquê de cada uma.

| Etapa | O que fazer | Referência | Scripts |
|---|---|---|---|
| 0 · Tema | Achar candidatos, ranquear falas e shorts, dar a nota da régua, escolher pelo placar | `references/ranqueamento.md` | `nota_viral.py`, `ranking_shorts.py`, `analise_shorts.py`, `acha_frase.py` |
| 1 · Fonte | Listar, ler a legenda, baixar a melhor faixa sem tomar bloqueio | `references/pesquisa-e-download.md` | `baixar.py`, `vtt2txt.py` |
| 1 · Roteiro | Transcrever o trecho, montar o raciocínio completo, entregar para ✋ | `references/roteiro.md` | `transcrever_local.py` |
| 2 · Corte | Medir as pontas, achar as trocas de câmera, cortar, realinhar, legendar | `references/corte-e-fala.md` | `pausas.py`, `trocas.py`, `cortar.py`, `alinhar.py`, `legendas.py`, `borrar_regiao.py`, `reenquadrar.py` |
| 2 · Conferir | Ouvir as emendas, olhar quadro a quadro | `references/conferencias.md` | `ouvir_emendas.py`, `conferir_fins.py`, `folha_contato.py`, `travada.py` |
| 3 · Animação | Roteiro da animação, cenas, telas cheias, área de segurança | `references/animacao-hyperframes.md` | `assets/modelo/`, `roteirista.py`, `marca.py`, `zona_segura.mjs`, `erros_js.mjs` |
| 3 · Reels de vídeo real | Manchete, nome e função, coberturas, logo, cores da marca (no lugar da animação) | `assets/modelo_reels/LEIA-ME.md` | `montar_reels.py`, `zona_segura.mjs`, `erros_js.mjs` |
| 3 · Som | Deixas na palavra da cena, sonoplastia por baixo da fala | `references/audio.md` | `sonoplastia.py` (+ `assets/foley/`) |
| 4 · Render | Render, mux, finalizar, conferir o pronto e mandar a prévia | `references/conferencias.md` | `finalizar.py`, `folha_contato.py` |

### Comandos, na ordem (da pasta `cortes/cNN-slug/`; `$S` = pasta `scripts/` desta skill)

Começar copiando `assets/modelo/` para `cortes/cNN-slug/` (ver `assets/modelo/LEIA-ME.md`): ele traz o
`cortes_gerar.py`, o `pos_cortar.py`, o `montar.py`, o `gera_som.py`, a capa e o `post.json` para preencher. Se a skill
não estiver em `~/.claude/skills/edicao-de-cortes`, definir `EDICAO_CORTES=<pasta da skill>`.

```bash
python $S/pausas.py <fonte> --palavras <palavras.json> <t:antes:depois> ... --perfil   # cada ponta, antes de escrever
python $S/trocas.py <fonte> --de <s> --ate <s>   # trocas de câmera e de layout no trecho
python cortes_gerar.py                       # escreve o cortes.json (blocos, janelas, recortes, trocas)
python $S/cortar.py .                        # monta assets/raul.mp4, raul.wav e tempos.json (barra ponta em fala)
python pos_cortar.py                         # TEXTO do roteiro realinhado pelo MMS_FA (palavra a palavra)
python $S/legendas.py .                      # assets/dados.js: a legenda em blocos de 1 a 3 palavras
python $S/ouvir_emendas.py .                 # cada emenda no Whisper local + envelope
python $S/conferir_fins.py .                 # as pontas de cada bloco
python $S/folha_contato.py assets/raul.mp4 --cada 2   # o Raul inteiro e a pessoa certa em cada quadro
# (✋2, se o dono pedir: ver o fim de references/corte-e-fala.md) · aqui, pedir o esforço extra antes de animar
python $S/roteirista.py batidas .            # batidas.md: frases, âncoras T() com o n certo, alusões a pessoas
python montar.py                             # index.html (animação + Raul + legenda + marca)
python gera_som.py && python $S/sonoplastia.py .   # trilha de efeitos; no fim confere JS e área de segurança
npx --yes hyperframes@0.8.99 render . --fps 24 -q standard -w 6 -o renders/etapa3_bruto.mp4
python $S/sonoplastia.py . --mux             # som sem perda na imagem do render
python $S/finalizar.py .                     # −14 LUFS, travada, prévia de 720p
python $S/folha_contato.py renders/etapa3.mp4 --cada 3   # olhar o vídeo pronto antes de mandar
```

## Como entregar

- **Roteiro:** no formato de `references/roteiro.md`: linha da história, blocos com o texto completo e a cena de cada
  um, telas cheias, capa, autocrítica com nota e, no fim, a lista do que fica de fora.
- **Prévia:** a prévia de 720p e a capa, com o resumo do vídeo:
  - as telas cheias;
  - o que foi conferido (área de segurança, travada, loudness);
  - o que foi corrigido depois do 1º render;
  - a legenda do post.
  Depois, esperar o "pode agendar". O pedido explícito de deixar agendado ("quero pronto, tudo perfeito, agendado") já vale
  como o "pode agendar" daqueles vídeos.
- **Legenda do post** (`post.json`): informação útil com o crédito ao apresentador ("Para o Raul Sena, …"), **até ~430
  caracteres** (no TikTok, a de ~600 perdeu o começo no campo em 3 tentativas; as de 421 e 426 entraram), sem travessão nem
  aspa angular e com palavrão censurado. No fim, as hashtags: as 2 da marca, de 3 a 5 do tema do jeito que as pessoas buscam e
  de 1 a 2 gerais, sem acento nem espaço. O `trecho` do `post.json` é o começo da legenda: ele acha o post no Studio.
- **Três redes no mesmo horário:** o "pode agendar" do TikTok vale para o Instagram e o Facebook no MESMO horário, sem pedir
  de novo. Depois do horário, conferir que o post saiu nas três (no C80 e no C83 o Instagram falhou por bloqueio da conta).
- **Folga no TikTok:** conta nova passa todo post pela revisão ("Conteúdo sob análise", até 12 h). Agendar com 2 h ou mais
  de folga, nunca a menos de 20 min do horário.
- **Decisão visual** (layout, estilo, capa): mandar as opções em IMAGEM para o dono escolher.
- **Depois de mexer em código ou ferramenta:** o resumo vem completo: o que mudou, por quê, o que ficou de fora e o que
  falta fazer.

## Instagram (Reels)

O mesmo vídeo serve para o Reels e para o TikTok. No Instagram:
- **Subir o arquivo renderizado** (`renders/etapa3.mp4`), nunca um vídeo baixado do TikTok: o Instagram diminui o alcance
  de vídeo reciclado com marca d'água.
- **A legenda do post** aceita até 2.200 caracteres, mas só a 1ª linha aparece antes do "mais": ela precisa ser o gancho.
  Hashtags: de 3 a 5 do tema, mais as da marca (o Instagram recomenda poucas e relevantes).
- **A capa** aparece na grade do perfil no recorte 3:4 do centro: o rosto e a manchete inteiros dentro dele (a capa do
  modelo já é feita assim). No app, ela entra em "Editar capa" → "Adicionar da galeria".
- **A área de segurança** do `zona_segura.mjs` (busca em cima, botões à direita, texto do post embaixo) vale para os dois.
  No 1º post, olhar um print do Reels publicado em cada tela cheia e, se a interface cobrir algo, ajustar os limites.
- **Duração:** de 1 a 2 min (o Reels aceita até 3).
- **Os números da régua e da grade** (horários, pesos, limites de views) foram medidos no TikTok deste canal: no Instagram,
  recomeçar o placar com os próprios dados.

## Outro canal

A skill nasceu no canal de cortes do Raul Sena e os exemplos são dele. Para usar com outro apresentador ou outra marca,
trocar:
- **A marca:** `CONTA` e o avatar no `scripts/marca.py` e em `assets/modelo/marca/` (a foto de perfil e o @ que ficam à
  esquerda na metade de baixo).
- **As fontes e o filtro de cópias:** o `CANAL` e as palavras que excluem cópias no `scripts/ranking_shorts.py`, e as
  palavras ignoradas no `scripts/analise_shorts.py`.
- **O personagem do apresentador:** o `TIPO.raul` no `assets/modelo/personagens.js` (cabelo, roupa, barba), e os rótulos
  `raul` e `apresentador` do `legendas.py` e do `travada.py` (quem fala).
- **O post:** as 2 hashtags da marca, o crédito do começo da legenda ("Para o Raul Sena, …") e a propaganda do apresentador
  que sai do corte (no Raul, a AUVP).
- **Os números:** os pesos da régua, os limites da prova (300 mil e 700 mil), o tom do canal e a grade de horários foram
  medidos neste canal. Outro canal recomeça o placar do zero e ajusta a régua pelo resultado (ver `references/ranqueamento.md`).
- **As janelas do momento** (ex.: a eleição de outubro de 2026): perguntar ao dono qual vale hoje.
