#!/usr/bin/env bash
# Instala a skill edicao-de-cortes no Mac (ou no Linux), num comando só (Terminal):
#
#   curl -fsSL https://raw.githubusercontent.com/MickaelAlecsander/edicao-de-cortes/main/instalar.sh | bash
#
# 1. Mac: instala pelo Homebrew o que faltar (Git, Python 3.12, Node, ffmpeg e Google Chrome). Sem o Homebrew, diz como
#    instalar (ele pede a senha do Mac, que só a própria pessoa digita) e para.
#    Linux: diz o que instalar pelo apt e para, se faltar algo.
# 2. Baixa a skill para ~/.claude/skills/edicao-de-cortes (ou atualiza com git pull, se já existir).
# 3. Roda o scripts/instalar.py, que cria o ambiente Python da skill (~/.venv-cortes) quando o Python do sistema recusa
#    o pip, instala os pacotes, o playwright-core, os modelos (Whisper e MMS_FA) e o HyperFrames, e faz o autoteste.
# Termina com "pronto para editar". Depois, abrir uma conversa NOVA no Claude Code para a skill aparecer.
# Para testar em outra pasta: EDICAO_DESTINO=/outra/pasta bash instalar.sh
set -euo pipefail

# tudo dentro de main(): com `curl | bash`, o bash lê o script inteiro antes de rodar (nenhum comando engole o resto)
main() {
REPO="https://github.com/MickaelAlecsander/edicao-de-cortes"
DESTINO="${EDICAO_DESTINO:-$HOME/.claude/skills/edicao-de-cortes}"
SO="$(uname -s)"
tem() { command -v "$1" >/dev/null 2>&1; }

echo "Skill edicao-de-cortes: instalando ($SO)"
echo "1 · Programas"
if [ "$SO" = "Darwin" ]; then
  if ! tem brew; then
    for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)"; done
  fi
  if ! tem brew; then
    echo "  ⛔ Falta o Homebrew. Instale no Terminal (ele pede a senha do Mac) e rode este comando de novo:"
    echo '     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
  fi
  for p in git node ffmpeg; do
    if tem "$p"; then echo "  ok $p"; else echo "  ... brew install $p"; brew install "$p"; fi
  done
  if ! brew list python@3.12 >/dev/null 2>&1; then echo "  ... brew install python@3.12"; brew install python@3.12; fi
  PY="$(brew --prefix python@3.12)/bin/python3.12"
  if [ -d "/Applications/Google Chrome.app" ]; then echo "  ok Chrome"; else echo "  ... brew install --cask google-chrome"; brew install --cask google-chrome; fi
elif [ "$SO" = "Linux" ]; then
  FALTA=""
  for p in git node ffmpeg python3; do tem "$p" || FALTA="$FALTA $p"; done
  [ -x /opt/google/chrome/chrome ] || FALTA="$FALTA google-chrome"
  if [ -n "$FALTA" ]; then
    echo "  ⛔ Falta:$FALTA. No Debian/Ubuntu: sudo apt install git nodejs npm ffmpeg python3 python3-venv python3-pip"
    echo "     e o Chrome pelo .deb de google.com/chrome. Depois, rode este comando de novo."
    exit 1
  fi
  PY="python3"
else
  echo "  ⛔ Sistema $SO: no Windows, use o instalar.ps1 (ver o README)."
  exit 1
fi

echo "2 · A skill em $DESTINO"
if [ -d "$DESTINO/.git" ]; then
  git -C "$DESTINO" pull --ff-only
elif [ -e "$DESTINO" ]; then
  echo "  ⛔ A pasta $DESTINO já existe e não é um clone do GitHub. Mova-a para outro lugar e rode de novo."
  exit 1
else
  mkdir -p "$(dirname "$DESTINO")"
  git clone "$REPO" "$DESTINO"
fi

echo "3 · Pacotes, modelos e autoteste (scripts/instalar.py)"
"$PY" "$DESTINO/scripts/instalar.py" ${@+"$@"}   # ${@+…}: o bash 3.2 do Mac quebra com "$@" vazio sob set -u
echo
echo "Pronto. Abra uma conversa NOVA no Claude Code para a skill edicao-de-cortes aparecer."
}

main ${@+"$@"}
