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

## Instalar (uma vez por notebook, Windows ou Mac)

### O jeito mais fácil: pedir ao Claude

Abra o **Claude Code** (a aba Code do app do Claude, ou o `claude` no terminal) e cole:

> Instala a skill https://github.com/MickaelAlecsander/edicao-de-cortes

O Claude lê esta página, segue a seção "Para o Claude" lá embaixo, instala o que faltar (pedindo o seu ok antes) e avisa
quando terminar. Depois, abra uma conversa **nova** no Claude Code para a skill aparecer.

### Ou um comando só

**Windows** (PowerShell):

```powershell
irm https://raw.githubusercontent.com/MickaelAlecsander/edicao-de-cortes/main/instalar.ps1 | iex
```

**Mac** (Terminal):

```bash
curl -fsSL https://raw.githubusercontent.com/MickaelAlecsander/edicao-de-cortes/main/instalar.sh | bash
```

O comando:

1. instala o que faltar: Git, Python 3.12, Node, ffmpeg e Google Chrome (no Windows pelo winget; no Mac pelo Homebrew);
2. baixa a skill para a pasta de skills do Claude (`~/.claude/skills/edicao-de-cortes`);
3. instala os pacotes do Python, o Whisper large-v3 (~3 GB), o alinhador MMS_FA (~1,2 GB) e o HyperFrames;
4. monta um projeto de teste.

Na 1ª vez leva de 10 a 30 min, por causa dos modelos. Ele termina com **"✓ pronto para editar"** ou com a lista do que
faltou e como resolver.

- **Mac sem o Homebrew:** o comando para e mostra como instalar o Homebrew. Ele pede a senha do Mac, que só você digita.
  Depois, rode o comando de novo.
- **Mac com o Python do Homebrew:** esse Python recusa instalar pacotes. O instalador cria sozinho o ambiente da skill
  (`~/.venv-cortes`) e o Claude passa a usá-lo.
- **Notebook fraco:** acrescente `--modelo-whisper medium` (Windows: `& ([scriptblock]::Create((irm <link>))) --modelo-whisper medium`;
  Mac: `curl -fsSL <link> | bash -s -- --modelo-whisper medium`).

### Manual

```bash
git clone https://github.com/MickaelAlecsander/edicao-de-cortes ~/.claude/skills/edicao-de-cortes
cd ~/.claude/skills/edicao-de-cortes
python3 scripts/instalar.py          # no Windows: python scripts\instalar.py
```

O `scripts/instalar.py` confere e instala os pacotes, os modelos e o HyperFrames. Para só conferir a máquina, sem instalar
nada: `--so-conferir`.

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

## Para o Claude (instalação a pedido de alguém)

Quando pedirem para instalar esta skill:

1. Ver o sistema (Windows, macOS ou Linux) e dizer à pessoa, numa mensagem curta, o que vai ser instalado: os programas
   que faltarem (Git, Python 3.12, Node, ffmpeg, Google Chrome), os pacotes do Python e os modelos (~4 GB). Pedir o ok
   antes de instalar programas.
2. Rodar o comando do sistema, em segundo plano (pode passar de 10 min), e acompanhar a saída:
   - Windows, no PowerShell: `irm https://raw.githubusercontent.com/MickaelAlecsander/edicao-de-cortes/main/instalar.ps1 | iex`
   - Mac ou Linux, no bash: `curl -fsSL https://raw.githubusercontent.com/MickaelAlecsander/edicao-de-cortes/main/instalar.sh | bash`
3. Se faltar o Homebrew no Mac, o comando para e mostra a linha de instalação: quem roda é a PESSOA, no Terminal dela,
   porque ele pede a senha do Mac. Nunca digitar senha. Depois, rodar o comando de novo.
4. Se um programa acabou de ser instalado e "não aparece", abrir um terminal novo (o PATH muda) e rodar de novo.
5. O fim certo é "✓ pronto para editar". Se vier a lista do que faltou, resolver item por item como ela diz e rodar
   `python scripts/instalar.py --so-conferir` na pasta da skill para confirmar.
6. Avisar a pessoa para abrir uma conversa NOVA no Claude Code (a skill carrega no começo da conversa) e pedir, por
   exemplo: "faz um reels de vídeo real com este vídeo: <arquivo ou link>".
