# -*- coding: utf-8 -*-
"""Pesquisa e download de fontes (YouTube, TikTok, Instagram) sem tomar bloqueio. Um script só, sem API.

    python baixar.py <comando> ... [--raiz PASTA] [--folga SEGUNDOS]

    listar <@canal|url|ytsearchN:termos> [--aba videos|shorts|streams] [--n 60]
        id|duração|views|data|título → _pesquisa/lista_<nome>.txt  (o modo plano do YouTube não traz a data)
    info <id|url>
        título, duração, data, idioma FALADO, canal, channel_id (é ele que lista o TikTok) e o começo da descrição
    legenda <id|url> [<id> ...] [--langs REGEX]
        só a legenda ORIGINAL, escolhida pelo idioma falado → _pesquisa/legendas/<id>.<faixa>.vtt e <id>.txt
    audio <id|url>
        o áudio inteiro, Opus 251 do YouTube → _fontes/<id>_audio.webm
    video <id|url> [--altura 1080]
        o vídeo inteiro com o AAC 140 (a referência do atraso) → _fontes/<id>.mp4; abaixo de 1080, <id>_<A>p.mp4 (só olhar)
    opus <id>
        audio + video, mede o atraso do AAC por correlação em 3 pontos e monta _fontes/<id>_opus.mkv (vídeo do .mp4 +
        Opus com -itsoffset); confere o resíduo e grava _fontes/<id>_opus.json
    somar <palavras.json> <atraso_s> [saida.json]
        soma o atraso nos tempos das palavras transcritas no .webm (saída padrão: <nome>_mkv.json)
    liberar <id> [<id> ...]
        move _fontes/<id>* para _lixeira/fontes/ (nunca apaga), a não ser que um corte sem render final use o id
    teste
        confere a lógica sem rede: sinal da correlação, escolha da legenda, vtt2txt

Pastas: _fontes/, _pesquisa/ e _lixeira/ dentro de --raiz (padrão: o diretório atual).

O que o script faz sozinho, e por quê:
  · UM pedido por vez na máquina inteira (trava em %TEMP%\\baixar_yt.trava) e uma FOLGA entre pedidos (10 s), mesmo
    entre execuções diferentes. Rajada marca o IP com 429, e IP marcado só cede com tempo (projeto de futebol,
    18/09/2026: três dias cegos; nada destravou: nove player_client, cookies de seis navegadores, PO token).
  · O cliente por TIPO de pedido. Listar e ler título: `web_safari,mweb` (é ali que mora o 429 de rajada). Legenda e
    mídia: o cliente PADRÃO, porque o anti-bot responde "has no subtitles" para todo vídeo, mente 360p e quebra o
    download com "GVS PO Token" (18/09; no canal do Raul, 13/10: a legenda com o anti-bot pediu PO Token). Se o padrão
    pedir "Sign in to confirm", a legenda tenta uma vez o `web_embedded` (23/09).
  · Legenda só a faixa ORIGINAL (`pt.*-orig`): a traduzida sai por outro caminho, muito mais estrangulado (13/10: o
    `pt` traduzido deu 429). `--sub-langs` é regex com casamento inteiro, e casa várias faixas: a escolha é pelo idioma
    falado, nunca o primeiro .vtt da pasta (23/09: 50 vídeos lidos em árabe).
  · 3 vídeos seguidos sem legenda param o lote: o bloqueio se disfarça de "não existe legenda".
  · 429 para tudo na hora, com aviso. 403 no download de mídia tenta de novo UMA vez (link expirado; o 2º pedido passou).
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import namedtuple

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vtt2txt  # noqa: E402

YTDLP = [shutil.which("yt-dlp")] if shutil.which("yt-dlp") else [sys.executable, "-m", "yt_dlp"]
# o yt-dlp novo precisa de um runtime de JS para o YouTube; o padrão é o Deno, e o Node só entra se for pedido
JS = [] if shutil.which("deno") or not shutil.which("node") else ["--js-runtimes", "node"]
ANTI = ["--extractor-args", "youtube:player_client=web_safari,mweb"]
EMBUTIDO = ["--extractor-args", "youtube:player_client=web_embedded;skip=hls,dash", "--ignore-no-formats-error"]
TRAVA = os.path.join(tempfile.gettempdir(), "baixar_yt.trava")
ULTIMO = os.path.join(tempfile.gettempdir(), "baixar_yt.ultimo")
FOLGA = 10.0
RAIZ = FONTES = PESQ = "."
SR = 48000


# ── um pedido de cada vez ───────────────────────────────────────────────────────────────────────────────────────────
def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return 0.0


def _pega_trava():
    avisou = False
    while True:
        try:
            os.close(os.open(TRAVA, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            return
        except FileExistsError:
            if time.time() - _mtime(TRAVA) > 3 * 3600:  # sobra de processo morto
                try:
                    os.remove(TRAVA)
                except OSError:
                    pass
                continue
            if not avisou:
                print("· outro pedido do yt-dlp em andamento nesta máquina: esperando a vez (trava: %s)" % TRAVA, flush=True)
                avisou = True
            time.sleep(3)


def rabo(err, n=3):
    return " | ".join([l for l in (err or "").splitlines() if l.strip()][-n:])


def pedido(a, timeout=None, cliente=()):
    """Um pedido ao yt-dlp: espera a vez, respeita a folga desde o último pedido e para tudo no 429."""
    _pega_trava()
    try:
        falta = FOLGA - (time.time() - _mtime(ULTIMO))
        if falta > 0:
            time.sleep(falta)
        r = subprocess.run(YTDLP + JS + list(cliente) + ["--no-progress"] + a, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    finally:
        open(ULTIMO, "w").close()
        try:
            os.remove(TRAVA)
        except OSError:
            pass
    err = r.stderr or ""
    if "HTTP Error 429" in err or "Too Many Requests" in err:
        sys.exit("⛔ HTTP 429: o YouTube marcou este IP. Pare TODOS os pedidos (de todas as sessões) e espere: 10 min no\n"
                 "   mínimo, às vezes horas. Só o tempo destrava; trocar de cliente, cookies do navegador e PO token já\n"
                 "   foram testados e não resolveram. Na volta, um pedido por vez.")
    if re.search(r"video (is )?unavailable", err, re.I):
        print("⚠ vídeo indisponível. Antes de desistir, confira maiúsculas e minúsculas do id: Z99ri8YcCsY e z99ri8YcCsY\n"
              "  são vídeos diferentes (17/10: o Z maiúsculo dava indisponível). Copie o id da lista, não redigite.")
    return r


def baixa(a):
    """Download de mídia, no cliente padrão. Devolve o caminho final."""
    for vez in (1, 2):
        r = pedido(["--print", "after_move:filepath"] + a)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().splitlines()[-1]
        if "403" in r.stderr and vez == 1:
            print("· 403 no download (link expirado): tentando de novo uma vez, depois da folga", flush=True)
            continue
        if "confirm you" in r.stderr:
            sys.exit("⛔ o YouTube pediu login (\"Sign in to confirm you're not a bot\"): é bloqueio por rajada. Espere;\n"
                     "   não passe cookies nem senha.")
        sys.exit("✗ download falhou: " + rabo(r.stderr))


# ── ids e nomes ─────────────────────────────────────────────────────────────────────────────────────────────────────
YT = re.compile(r"(?:v=|youtu\.be/|shorts/|live/|embed/)([A-Za-z0-9_-]{11})")


def alvo(x):
    """(url, id, é_youtube). Id do YouTube diferencia maiúscula de minúscula; para outra rede, o id vem do yt-dlp."""
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", x):
        return "https://www.youtube.com/watch?v=" + x, x, True
    m = YT.search(x)
    if m and "youtu" in x:
        return x, m.group(1), True
    return x, None, False


def prefixo(url):
    return "ig_" if "instagram.com" in url else "tt_" if "tiktok.com" in url else ""


def ja_tem(nome_inicio):
    """arquivo em _fontes/ que começa EXATAMENTE assim (caixa exata; o glob do Windows ignora a caixa)"""
    for n in sorted(os.listdir(FONTES)):
        if n.startswith(nome_inicio) and not n.endswith((".part", ".ytdl")):
            return os.path.join(FONTES, n)
    return None


# ── legenda ─────────────────────────────────────────────────────────────────────────────────────────────────────────
class Faixa(namedtuple("Faixa", "caminho idioma todas")):
    __slots__ = ()

    def __str__(self):
        return self.idioma + (" (de %d faixas: %s)" % (len(self.todas), ", ".join(self.todas)) if len(self.todas) > 1 else "")


def posto(cod, falado=""):
    """Chave de ordenação de uma faixa: a do idioma FALADO primeiro, depois pt, en, es; dentro, a -orig antes."""
    raiz = cod.split("-")[0].lower()
    raiz = "pt" if raiz == "por" else raiz  # o TikTok escreve por-PT
    f = (falado or "").split("-")[0].lower()
    ordem = ([f] if f and f != "na" else []) + [l for l in ("pt", "en", "es") if l != f]
    return (ordem.index(raiz) if raiz in ordem else len(ordem), 0 if cod.endswith("-orig") else 1, cod)


def escolhe_legenda(pasta, vid, falado=""):
    """Qual dos <vid>.<faixa>.vtt se lê. NUNCA o primeiro da pasta: na ordem alfabética, ar-orig vem antes de pt."""
    achados = {}
    for n in os.listdir(pasta):
        m = re.match(re.escape(vid) + r"\.([A-Za-z0-9-]+)\.(vtt|srt)$", n)
        if m:
            achados[m.group(1)] = os.path.join(pasta, n)
    if not achados:
        return None
    ordem = sorted(achados, key=lambda c: posto(c, falado))
    return Faixa(achados[ordem[0]], ordem[0], ordem)


def legenda(ids, langs):
    pasta = os.path.join(PESQ, "legendas")
    os.makedirs(pasta, exist_ok=True)
    faltas = 0
    for x in ids:
        url, vid, yt = alvo(x)
        regex = langs or ("pt.*-orig" if yt else "pt.*|por.*")
        a = ["--skip-download", "--no-simulate", "--print", "%(id)s|%(language)s", "--write-auto-subs", "--write-subs",
             "--sub-langs", regex, "--sub-format", "vtt/srt/best", "-o", os.path.join(pasta, "%(id)s.%(ext)s"), url]
        r = pedido(a, 300)
        if yt and "confirm you" in r.stderr:
            print("· o cliente padrão pediu login: tentando o web_embedded (só para legenda)", flush=True)
            r = pedido(a, 300, EMBUTIDO)
        campos = ((r.stdout.strip().splitlines() or ["|"])[-1] + "|").split("|")
        vid, falado = vid or campos[0], campos[1]
        f = escolhe_legenda(pasta, vid, falado) if vid else None
        if not f:
            faltas += 1
            print("✗ %s: sem legenda em /%s/ (idioma falado: %s). %s" % (vid or x, regex, falado or "?", rabo(r.stderr, 1)))
            if faltas >= 3:
                sys.exit("⛔ 3 vídeos seguidos sem legenda. Pode ser bloqueio disfarçado de \"não existe legenda\": peça a\n"
                         "   legenda de um vídeo de CONTROLE que sabidamente tem. Se ele também falhar, pare e espere.")
            continue
        faltas = 0
        destino = os.path.join(pasta, vid + ".txt")
        texto = vtt2txt.parse(f.caminho)
        with open(destino, "w", encoding="utf-8") as s:
            s.write("# %s · faixa %s · idioma falado %s\n%s\n" % (vid, f, falado or "?", texto))
        print("✓ %s: faixa %s → %s (%d blocos de ~15 s)" % (vid, f, destino, texto.count("\n") + 1 if texto else 0))
        if falado and falado != "NA" and f.idioma.split("-")[0] not in (falado.split("-")[0], "por"):
            print("  ⚠ a faixa lida não é a do idioma falado (%s): pode ser dublagem automática. Use --langs." % falado)


# ── listar e ler ────────────────────────────────────────────────────────────────────────────────────────────────────
def listar(canal, aba, n):
    url = "https://www.youtube.com/%s/%s" % (canal, aba) if canal.startswith("@") else canal
    r = pedido(["--flat-playlist", "--playlist-end", str(n), "--print",
                "%(id)s|%(duration_string)s|%(view_count)s|%(upload_date)s|%(title)s", url], 600, ANTI)
    linhas = [l for l in r.stdout.splitlines() if l.strip()]
    if not linhas:
        print("✗ nada listado: " + rabo(r.stderr))
        if "tiktok.com/@" in url:
            print("  O @ direto do TikTok costuma falhar: rode `info <url de um vídeo da conta>` e liste com\n"
                  "  `listar tiktokuser:<channel_id>`.")
        if "instagram.com" in url:
            print("  Perfil do Instagram não lista sem login: use o navegador logado (references/pesquisa-e-download.md).")
        sys.exit(1)
    nome = re.sub(r"[^\w@-]+", "_", url.split("://")[-1]).strip("_")[-60:]
    saida = os.path.join(PESQ, "lista_%s.txt" % nome)
    open(saida, "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("\n".join(linhas))
    print("\n%d itens → %s" % (len(linhas), saida))


def info(x):
    url, _, _ = alvo(x)
    r = pedido(["--skip-download", "--print",
                "id: %(id)s\ntítulo: %(title)s\nduração: %(duration_string)s\ndata: %(upload_date)s\n"
                "idioma falado: %(language)s\ncanal: %(channel)s (%(uploader_id)s)\nchannel_id: %(channel_id)s\n"
                "views: %(view_count)s\ndescrição: %(description).400s", url], 300, ANTI)
    print(r.stdout.strip() or "✗ " + rabo(r.stderr))


# ── mídia ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def audio(x):
    url, vid, yt = alvo(x)
    if vid and ja_tem(vid + "_audio."):
        print("· já está em _fontes: " + ja_tem(vid + "_audio."))
        return ja_tem(vid + "_audio.")
    f = baixa(["-f", "251/bestaudio[ext=webm]/bestaudio", "-o",
               os.path.join(FONTES, (vid or prefixo(url) + "%(id)s") + "_audio.%(ext)s"), url])
    print("✓ " + f)
    return f


def video(x, altura=1080):
    url, vid, yt = alvo(x)
    suf = "" if altura >= 1080 else "_%dp" % altura
    if vid and ja_tem(vid + suf + ".mp4"):
        print("· já está em _fontes: " + ja_tem(vid + suf + ".mp4"))
        return ja_tem(vid + suf + ".mp4")
    # res = a MENOR dimensão: 1080 pega o 1920x1080 e também o short em pé (1080x1920)
    f = baixa(["-f", "bv*+140/bv*+ba/b" if yt else "bv*+ba/b", "-S", "res:%d" % altura, "--merge-output-format", "mp4",
               "-o", os.path.join(FONTES, (vid or prefixo(url) + "%(id)s") + suf + ".%(ext)s"), url])
    print("✓ " + f)
    return f


def duracao(arq):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                                capture_output=True, text=True, check=True).stdout.strip())


def pcm(arq, t, dur):
    """mono 48 kHz de [t, t+dur]. O -ss vai DEPOIS do -i: no AAC, antes do -i errou ~60 ms (C44)."""
    import numpy as np
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-ss", "%.3f" % t, "-t", "%.3f" % dur, "-map", "0:a:0",
                        "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def atraso(a, b, maximo=0.5):
    """Quanto `a` vem ATRASADO em relação a `b`, em segundos (a[n] ≈ b[n − d]), e a força da correlação (0 a 1)."""
    import numpy as np
    n = len(a) + len(b)
    c = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
    m = int(maximo * SR)
    lags = np.r_[0:m + 1, -m:0]
    v = np.r_[c[:m + 1], c[n - m:]]
    i = int(np.argmax(v))
    return lags[i] / SR, float(v[i] / (np.sqrt(np.dot(a, a) * np.dot(b, b)) + 1e-12))


def opus(x):
    url, vid, yt = alvo(x)
    if not yt:
        sys.exit("✗ o opus é só para o YouTube (TikTok e Instagram têm uma faixa só: use `video`).")
    mp4, webm = video(vid), audio(vid)
    mkv = os.path.join(FONTES, vid + "_opus.mkv")
    d = duracao(mp4)
    janela = min(20.0, d / 4)
    pontos = [max(0.0, d * f - janela / 2) for f in (0.25, 0.5, 0.75)]
    medidas = []
    for t in pontos:
        s, forca = atraso(pcm(mp4, t, janela), pcm(webm, t, janela))
        medidas.append(s)
        print("· %7.1f s: o AAC do .mp4 vem %+.2f ms em relação ao Opus (força %.2f)%s"
              % (t, s * 1000, forca, "  ⚠ fraca: trecho sem voz?" if forca < 0.5 else ""), flush=True)
    medidas.sort()
    desvio = medidas[1]
    if medidas[-1] - medidas[0] > 0.002:
        print("⚠ os 3 pontos discordam em mais de 2 ms: confira antes de usar (pode ser corte na fonte ou trecho sem voz)")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4, "-itsoffset", "%.4f" % desvio, "-i", webm,
                    "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", mkv], check=True)
    residuo = max(abs(atraso(pcm(mp4, t, janela), pcm(mkv, t, janela))[0]) for t in pontos)
    json.dump({"atraso_s": round(desvio, 5), "residuo_ms": round(residuo * 1000, 2), "pontos_s": [round(t, 1) for t in pontos],
               "mp4": os.path.basename(mp4), "webm": os.path.basename(webm)},
              open(os.path.join(FONTES, vid + "_opus.json"), "w", encoding="utf-8"), indent=1)
    print("%s %s: atraso %.2f ms, resíduo no .mkv %.2f ms" % ("✓" if residuo < 0.001 else "⚠", mkv, desvio * 1000, residuo * 1000))
    print("  Palavras transcritas no .webm: `somar <palavras.json> %.4f`. Transcritas do próprio .mkv: nada a somar." % desvio)


def somar(arq, d, saida=None):
    chaves = ("s", "e", "start", "end", "ini", "fim")

    def anda(o):
        if isinstance(o, list):
            return [anda(x) for x in o]
        if isinstance(o, dict):
            return {k: round(v + d, 4) if k in chaves and isinstance(v, (int, float)) and not isinstance(v, bool) else anda(v)
                    for k, v in o.items()}
        return o
    saida = saida or re.sub(r"\.json$", "", arq) + "_mkv.json"
    json.dump(anda(json.load(open(arq, encoding="utf-8"))), open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("✓ %s (+%.4f s)" % (saida, d))


def liberar(ids):
    lixo = os.path.join(RAIZ, "_lixeira", "fontes")
    os.makedirs(lixo, exist_ok=True)
    for vid in ids:
        uso = [os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(RAIZ, "cortes", "*", "cortes.json"))
               if vid in open(p, encoding="utf-8").read()
               and not os.path.exists(os.path.join(os.path.dirname(p), "renders", "etapa3.mp4"))]
        if uso:
            print("· %s fica: %s ainda não tem o render final" % (vid, ", ".join(uso)))
            continue
        arqs = [n for n in os.listdir(FONTES) if n.startswith(vid)]
        for n in arqs:
            shutil.move(os.path.join(FONTES, n), os.path.join(lixo, n))
            print("→ _lixeira/fontes/" + n)
        if not arqs:
            print("· %s: nada em _fontes/" % vid)
    print("Nada foi apagado: quem esvazia a _lixeira/ é o dono do canal.")


# ── conferência sem rede ────────────────────────────────────────────────────────────────────────────────────────────
def teste():
    import numpy as np
    b = np.random.default_rng(1).standard_normal(SR * 3).astype(np.float32)
    k = int(round(0.0353 * SR))
    a = np.r_[np.zeros(k, np.float32), b[:-k]]  # `a` é o `b` atrasado 35,3 ms, como o AAC em relação ao Opus
    s, forca = atraso(a, b)
    assert abs(s - k / SR) < 1e-9 and forca > 0.9, (s, forca)
    assert abs(atraso(b, a)[0] + k / SR) < 1e-9
    with tempfile.TemporaryDirectory() as p:
        for c in ("ar-orig", "en-US-orig", "pt-BR-orig", "pt"):
            open(os.path.join(p, "abcdefghijk.%s.vtt" % c), "w").close()
        assert escolhe_legenda(p, "abcdefghijk").idioma == "pt-BR-orig"
        assert escolhe_legenda(p, "abcdefghijk", "en").idioma == "en-US-orig"
        v = os.path.join(p, "x.vtt")
        open(v, "w", encoding="utf-8").write(
            "WEBVTT\n\n00:01.000 --> 00:03.000\no juro &amp; a dívida\n\n00:03.000 --> 00:03.010\no juro &amp; a dívida\n\n"
            "00:03.010 --> 00:05.000\no juro &amp; a dívida\n<00:03.500><c>do país</c>\n\n"
            "01:02:03.000 --> 01:02:05.000\nfim\n")
        assert vtt2txt.parse(v) == "[00:01] o juro & a dívida do país\n[1:02:03] fim", vtt2txt.parse(v)
    print("✓ teste ok: correlação (sinal e valor), escolha da legenda, vtt2txt")


def main():
    global RAIZ, FONTES, PESQ, FOLGA
    comum = argparse.ArgumentParser(add_help=False)
    comum.add_argument("--raiz", default=".", help="pasta do projeto (padrão: a atual)")
    comum.add_argument("--folga", type=float, default=FOLGA, help="segundos entre dois pedidos (padrão 10)")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("listar", parents=[comum], help="lista um canal, uma aba, uma playlist ou uma busca")
    p.add_argument("canal")
    p.add_argument("--aba", default="videos", choices=["videos", "shorts", "streams"])
    p.add_argument("--n", type=int, default=60)
    sub.add_parser("info", parents=[comum], help="metadados de um vídeo").add_argument("id")
    p = sub.add_parser("legenda", parents=[comum], help="só a legenda, lida como texto")
    p.add_argument("ids", nargs="+")
    p.add_argument("--langs", help="regex do --sub-langs (padrão pt.*-orig no YouTube)")
    sub.add_parser("audio", parents=[comum], help="o áudio inteiro (Opus)").add_argument("id")
    p = sub.add_parser("video", parents=[comum], help="o vídeo inteiro (mp4 com o AAC)")
    p.add_argument("id")
    p.add_argument("--altura", type=int, default=1080, help="menor dimensão máxima (360 para só olhar)")
    sub.add_parser("opus", parents=[comum], help="webm + mp4 + atraso medido → _opus.mkv").add_argument("id")
    p = sub.add_parser("somar", parents=[comum], help="soma o atraso nos tempos das palavras")
    p.add_argument("palavras")
    p.add_argument("atraso", type=float)
    p.add_argument("saida", nargs="?")
    sub.add_parser("liberar", parents=[comum], help="fonte para a _lixeira/fontes/").add_argument("ids", nargs="+")
    sub.add_parser("teste", parents=[comum], help="confere a lógica sem rede")
    a = ap.parse_args()
    RAIZ, FOLGA = os.path.abspath(a.raiz), a.folga
    FONTES, PESQ = os.path.join(RAIZ, "_fontes"), os.path.join(RAIZ, "_pesquisa")
    if a.cmd not in ("teste", "somar"):
        os.makedirs(FONTES, exist_ok=True)
        os.makedirs(PESQ, exist_ok=True)
    {"listar": lambda: listar(a.canal, a.aba, a.n), "info": lambda: info(a.id), "legenda": lambda: legenda(a.ids, a.langs),
     "audio": lambda: audio(a.id), "video": lambda: video(a.id, a.altura), "opus": lambda: opus(a.id),
     "somar": lambda: somar(a.palavras, a.atraso, a.saida), "liberar": lambda: liberar(a.ids), "teste": teste}[a.cmd]()


if __name__ == "__main__":
    main()
