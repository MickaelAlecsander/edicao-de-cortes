# -*- coding: utf-8 -*-
"""Do render ao arquivo de postar: volume, conferência de imagem travada, prévia e cópia para o TikTok.

    python <skill>/scripts/finalizar.py cortes/<slug>      (ou `.` de dentro da pasta do corte)

Lê `renders/etapa3_bruto.mp4` (de preferência já com o som do `sonoplastia.py --mux`, em FLAC) e escreve em `renders/`:
  · etapa3.mp4        loudnorm em 2 passadas (-14 LUFS, pico -1 dBTP), vídeo copiado, áudio AAC 256k;
  · <cNN>_previa.mp4  720p CRF 28 para a aprovação, com o MESMO áudio do etapa3.mp4 (copiado, sem recomprimir);
  · etapa3_tiktok.mp4 CRF 21, só quando o etapa3.mp4 passa de 240 MB (o de 252 MB derrubou o Chrome no upload, C44).
Para sem gerar a prévia se a metade do Raul tiver imagem parada (`travada.py`, regra de 10/10/2026). Trecho parado dentro de
uma janela de `assets/tela_cheia.json` (a folha cobre o Raul de propósito) não conta. Precisa do ffmpeg/ffprobe no PATH e do
`travada.py` na mesma pasta. Nenhuma API.
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
if __name__ == "__main__" and (len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help")):
    print(__doc__)
    sys.exit(0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from travada import RAUL, travadas  # noqa: E402

ALVO = "I=-14:TP=-1:LRA=11"


def loudnorm(entrada, filtro, *saida):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", entrada, *saida[:-1], "-af", filtro, *saida[-1:]],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    j = err[err.rfind("{"):]
    return json.loads(j[:j.find("}") + 1])


def main():
    pasta = sys.argv[1]
    r = os.path.join(pasta, "renders")
    bruto, final = os.path.join(r, "etapa3_bruto.mp4"), os.path.join(r, "etapa3.mp4")
    if not os.path.exists(bruto):
        raise SystemExit("⛔ falta %s: renderize antes (e rode o sonoplastia.py --mux)" % bruto)
    codec = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "csv=p=0",
                            bruto], capture_output=True, text=True).stdout.strip()
    if codec != "flac":   # o render sai em AAC; o --mux grava o som_mix.wav em FLAC (uma recompressão a menos)
        print("· aviso: o áudio do etapa3_bruto.mp4 é %s, o do render; o sonoplastia.py --mux poupa uma recompressão" % (codec or "nenhum"))
    m = loudnorm(bruto, "loudnorm=%s:print_format=json" % ALVO, "-f", "null", "-")
    f = ("loudnorm=%s:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true:print_format=json"
         % (ALVO, m["input_i"], m["input_tp"], m["input_lra"], m["input_thresh"], m["target_offset"]))
    m2 = loudnorm(bruto, f, "-c:v", "copy", "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", final)
    print("volume: %s → %s LUFS, pico %s dBTP (%s)" % (m["input_i"], m2["output_i"], m2["output_tp"], m2["normalization_type"]))
    t = travadas(final, RAUL)
    # TELA CHEIA (teste de 16/10/2026): enquanto a folha da animação cobre a tela inteira, a metade do Raul fica sem
    # movimento de propósito. O montar.py do corte grava as janelas em assets/tela_cheia.json ([[início, fim], ...], com a
    # subida e a descida da folha); trecho parado inteiro dentro de uma delas não conta
    jan = os.path.join(pasta, "assets", "tela_cheia.json")
    if t and os.path.exists(jan):
        cheia = json.load(open(jan, encoding="utf-8"))
        fora = [p for p in t if not any(a - 0.1 <= p[0] and p[1] <= z + 0.1 for a, z in cheia)]
        if len(fora) < len(t):
            print("· %d trecho(s) parado(s) dentro da tela cheia (a folha cobre o Raul): ok" % (len(t) - len(fora)))
        t = fora
    if t:
        raise SystemExit("⛔ imagem do Raul parada: %s" % "; ".join("%.2f–%.2f s" % p for p in t))
    print("✓ nenhuma imagem parada na metade do Raul")
    previa = os.path.join(r, os.path.basename(os.path.abspath(pasta)).split("-")[0] + "_previa.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", final, "-vf", "scale=720:-2", "-c:v", "libx264", "-crf", "28", "-preset",
                    "medium", "-c:a", "copy", "-movflags", "+faststart", previa], check=True)
    if os.path.getsize(final) > 240 * 2**20:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", final, "-map", "0", "-c:v", "libx264", "-preset", "slow", "-crf", "21",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", os.path.join(r, "etapa3_tiktok.mp4")],
                       check=True)
    for a in sorted(os.listdir(r)):
        if a.endswith(".mp4"):
            print("%-22s %6.1f MB" % (a, os.path.getsize(os.path.join(r, a)) / 2**20))


if __name__ == "__main__":
    main()
