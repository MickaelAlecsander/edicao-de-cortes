# Modelo de projeto: REELS DE VÍDEO REAL (sem a animação de papel)

Para perfis como o da Amigos do Bem (@amigosdobem): a pessoa ou a ação na tela inteira, manchete forte, nome e função de
quem fala, imagens de cobertura, logo da marca e a legenda do começo ao fim. Nada de papel recortado, personagens ou
telas cheias de animação. O corte, as conferências de fala e de áudio, a legenda, a área de segurança e a finalização são
os mesmos da skill (`references/corte-e-fala.md`, `references/conferencias.md`, `references/audio.md`).

Testado de ponta a ponta numa máquina limpa (corte vertical real, manchete, nome, cobertura em vídeo e em foto, som,
render, `--mux` e `finalizar.py`).

## Começar

```bash
mkdir cortes/r01-slug && cd cortes/r01-slug
cp <skill>/assets/modelo/cortes_gerar.py <skill>/assets/modelo/pos_cortar.py .
cp <skill>/assets/modelo_reels/montar_reels.py <skill>/assets/modelo_reels/reels.json .
```

No `cortes_gerar.py`:
- `JW, JH = 1080, 1920` (vertical).
- O recorte de cada bloco é `[x, largura, y]` na fonte:
  - **fonte vertical** (celular, 1080×1920): `[0, 1080, 0]`;
  - **fonte horizontal** (1920×1080): uma faixa de `[x, 606, 0]` centrada no rosto (a altura sai 606 × 1920/1080 ≈ 1077).
    O rosto fica no meio da faixa e a cabeça inteira, com folga em cima para a manchete.
- `"recorte": {"w": <largura>, "y": 0}` igual à largura dos blocos.

## O `reels.json`

| Campo | O que é |
|---|---|
| `manchetes` | O gancho escrito: `texto` (`\n` quebra a linha), `de`, `ate`, `y` (padrão 300). Até ~4 palavras por linha, 2 linhas. |
| `nomes` | Quem fala, na 1ª vez que aparece: `nome`, `funcao`, `de`, `ate`, `y` (padrão 1060). |
| `coberturas` | Imagens da ação por cima da fala: `arquivo` (vídeo ou foto em `assets/`), `de`, `ate`, `inicio` (o ponto do vídeo). |
| `logo` | `arquivo` (PNG com fundo transparente), `canto` (`esquerda` ou `direita`), `tamanho` (px). Vazio = sem logo. |
| `cores` | As cores da marca: cartão e texto da legenda, marca-texto, destaque, fundo e texto da manchete e do nome. |
| `legenda_y` | O centro da legenda (padrão 1270, longe dos botões e do texto do post). |
| `musica` | `arquivo` e `volume` (padrão 0,07, bem por baixo da fala). Só música com licença de uso. Vazio = sem música. |
| `som` | `true` escreve o `som.json` com o som discreto das entradas (whoosh na cobertura, pouso na manchete e no nome). |

Todo tempo (`de`, `ate`) é um número em segundos ou uma âncora `["palavra", "bloco", n, deslocamento]`, como o `T()` das
cenas: a âncora acompanha a palavra quando o corte muda. Conferir o `n` no `assets/tempos.json` (a palavra pode se repetir).

## Ordem dos comandos (na pasta do corte; `$S` = `<skill>/scripts`)

```bash
python cortes_gerar.py && python $S/cortar.py .   # assets/raul.mp4 em 1080×1920, raul.wav, tempos.json
python pos_cortar.py && python $S/legendas.py .   # o texto certo realinhado e a legenda
python $S/ouvir_emendas.py . && python $S/conferir_fins.py .
python montar_reels.py                            # index.html, som.json e assets/tela_cheia.json
python $S/sonoplastia.py . && python montar_reels.py   # o som; montar de novo põe a trilha no index.html
npx --yes hyperframes@0.8.99 snapshot . --at <instantes> --no-end --describe false -o snapshots
npx --yes hyperframes@0.8.99 render . --fps 24 -q standard -w 6 -o renders/etapa3_bruto.mp4
python $S/sonoplastia.py . --mux                  # SÓ sem música: o --mux troca o áudio inteiro e tiraria a música
python $S/finalizar.py .                          # −14 LUFS, imagem parada (na tela inteira), prévia de 720p
```

O `sonoplastia.py` confere no fim o JavaScript e a área de segurança (manchete, nome e logo entre y 150 e 1700, e nada à
direita de x 920 entre y 900 e 1700, onde ficam os botões).

## Regras do reels de vídeo real

- **Gancho nos 3 primeiros segundos, com manchete.** A manchete diz a ideia do vídeo em até 8 palavras e sai quando a fala
  já se sustenta (ou fica até o fim do gancho).
- **A legenda fica do começo ao fim**, de 1 a 3 palavras, com a palavra dita marcada; nunca some, nem com a manchete.
- **Nome e função** na 1ª vez que cada pessoa aparece, por 3 a 4 s.
- **Cobertura a cada 5 a 8 s de fala parada**, sempre de imagem que mostra o que a pessoa diz (o projeto, o lugar, as
  pessoas atendidas). Imagem do mesmo instante da fala da pessoa nunca é trocada por outra dela mesma (`de`/`congela`).
- **A cabeça inteira e o rosto centrado** em todo quadro; nada de zoom que varia.
- **Pessoa atendida, criança ou paciente:** só com autorização de imagem; na dúvida, cobertura sem rosto. Nunca nome
  completo de beneficiário na tela.
- **Música** só com licença de uso e bem baixa; nenhum efeito por cima da fala.
- **A manchete nunca cobre os olhos** (no vídeo e na capa). No vídeo, ela fica acima da cabeça (`y`) ou só no gancho; se o
  rosto estiver alto no quadro, deixar mais espaço em cima no recorte.
- **Capa:** um quadro real com o rosto livre, a manchete de 2 a 3 linhas ABAIXO do rosto e o logo, dentro do recorte 3:4
  do centro, y 240 a 1680 (`capa/index.html` já vem assim).

## Capa

```bash
ffmpeg -ss <t do rosto livre, olhos abertos> -i assets/raul.mp4 -frames:v 1 capa/assets/foto.jpg
npx --yes hyperframes@0.8.99 snapshot capa --at 0.5 --no-end --describe false -o _capa
ffmpeg -i _capa/frame-00-at-0.5s.png -q:v 2 renders/r01_capa.jpg
```
Trocar as 3 linhas e as cores no `capa/index.html` (copiar a pasta `capa/` deste modelo para o corte).
