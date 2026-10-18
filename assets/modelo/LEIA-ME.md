# Modelo de projeto: a animação de um corte

Um corte novo começa daqui. O modelo roda só com o que a skill leva: o motor, os bancos de desenho, a legenda, o papel,
o grão e a marca. As regras e o porquê de cada uma estão em `references/animacao-hyperframes.md`.

## Começar

```bash
cp -r <skill>/assets/modelo cortes/cNN-slug      # <skill> = a pasta desta skill
cp cortes/cNN-slug/_cenas_exemplo.js cortes/cNN-slug/_cenas.js
```

- `assets/tempos.json` e `assets/dados.js` do modelo são os 2 primeiros blocos do C84, e `assets/raul.mp4` e `raul.wav`
  são de mentira (29,6 s pretos e mudos, com a voz em 48 kHz estéreo como a do `cortar.py`). A Etapa 2 (`cortar.py`, `legendas.py`) escreve os de verdade por cima.
- A marca vem do `scripts/marca.py` da skill. O `montar.py` procura a skill em `~/.claude/skills/edicao-de-cortes`; se
  ela estiver em outro lugar, defina `EDICAO_CORTES=<pasta da skill>`.

## O que trocar

| Arquivo | O que muda |
|---|---|
| `cortes_gerar.py` | A fonte, as palavras e os blocos do roteiro (vales do `pausas.py`, recortes, trocas). |
| `pos_cortar.py` | O `TEXTO` de cada bloco (a escrita certa), a `FALA` (pronúncia para o alinhador) e o `OUTRO`. |
| `montar.py` | Só o bloco do topo: `TITULO`, `CENAS = "_cenas.js"` e a lista `TELAS` (início e fim de cada tela cheia). |
| `_cenas.js` | O elenco, as cenas, as telas cheias e o `camera([...])` no fim. |
| `gera_som.py` | As deixas, nas mesmas palavras das cenas. O par de som das telas cheias sai sozinho. |
| `capa/index.html` | As 3 linhas da manchete; `capa/assets/raul.jpg` e `capa/assets/mundo.png`. |
| `post.json` | Legenda, trecho, hora e data. |

Não mexa no `motor.html`: o `montar.py` procura trechos exatos dele e para se não achar. Um desenho novo que sirva a
outros cortes vai para o `_desenhos.js` da skill (`assets/modelo/`), não só para a cópia do corte.

## Ordem dos comandos (na pasta do corte; `$S` = `<skill>/scripts`)

```bash
python montar.py                                  # index.html + assets/tela_cheia.json; roda o node --check
node $S/erros_js.mjs index.html                   # nenhum erro de JavaScript
npx --yes hyperframes@0.8.99 snapshot . --at 2,5.5,9 --no-end --describe false -o snapshots   # fotos de cada entrada
python gera_som.py && python $S/sonoplastia.py .  # trilha de efeitos; no fim confere JS e área de segurança
node $S/zona_segura.mjs .                         # precisa dar "✓ tudo dentro da área de segurança"
npx --yes hyperframes@0.8.99 render . --fps 24 -q standard -w 6 -o renders/etapa3_bruto.mp4
python $S/sonoplastia.py . --mux && python $S/finalizar.py .
```

Capa:

```bash
ffmpeg -ss <t do Raul de olhos abertos> -i assets/raul.mp4 -frames:v 1 capa/assets/raul.jpg
npx --yes hyperframes@0.8.99 snapshot . --at <t da cena> --no-end --describe false --zoom <x>,<y>,600,317 --zoom-scale 1 -o _mundo
cp _mundo/frame-00-*.png capa/assets/mundo.png
npx --yes hyperframes@0.8.99 snapshot capa --at 0.5 --no-end --describe false -o _capa
ffmpeg -i _capa/frame-00-at-0.5s.png -q:v 2 renders/cNN_capa.jpg
```

## Testar o modelo sem corte

Numa cópia do modelo: `python montar.py`, depois `node <skill>/scripts/erros_js.mjs index.html` e
`npx --yes hyperframes@0.8.99 snapshot . --at 2,15 --no-end --describe false`. A metade de baixo sai preta (o
`raul.mp4` de mentira). O modelo também passa pelo `gera_som.py`, `sonoplastia.py`, render, `--mux` e `finalizar.py`
(testado de ponta a ponta numa máquina limpa); no fim, o `finalizar.py` acusa "imagem do Raul parada", e é o esperado:
o vídeo de mentira é preto e parado.

## O que vem de fora

- O GSAP vem do CDN (`cdn.jsdelivr.net/npm/gsap@3.14.2`), como em toda composição HyperFrames: o render precisa de
  internet, ou de uma cópia local do `gsap.min.js` em `assets/` com o `<script src>` do `motor.html` apontando para ela
  (essa linha o `montar.py` não confere; a da capa também muda).
- As fontes (Archivo Black e IBM Plex Mono) o HyperFrames embute sozinho. Na 1ª vez ele as baixa do Google Fonts e guarda
  em `~/.cache/hyperframes/fonts`.
