# Edição de cortes · skill do Claude Code

Skill que faz um corte vertical (1080×1920) do começo ao fim, sem nenhuma API paga:

- pesquisa e baixa a fonte sem tomar bloqueio;
- ranqueia as falas e escreve o roteiro;
- corta sem comer palavra;
- confere fala, áudio e imagem quadro a quadro;
- monta o vídeo em um de dois modos: **Reels de vídeo real** (a pessoa na tela inteira, manchete, nome e função, imagens de
  cobertura, logo e legenda nas cores da marca, como no Instagram da Amigos do Bem) ou **papel recortado** (a metade de cima
  animada, como no canal do Raul), com sonoplastia;
- renderiza e entrega a prévia e a capa.

Ela nasceu no canal de cortes do Raul Sena (@cortesdoraulsena). Cada regra dela veio de um erro que já foi ao ar ou quase
foi. Para usar com outro canal ou outro apresentador, veja "Outro canal" no fim do [SKILL.md](SKILL.md).

## Instalar (uma vez por notebook)

Precisa de: **Claude Code** (o app do Claude na aba Code, ou o `claude` no terminal), **Git**, **Python 3.11+**,
**Node 18+**, **ffmpeg** e **Google Chrome**. O instalador confere tudo e diz como instalar o que faltar.

### Windows (PowerShell)

```powershell
git clone https://github.com/MickaelAlecsander/edicao-de-cortes "$env:USERPROFILE\.claude\skills\edicao-de-cortes"
cd "$env:USERPROFILE\.claude\skills\edicao-de-cortes"
python scripts\instalar.py
```

### macOS e Linux

```bash
git clone https://github.com/MickaelAlecsander/edicao-de-cortes ~/.claude/skills/edicao-de-cortes
cd ~/.claude/skills/edicao-de-cortes
python3 scripts/instalar.py
```

O instalador:

- faz o `pip install` só do que falta;
- põe o `playwright-core` em `scripts/`;
- baixa o Whisper large-v3 (~3 GB) e o alinhador MMS_FA (~1,2 GB);
- prepara o HyperFrames;
- monta um projeto de teste.

Ele termina com **"✓ pronto para editar"** ou com a lista do que faltou.

Opções do instalador:

- `--modelo-whisper medium`: para notebook fraco.
- `--so-conferir`: só confere a máquina, sem instalar nada.

### Atualizar

```bash
cd ~/.claude/skills/edicao-de-cortes      # no Windows: cd "$env:USERPROFILE\.claude\skills\edicao-de-cortes"
git pull
python scripts/instalar.py --so-conferir
```

## Usar

Abra o Claude Code na pasta do seu projeto de cortes (uma pasta vazia serve; a skill cria `_fontes/`, `_pesquisa/`,
`cortes/` e `_lixeira/`) e peça em português, por exemplo:

- "faz um reels de vídeo real com esse depoimento: <arquivo ou link>"
- "faz um corte desse vídeo: https://www.youtube.com/watch?v=…"
- "quais trechos desse vídeo rendem mais corte?"
- "faz o roteiro do corte com o trecho de 12:30 a 15:10"
- "corta, confere as emendas e anima"
- "renderiza e me manda a prévia"

A skill para em dois pontos para você aprovar: o **roteiro** e a **prévia**. Nada é publicado sem o seu "pode agendar".

## O que tem aqui

| Pasta | O que é |
|---|---|
| `SKILL.md` | As regras de ouro e o fluxo de um corte, etapa por etapa. |
| `references/` | Uma referência por etapa: pesquisa e download, ranqueamento, roteiro, corte e fala, conferências, áudio e animação. |
| `scripts/` | As ferramentas (download espaçado, corte sem comer palavra, alinhador, legenda, área de segurança, sonoplastia, finalização) e o `instalar.py`. |
| `assets/modelo_reels/` | O modelo do Reels de vídeo real: `montar_reels.py`, `reels.json` (manchetes, nomes, coberturas, logo, cores, música) e a capa. |
| `assets/modelo/` | O modelo do papel recortado: motor de animação, bancos de personagens e desenhos, legenda, capa e post. |
| `assets/foley/` | Os efeitos sonoros (Kenney, CC0, e os do HyperFrames). |

## Precisa de internet para

- baixar as fontes (yt-dlp);
- na 1ª vez, os modelos e o Chrome do render (o instalador já baixa);
- o GSAP do CDN, em todo render;
- as fontes do Google Fonts, só na 1ª montagem.

O resto roda offline.
