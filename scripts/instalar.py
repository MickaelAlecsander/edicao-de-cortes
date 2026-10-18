# -*- coding: utf-8 -*-
"""Prepara uma máquina (Windows, macOS ou Linux) para a skill edicao-de-cortes, numa rodada só.

    python scripts/instalar.py                         # confere, instala o que falta, baixa os modelos e faz o autoteste
    python scripts/instalar.py --so-conferir           # só confere e diz o que falta: não instala nem baixa nada
    python scripts/instalar.py --sem-modelos           # tudo, menos o download dos modelos (Whisper e MMS_FA)
    python scripts/instalar.py --modelo-whisper medium # máquina fraca: o medium (~1,5 GB) no lugar do large-v3 (~3 GB)

1. Confere o Python 3.11+, o ffmpeg e o ffprobe, o Node 18+ e o npx, e o Chrome. O que não sai por pip/npm, ele explica
   como instalar naquele sistema e segue.
2. pip install SÓ do que falta. O que já está instalado fica fixo na versão de agora: nada é atualizado nem rebaixado.
   O torch vai na versão de CPU (ver TORCH_CPU).
3. npm install playwright-core em scripts/, de onde o zona_segura.mjs e o erros_js.mjs o importam.
4. Baixa e aquece os modelos uma vez (faster-whisper e MMS_FA) e o cache do npx do HyperFrames (+ o Chrome do render).
5. Autoteste: import de cada pacote, --help de 3 scripts, node --check dos .mjs e o modelo de projeto montado numa pasta
   temporária (assets/modelo → python montar.py → node scripts/erros_js.mjs index.html).
Termina com "✓ pronto para editar" ou com a lista do que faltou (e sai com código 1).
"""
import argparse
import functools
import importlib.metadata
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AQUI = os.path.dirname(os.path.abspath(__file__))  # scripts/
SKILL = os.path.dirname(AQUI)
SO = {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")
HF = "hyperframes@0.8.99"
# (módulo, pacote do pip, quem usa). opencv sem GUI: nenhum script abre janela, e a versão com GUI pede a libGL no Linux.
PACOTES = [
    ("numpy", "numpy", "quase todos os scripts"),
    ("scipy", "scipy", "sonoplastia.py"),
    ("soundfile", "soundfile", "sonoplastia.py"),
    ("cv2", "opencv-python-headless", "folha_contato.py, reenquadrar.py"),
    ("faster_whisper", "faster-whisper", "transcrever_local.py, conferir_fins.py, ouvir_emendas.py"),
    ("torch", "torch", "alinhar.py, pos_cortar.py"),
    ("torchaudio", "torchaudio", "alinhar.py: o MMS_FA"),
    ("yt_dlp", "yt-dlp", "baixar.py, ranking_shorts.py, analise_shorts.py"),
]
# TORCH_CPU: o torch aqui só roda o alinhador MMS_FA (alinhar.py), que trabalha na CPU e leva segundos por bloco; a GPU
# do Whisper vem do ctranslate2 (faster-whisper), não do torch. Então, no Windows e no Linux, a roda de CPU do pytorch.org
# (~200 MB; a do PyPI no Linux puxa ~2,5 GB de CUDA que nada usaria). No macOS, a do PyPI já é a de CPU (+ MPS).
TORCH_CPU = [] if SO == "macos" else ["--index-url", "https://download.pytorch.org/whl/cpu"]
TAMANHO = {"large-v3": "~3 GB", "medium": "~1,5 GB", "small": "~0,5 GB"}
COMO = {
    "python": {"windows": "winget install Python.Python.3.12 (ou python.org) e rode este instalador com ele",
               "macos": "brew install python@3.12 e rode este instalador com ele",
               "linux": "sudo apt install python3.12 python3.12-venv (ou o pacote da sua distribuição)"},
    "ffmpeg": {"windows": "winget install Gyan.FFmpeg e abra um terminal novo",
               "macos": "brew install ffmpeg",
               "linux": "sudo apt install ffmpeg (Fedora: sudo dnf install ffmpeg, do RPM Fusion)"},
    "node": {"windows": "winget install OpenJS.NodeJS.LTS e abra um terminal novo",
             "macos": "brew install node",
             "linux": "o Node LTS de nodejs.org ou do nvm (nvm install --lts); o nodejs do apt costuma ser velho"},
    "chrome": {"windows": "winget install Google.Chrome",
               "macos": "brew install --cask google-chrome (ou google.com/chrome)",
               "linux": "o .deb/.rpm de google.com/chrome (instala em /opt/google/chrome; o Chromium do snap não serve)"},
}
FALTA, AVISOS = [], []


def ok(m):
    print("  ✓ " + m)


def aviso(m):
    print("  ⚠ " + m)
    AVISOS.append(m)


def falta(m, como=None):
    print("  ⛔ " + m + ("\n       → " + como if como else ""))
    FALTA.append(m)


def roda(cmd, timeout=600, **kw):
    """(código, saída) sem estourar: programa ausente vira 127 e tempo esgotado vira 124."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, **kw)
        return r.returncode, (r.stdout + "\n" + r.stderr).strip()
    except FileNotFoundError:
        return 127, "não encontrado"
    except subprocess.TimeoutExpired:
        return 124, "passou de %d s" % timeout


def ultima(s):
    linhas = [x for x in s.splitlines() if x.strip()]
    return linhas[-1].strip() if linhas else ""


def chrome():
    """Os mesmos caminhos onde o playwright-core procura o channel "chrome" (o do zona_segura.mjs e do erros_js.mjs)."""
    if SO == "windows":
        bases = [os.environ.get(k) for k in ("LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)")]
        cands = [os.path.join(b, "Google", "Chrome", "Application", "chrome.exe") for b in bases if b]
    elif SO == "macos":
        cands = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    else:
        cands = ["/opt/google/chrome/chrome"]
    return next((c for c in cands if os.path.isfile(c)), None)


# ── 1 · programas do sistema ───────────────────────────────────────────────────────────────────────────────────────
def sistema():
    """Devolve se dá para usar o pip neste Python."""
    print("\n1 · Programas do sistema (%s)" % SO)
    v = sys.version_info
    py_ok = v >= (3, 11)
    if py_ok:
        ok("Python %d.%d.%d (%s)" % (v[0], v[1], v[2], sys.executable))
    else:
        falta("Python %d.%d: a skill pede 3.11+ (os pacotes não vão para este Python)" % (v[0], v[1]), COMO["python"][SO])
    for p in ("ffmpeg", "ffprobe"):
        c, s = roda([p, "-version"], timeout=60) if shutil.which(p) else (127, "")
        if c == 0:
            ok("%s %s" % (p, (s.split() + ["", "", ""])[2]))
        else:
            falta(p + " no PATH", COMO["ffmpeg"][SO])
    node = shutil.which("node")
    c, s = roda([node, "--version"], timeout=60) if node else (127, "")
    try:
        maior = int(s.strip().lstrip("v").split(".")[0]) if c == 0 else 0
    except ValueError:
        maior = 0
    if maior >= 18:
        ok("Node %s" % s.strip())
    else:
        falta("Node 18+" + (" (este é o %s)" % s.strip() if maior else ""), COMO["node"][SO])
    for p in ("npx", "npm"):
        if shutil.which(p):
            ok(p)
        else:
            falta(p + " (vem com o Node)", COMO["node"][SO])
    cr = chrome()
    if cr:
        ok("Chrome: " + cr)
    else:
        falta("Chrome instalado (o zona_segura.mjs e o erros_js.mjs abrem o index.html nele)", COMO["chrome"][SO])
    if shutil.which("nvidia-smi"):
        aviso("GPU NVIDIA: o faster-whisper a usa sozinho se houver as bibliotecas do CUDA 12 e do cuDNN 9; sem elas, "
              "rode o transcrever_local.py e o ouvir_emendas.py com --cpu (o torch fica na CPU de qualquer jeito)")
    if not py_ok:
        return False
    if roda([sys.executable, "-m", "pip", "--version"], timeout=120)[0]:
        falta("o pip deste Python", "python -m ensurepip --upgrade (Debian/Ubuntu: sudo apt install python3-pip)")
        return False
    return True


# ── 2 · pacotes do Python ──────────────────────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _mapa():
    return importlib.metadata.packages_distributions()  # ~10 s no Windows: uma vez só (de novo depois do pip)


def dists(m):
    """[(pacote, versão)] instalados que trazem o módulo m (o cv2 pode vir do opencv-python ou do -headless)."""
    out = []
    for d in _mapa().get(m, []):
        try:
            out.append((d, importlib.metadata.version(d)))
        except importlib.metadata.PackageNotFoundError:
            pass
    return sorted(set(out))


def pip(nomes, extra=()):
    cmd = [sys.executable, "-m", "pip", "install", *nomes, *extra]
    print("    $ " + " ".join(cmd[1:]), flush=True)
    return subprocess.run(cmd).returncode


def pacotes(instalar, pode_pip):
    print("\n2 · Pacotes do Python")
    if sys.version_info < (3, 11):
        return aviso("pulado: falta o Python 3.11+ (ver acima)")
    faltam = [(m, p) for m, p, _ in PACOTES if importlib.util.find_spec(m) is None]
    for m, p, quem in PACOTES:
        if (m, p) not in faltam:
            ok("%s (%s)" % (", ".join("%s %s" % dv for dv in dists(m)) or m, quem))
    gerenciado = sys.prefix == sys.base_prefix and os.path.exists(
        os.path.join(sysconfig.get_path("stdlib"), "EXTERNALLY-MANAGED"))
    if faltam and instalar and pode_pip and gerenciado:  # PEP 668: o pip recusa instalar no Python do sistema
        venv, py = ((r"py -m venv %USERPROFILE%\.venv-cortes", r"%USERPROFILE%\.venv-cortes\Scripts\python")
                    if SO == "windows" else ("python3 -m venv ~/.venv-cortes", "~/.venv-cortes/bin/python"))
        pode_pip = False
        print("  ⛔ este Python é do sistema e o pip não instala nele: crie um ambiente virtual\n       → %s e rode "
              "%s scripts/instalar.py (e use esse python nos scripts da skill)" % (venv, py))
    if faltam and not (instalar and pode_pip):
        como = "rode este instalador sem --so-conferir" if not instalar else None
        for _, p in faltam:
            falta(p, como)
    elif faltam:
        # o que já existe vai junto com a versão de agora: o pip só instala o que falta e não mexe no resto
        fixos = ["%s==%s" % dv for m, _, _ in PACOTES for dv in dists(m)]
        tch = [p for m, p in faltam if m in ("torch", "torchaudio")]
        resto = [p for m, p in faltam if m not in ("torch", "torchaudio")]
        if tch:
            print("  … %s na versão de CPU: o torch só roda o alinhador MMS_FA, que usa a CPU" % " e ".join(tch))
            pip(tch + fixos, TORCH_CPU)
        if resto:
            print("  … " + ", ".join(resto))
            pip(resto + fixos)
        importlib.invalidate_caches()
        _mapa.cache_clear()
        for m, p in faltam:
            if importlib.util.find_spec(m):
                ok("%s instalado" % ", ".join("%s %s" % dv for dv in dists(m)))
            else:
                falta(p + " (o pip falhou: veja a mensagem acima)")
    if importlib.util.find_spec("yt_dlp") and not shutil.which("yt-dlp"):
        pastas = {sysconfig.get_path("scripts")} | {sysconfig.get_path("scripts", s) for s in sysconfig.get_scheme_names()
                                                     if s.endswith("_user")}
        achou = [d for d in pastas if any(os.path.exists(os.path.join(d, x)) for x in ("yt-dlp", "yt-dlp.exe"))]
        aviso("o comando yt-dlp não está no PATH (o ranking_shorts.py e o analise_shorts.py o chamam direto): ponha "
              + (" ou ".join(achou) if achou else "a pasta de scripts do pip") + " no PATH")


# ── 3 · playwright-core ────────────────────────────────────────────────────────────────────────────────────────────
def playwright(instalar):
    print("\n3 · playwright-core (o zona_segura.mjs e o erros_js.mjs o importam de scripts/)")
    local = os.path.join(AQUI, "node_modules", "playwright-core")
    if os.path.exists(os.path.join(local, "index.mjs")):
        return ok("playwright-core %s em scripts/node_modules" % json.load(open(os.path.join(local, "package.json"),
                                                                              encoding="utf-8"))["version"])
    npm = shutil.which("npm")
    if npm:  # o 2º lugar onde os .mjs procuram: o global
        c, raiz = roda([npm, "root", "-g"], timeout=120)
        if c == 0 and os.path.exists(os.path.join(ultima(raiz), "playwright-core", "index.mjs")):
            return ok("playwright-core global (%s)" % ultima(raiz))
    if not instalar:
        return falta("playwright-core", "rode este instalador sem --so-conferir (npm install playwright-core em scripts/)")
    if not npm:
        return falta("playwright-core (sem o npm)", COMO["node"][SO])
    # --prefix: sem ele, o npm sobe as pastas atrás de um package.json e pode instalar no lugar errado
    cmd = [npm, "install", "--prefix", AQUI, "playwright-core", "--no-audit", "--no-fund"]
    print("    $ npm install --prefix scripts playwright-core", flush=True)
    if subprocess.run(cmd).returncode == 0 and os.path.exists(os.path.join(local, "index.mjs")):
        ok("playwright-core instalado em scripts/node_modules")
    else:
        falta("playwright-core (o npm falhou: veja a mensagem acima)")


# ── 4 · modelos e caches ───────────────────────────────────────────────────────────────────────────────────────────
WHISPER = r"""
import os, sys
from faster_whisper import download_model, WhisperModel
nome, baixar = sys.argv[1], sys.argv[2] == "1"
try:
    p = download_model(nome, local_files_only=True)
    if os.path.exists(os.path.join(p, "model.bin")):
        print("CACHE " + p); sys.exit(0)
except Exception:
    pass
if not baixar:
    print("FALTA"); sys.exit(3)
WhisperModel(nome, device="cpu", compute_type="int8")  # baixa e carrega uma vez
print("BAIXADO " + download_model(nome, local_files_only=True))
"""
MMS = r"""
import os, sys, torch, torchaudio
b = torchaudio.pipelines.MMS_FA
f = os.path.normpath(os.path.join(torch.hub.get_dir(), "checkpoints", os.path.basename(getattr(b, "_path", "model.pt"))))
if os.path.exists(f):
    print("CACHE " + f); sys.exit(0)
if sys.argv[1] != "1":
    print("FALTA"); sys.exit(3)
b.get_model()  # baixa e carrega uma vez
print("BAIXADO " + f)
"""


def modelo(nome, codigo, args, baixar, so_conferir, tamanho):
    if baixar:
        print("  … %s: confere o cache e baixa se faltar (%spode levar alguns minutos)"
              % (nome, tamanho + "; " if tamanho else ""), flush=True)
        r = subprocess.run([sys.executable, "-c", codigo, *args, "1"], stdout=subprocess.PIPE, text=True,
                           encoding="utf-8", errors="replace")  # o stderr passa direto: a barra de progresso
        c, s = r.returncode, r.stdout
    else:
        c, s = roda([sys.executable, "-c", codigo, *args, "0"], timeout=600)
    s = ultima(s)
    if c == 0 and s.startswith("CACHE"):
        ok("%s já no cache, não baixa de novo (%s)" % (nome, s[6:]))
    elif c == 0 and s.startswith("BAIXADO"):
        ok("%s baixado e aquecido (%s)" % (nome, s[8:]))
    elif c == 3 and so_conferir:
        falta("%s não baixado%s" % (nome, " (%s)" % tamanho if tamanho else ""), "rode este instalador sem --so-conferir")
    elif c == 3:
        aviso("%s não baixado (--sem-modelos): baixa sozinho no 1º uso, com internet" % nome)
    else:
        falta("%s: %s" % (nome, s or "erro ao carregar"))


def modelos(instalar, sem_modelos, nome_whisper):
    print("\n4 · Modelos e caches")
    baixar = instalar and not sem_modelos
    if importlib.util.find_spec("faster_whisper"):
        modelo("Whisper " + nome_whisper, WHISPER, [nome_whisper], baixar, not instalar, TAMANHO.get(nome_whisper, ""))
    else:
        aviso("Whisper %s: pulado (falta o faster-whisper, ver acima)" % nome_whisper)
    if importlib.util.find_spec("torch") and importlib.util.find_spec("torchaudio"):
        modelo("MMS_FA (alinhador)", MMS, [], baixar, not instalar, "~1,2 GB")
    else:
        aviso("MMS_FA: pulado (falta o torch/torchaudio, ver acima)")
    if nome_whisper != "large-v3":
        aviso("os scripts usam o large-v3 por padrão: passe --modelo %s ao transcrever_local.py e ao ouvir_emendas.py, "
              "e MODELO=%s ao conferir_fins.py" % (nome_whisper, nome_whisper))
    npx = shutil.which("npx")
    if not npx:
        return aviso("HyperFrames: pulado (falta o npx, ver acima)")
    sim = "--yes" if instalar else "--no-install"
    c, s = roda([npx, sim, HF, "--version"], timeout=900)
    if c == 0:
        ok("HyperFrames %s no cache do npx" % ultima(s))
    else:
        return falta("HyperFrames no cache do npx", ultima(s) if instalar else "rode este instalador sem --so-conferir")
    c, s = roda([npx, sim, HF, "browser", "ensure" if instalar else "path"], timeout=900)
    if c == 0:  # o ensure escreve "Path:    <caminho>" no meio; o path, só o caminho
        ok("Chrome do render do HyperFrames: " + next((x.strip()[5:].strip() for x in s.splitlines()
                                                     if x.strip().startswith("Path:")), ultima(s)))
    else:
        falta("o Chrome do render do HyperFrames", "npx --yes %s browser ensure (%s)" % (HF, ultima(s)))


# ── 5 · autoteste ──────────────────────────────────────────────────────────────────────────────────────────────────
ALINHA = ("import torch, torchaudio.functional as F; F.forced_align(torch.randn(1, 50, 28).log_softmax(-1), "
          "torch.tensor([[3, 5, 7, 2]], dtype=torch.int32), blank=0)")


def autoteste():
    print("\n5 · Autoteste")
    if sys.version_info < (3, 11):
        return aviso("pulado: falta o Python 3.11+ (ver acima)")
    mods =[m for m, _, _ in PACOTES if importlib.util.find_spec(m)]
    if mods:
        c, s = roda([sys.executable, "-c", "import " + ", ".join(mods)], timeout=600)
        if c == 0:
            ok("import de " + ", ".join(mods))
        else:
            falta("import dos pacotes: " + ultima(s))
    if "torchaudio" in mods:  # o torchaudio novo não fixa a versão do torch: a conta do MMS_FA prova que os dois casam
        c, s = roda([sys.executable, "-c", ALINHA], timeout=300)
        ta = (dists("torchaudio") or [("", "?")])[0][1].split("+")[0].rsplit(".", 1)[0]
        if c == 0:
            ok("forced_align do torchaudio (a conta do MMS_FA)")
        else:
            falta("forced_align do torchaudio: " + ultima(s),
                  "o torch não casa com o torchaudio: pip install \"torch==%s.*\" %s" % (ta, " ".join(TORCH_CPU)))
    for nome in ("transcrever_local.py", "sonoplastia.py", "folha_contato.py"):
        c, s = roda([sys.executable, os.path.join(AQUI, nome), "--help"], timeout=300)
        if c == 0:
            ok(nome + " --help")
        else:
            falta(nome + " --help: " + ultima(s))
    node = shutil.which("node")
    if not node:
        return aviso("node --check e o modelo de projeto: pulados (falta o Node, ver acima)")
    for f in sorted(x for x in os.listdir(AQUI) if x.endswith(".mjs")):
        c, s = roda([node, "--check", os.path.join(AQUI, f)], timeout=60)
        if c == 0:
            ok("node --check " + f)
        else:
            falta("node --check %s: %s" % (f, ultima(s)))
    tmp = tempfile.mkdtemp(prefix="cortes_autoteste_")
    try:
        corte = os.path.join(tmp, "corte")
        shutil.copytree(os.path.join(SKILL, "assets", "modelo"), corte)
        c, s = roda([sys.executable, "montar.py"], timeout=300, cwd=corte, env=dict(os.environ, EDICAO_CORTES=SKILL))
        if c != 0 or not os.path.exists(os.path.join(corte, "index.html")):
            return falta("modelo de projeto: python montar.py: " + ultima(s))
        ok("modelo de projeto: " + ultima(s))
        c, s = roda([node, os.path.join(AQUI, "erros_js.mjs"), "index.html"], timeout=300, cwd=corte)
        if c == 0:
            ok("modelo de projeto: erros_js.mjs " + ultima(s).lstrip("✓ "))
        else:
            falta("modelo de projeto: erros_js.mjs: " + ultima(s))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Instala e confere o que a skill edicao-de-cortes precisa (ver o topo do arquivo).")
    ap.add_argument("--so-conferir", action="store_true", help="só confere e diz o que falta, sem instalar nem baixar nada")
    ap.add_argument("--sem-modelos", action="store_true", help="não baixa o Whisper nem o MMS_FA")
    ap.add_argument("--modelo-whisper", default="large-v3", help="large-v3 (padrão) ou medium, para máquina fraca")
    a = ap.parse_args()
    instalar = not a.so_conferir
    print("Skill edicao-de-cortes: %s em %s" % ("só conferindo" if a.so_conferir else "instalação", SKILL))
    pode_pip = sistema()
    pacotes(instalar, pode_pip)
    playwright(instalar)
    modelos(instalar, a.sem_modelos, a.modelo_whisper)
    autoteste()
    if FALTA:
        print("\n⛔ Faltou %d item(ns):" % len(FALTA))
        for f in FALTA:
            print("  - " + f)
        sys.exit(1)
    print("\n✓ pronto para editar" + (" (%d aviso(s) acima, com ⚠)" % len(AVISOS) if AVISOS else ""))


if __name__ == "__main__":
    main()
