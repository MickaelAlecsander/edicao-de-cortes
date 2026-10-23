# -*- coding: utf-8 -*-
"""Corta os blocos de um corte, enquadra o Raul e gera o mapa de tempo das palavras.

    python cortar.py cortes/<slug>      (ou `python <skill>/scripts/cortar.py .` de dentro da pasta do corte)

Lê `cortes/<slug>/cortes.json` e escreve em `cortes/<slug>/assets/`:
  · raul.mp4      os blocos emendados, recortados pelo rosto, na janela de baixo (sem texto);
  · raul.wav      o áudio dos mesmos blocos, normalizado em -15 LUFS (o <audio> do HyperFrames);
  · raul_bruto.wav o mesmo áudio sem normalizar;
  · tempos.json   onde cada bloco caiu na montagem e cada palavra com o tempo NA MONTAGEM.

Cada fronteira é o ponto mais silencioso (RMS de 10 ms) dentro da janela de busca do bloco,
arredondado para fora (início para trás, fim para frente) no quadro. Quem decide onde a palavra acaba é a energia do áudio,
não o Whisper. Os caminhos do cortes.json são relativos à pasta do corte. O travada.py tem de estar na mesma
pasta deste script (ele roda no fim e para o corte se achar imagem parada).
"""
import json
import math
import os
import subprocess
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")   # a mensagem do ⛔ sai pelo stderr
SR = 16000
FADE = 0.015   # o bloco pode pedir "fade_fim" maior quando o fim é emendado sem pausa (C26: "também | Então")
# ⛔ Ponta só em silêncio de verdade: o ponto escolhido tem de estar abaixo de -40 dB (C26, 05/10/2026: o fim do gancho
# caiu num vale de -32 dB que era o fechamento do "t" DENTRO de "inves|tir", e o dono do canal ouviu a palavra comida). Ponta
# acima disso trava o corte. A saída é mudar o bloco para a pausa mais perto; só quando não existe pausa (palavras
# emendadas) a ponta entra em "fala_ok": {"fim": "motivo"} no bloco, com o envelope de 5 ms conferido e o motivo escrito.
# Silêncio não basta no FIM: o fechamento de "p/t/k" dentro da palavra também é silêncio (veja rabo()).
# Fonte com ruído de fundo constante (C95, 22/10/2026: selfie no carro, piso −35 dB, nenhum vale a −40): "limite" no
# cortes.json, ~1 dB acima do piso, o mesmo do `pausas.py --limite`. O rabo()/cabeca() seguem valendo.
LIMITE = -40.0


def audio(src, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", src,
                          "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def silencio(src, a, b):
    """Centro da janela de 10 ms mais quieta entre a e b; devolve (tempo, rms em dB)."""
    x = audio(src, a, b)
    n = SR // 100
    rms = np.sqrt(np.convolve(x * x, np.ones(n) / n, mode="valid") + 1e-12)
    i = int(np.argmin(rms))
    return a + (i + n / 2) / SR, 20 * np.log10(rms[i])


def rabo(src, t):
    """Depois de um FIM, um trecho de voz curto (< 220 ms) seguido de outro vale = a sílaba final da MESMA palavra.

    O corte caiu no fechamento de uma consoante, e não na pausa antes da palavra seguinte (C26, 05/10/2026: "inves|tir",
    "minús|culo", "al|ta"; os três vales tinham de 10 a 70 ms, e o de "minúsculo" estava a -49 dB). Devolve a duração do
    trecho de voz em ms, ou 0. Palavra seguinte curta ("Eu", "é") também acende: aí se confere e se escreve em "fala_ok".
    """
    x = audio(src, t, t + 0.45)
    n = SR // 200
    db = [20 * np.log10(np.sqrt(np.mean(x[i:i + n] ** 2)) + 1e-9) for i in range(0, len(x) - n + 1, n)]
    v0 = next((i for i, d in enumerate(db) if d > -30), None)
    if v0 is None or v0 > 24:                      # voz só depois de 120 ms: o corte está numa pausa de verdade
        return 0
    baixo = 0
    for i in range(v0, len(db)):
        baixo = baixo + 1 if db[i] < -32 else 0
        if baixo >= 4:                              # vale de 20 ms
            voz = (i - 3 - v0) * 5
            return voz if voz < 220 else 0
    return 0


def cabeca(src, t):
    """Antes de um INÍCIO, um trecho de voz curto (< 220 ms) a até 120 ms do corte, com um vale antes dele = a primeira
    sílaba da palavra ficou de fora (C26: o "O" de "O meu conteúdo" vinha antes de um "hum" a -40 dB, que passou por
    silêncio). Devolve a duração do trecho em ms, ou 0."""
    a = max(0.0, t - 0.45)
    x = audio(src, a, t)
    n = SR // 200
    db = [20 * np.log10(np.sqrt(np.mean(x[i:i + n] ** 2)) + 1e-9) for i in range(0, len(x) - n + 1, n)][::-1]
    v0 = next((i for i, d in enumerate(db) if d > -30), None)
    if v0 is None or v0 > 24:
        return 0
    baixo = 0
    for i in range(v0, len(db)):
        baixo = baixo + 1 if db[i] < -32 else 0
        if baixo >= 4:
            voz = (i - 3 - v0) * 5
            return voz if voz < 220 else 0
    return 0


def normalizar(src, dst, alvo=-15.0):
    """Voz em -15 LUFS (loudnorm em duas passadas): com os efeitos por cima, o MP4 fica perto de -14."""
    filtro = "loudnorm=I=%s:TP=-1.5:LRA=9" % alvo
    err = subprocess.run(["ffmpeg", "-nostats", "-i", src, "-af", filtro + ":print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
    medido = ":measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true" % (
        m["input_i"], m["input_tp"], m["input_lra"], m["input_thresh"], m["target_offset"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", filtro + medido + ",aresample=48000",
                    "-ar", "48000", dst], check=True)
    print("voz: %s LUFS → %s LUFS" % (m["input_i"], alvo))


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    pasta = os.path.abspath(sys.argv[1])
    cfg = json.load(open(os.path.join(pasta, "cortes.json"), encoding="utf-8"))
    caminho = lambda p: os.path.normpath(os.path.join(pasta, p))
    # o bloco pode trazer "fonte" e "palavras" próprios (C17 junta dois vídeos); cada fonte vira uma entrada do ffmpeg
    fontes = list(dict.fromkeys(caminho(b.get("fonte", cfg["fonte"])) for b in cfg["blocos"]))
    falas = {}
    fps = 24
    W, H = cfg["janela"]
    r = dict(cfg["recorte"])
    r["h"] = int(round(r["w"] * H / W / 2)) * 2    # a altura sai da janela: mudou a janela, o recorte acompanha
    os.makedirs(os.path.join(pasta, "assets"), exist_ok=True)

    blocos, filtros, rot, off, barrados = [], [], "", 0.0, []
    # cada fonte é UMA entrada do ffmpeg, aberta já no 1º trecho usado ("-ss" antes do "-i" pula direto), e cada trim desconta
    # esse início (o). Antes a entrada abria no 0 e o trim decodificava a live desde o começo: num corte aos 54 min eram ~60 s
    # só para chegar no trecho (10/10/2026, C46: 70 s → 11 s). Uma entrada por bloco estourou a memória (9 decodificadores de
    # 1080p guardando quadros para o concat), e o "-itsoffset" embaralhou o tempo do áudio
    janela = {}
    for b in cfg["blocos"]:
        xs = [b["x"]] + [tr[1] for tr in b.get("trocas", [])]
        ts = [b["ini"][0], b["fim"][1]] + [tr[2] for tr in b.get("trocas", []) if len(tr) > 2] + \
             ([b["de"]] if b.get("de") is not None else []) + [x["congela"] for x in xs if isinstance(x, dict) and "congela" in x]
        f = caminho(b.get("fonte", cfg["fonte"]))
        j0, j1 = janela.get(f, (math.inf, 0.0))
        janela[f] = (min(j0, min(ts) - 2), max(j1, max(ts) + 60))   # +60: o "de" pode pedir imagem até o fim do bloco
    janela = {f: (max(0.0, a), z) for f, (a, z) in janela.items()}
    for i, b in enumerate(cfg["blocos"]):
        src = caminho(b.get("fonte", cfg["fonte"]))
        e = fontes.index(src)
        o = janela[src][0]
        pal = caminho(b.get("palavras", cfg["palavras"]))
        if pal not in falas:
            falas[pal] = json.load(open(pal, encoding="utf-8"))
        palavras = falas[pal]
        t0, db0 = silencio(src, *b["ini"])
        t1, db1 = silencio(src, *b["fim"])
        for lado, db in (("ini", db0), ("fim", db1)):
            if db > cfg.get("limite", LIMITE) and lado not in b.get("fala_ok", {}):
                barrados.append("%s.%s (%.1f dB)" % (b["id"], lado, db))
        cb = cabeca(src, t0)
        if cb and "ini" not in b.get("fala_ok", {}):
            barrados.append("%s.ini (voz de %d ms logo antes do corte, com um vale antes: 1ª sílaba de fora?)" % (b["id"], cb))
        rb = rabo(src, t1)
        if rb and "fim" not in b.get("fala_ok", {}):
            barrados.append("%s.fim (voz de %d ms logo depois do corte e outro vale: sílaba final comida?)" % (b["id"], rb))
        # o VÍDEO anda em quadros: início puxa para ANTES e fim para DEPOIS (arredondar para o mais próximo jogou o
        # início do «a caneta» para dentro do ataque da palavra, 130,645 → 130,667). O ÁUDIO não: ele é cortado no
        # ponto exato de silêncio (s0, s1) e a sobra até o quadro vira silêncio. Antes o áudio seguia o quadro, e
        # na fala corrida esses até 40 ms caíam dentro da palavra vizinha (C05, 02/10: vários fins no meio da palavra).
        s0, s1 = t0, t1
        t0, t1 = math.floor(t0 * fps + 1e-6) / fps, math.ceil(t1 * fps - 1e-6) / fps
        # "respiro": s — silêncio a mais no fim do bloco, com o último quadro parado (C34, 07/10/2026). Serve para a emenda
        # entre frases que ficaria com menos de ~200 ms de silêncio porque a pausa da fonte é curta ("emenda seca" do C29)
        nr = int(round(b.get("respiro", 0) * fps))
        dur = t1 - t0 + nr / fps
        ws = [{"w": p["w"], "s": round(p["s"] - t0 + off, 3), "e": round(min(p["e"], t1) - t0 + off, 3)}
              for p in palavras if s0 - 0.05 <= p["s"] < s1 - 0.05]
        blocos.append({"id": b["id"], "arquivo": src, "fonte": [t0, t1], "audio": [round(s0, 4), round(s1, 4)], "inicio": round(off, 3), "dur": round(dur, 3),
                       "palavras": ws})
        print("%-9s %7.3f → %7.3f (%5.2f s)  silêncio %5.1f / %5.1f dB  «%s … %s»"
              % (b["id"], t0, t1, dur, db0, db1, ws[0]["w"] if ws else "?", ws[-1]["w"] if ws else "?"))
        # "trocas": [[t, x], ...] — a fonte troca de layout no meio do bloco (câmera cheia ↔ painel com
        # slide, lição do C03): o vídeo vira pedaços com recortes diferentes, o áudio segue inteiro
        # [t, x, de]: o terceiro item (e o "de" do bloco, para o 1º pedaço) diz de que instante da fonte vem a imagem do
        # pedaço; sem ele, a imagem é a do mesmo instante do áudio. Serve para pôr na tela quem fala quando a câmera da
        # fonte está em quem escuta (C21: debate com duas câmeras)
        pedacos, ini, x, de = [], t0, b["x"], b.get("de")
        for tr in b.get("trocas", []):
            tt, nx, nde = tr[0], tr[1], (tr[2] if len(tr) > 2 else None)
            # sem arredondar para o quadro de 24: a troca de recorte cai no quadro exato da troca de câmera da fonte
            # (arredondada, ela vinha 1 quadro antes ou depois e mostrava a outra câmera com o recorte errado; C21)
            if t0 < tt < t1:
                pedacos.append((ini, tt, x, de)); ini, x, de = tt, nx, nde
        pedacos.append((ini, t1, x, de))
        for k, (a, z, xx, de) in enumerate(pedacos):
            # o pedaço sai com o número exato de quadros a 24 qps: sem isso, cada pedaço de uma fonte de 30 qps ganhava ou
            # perdia uma fração de quadro, e com muitas trocas a imagem atrasava em relação ao áudio (C21: +8 quadros em 110 s)
            nq = int(round((z - t0) * fps)) - int(round((a - t0) * fps))   # soma exata: o bloco tem round(dur × fps) quadros
            if de is not None:
                a, z = de, de + (z - a)
            if isinstance(xx, dict) and "congela" in xx:
                # a fonte troca o Raul por um gráfico em tela cheia (C25, 05/10: "em baixo sempre que possível foque no
                # Raul… nossa animação em cima é o nosso produto"): fica o último quadro dele, parado, com uma
                # aproximação lenta. Quadro parado não mexe a boca, então não briga com o áudio (o que uma imagem em
                # movimento de outro instante faria, lição do C21). "zoom": 0 para o congelado curto de uma transição da
                # fonte (C37, 08/10: com a aproximação, a volta ao vídeo dava um pulo de escala que parecia defeito)
                cx_, cw_, cy_ = xx["x"]
                ch_ = int(round(cw_ * H / W / 2)) * 2
                filtros.append("[%d:v]trim=start=%.4f:end=%.4f,setpts=PTS-STARTPTS,select='eq(n\\,0)',crop=%d:%d:%d:%d,"
                               "scale=%d:%d:flags=lanczos,zoompan=z='1+%s*on/%d':d=%d:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                               "s=%dx%d:fps=%d,setsar=1[v%d_%d];"
                               % (e, xx["congela"] - o, xx["congela"] + 0.2 - o, cw_, ch_, cx_, cy_, W * 2, H * 2, xx.get("zoom", 0.07), max(1, nq), nq, W, H, fps, i, k))
                continue
            if xx == "cheio":
                # manchete ou imagem em tela cheia na fonte (C20): o quadro inteiro na largura, sobre ele mesmo desfocado
                filtros.append("[%d:v]trim=start=%.4f:end=%.4f,setpts=PTS-STARTPTS,fps=%d,trim=end_frame=%d,setpts=PTS-STARTPTS,split[f%d_%d][g%d_%d];"
                               "[f%d_%d]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,boxblur=30:2,eq=brightness=-0.12[fb%d_%d];"
                               "[g%d_%d]scale=%d:-2:flags=lanczos[gb%d_%d];[fb%d_%d][gb%d_%d]overlay=0:(H-h)/2,setsar=1[v%d_%d];"
                               % (e, a - o, z - o, fps, nq, i, k, i, k, i, k, W, H, W, H, i, k, i, k, W, i, k, i, k, i, k, i, k))
                continue
            # x pode vir como [x, largura]: painel estreito da fonte (o do C03 tem 680 px a partir de x=1240);
            # ou [x, largura, y]: fonte multicâmera, cada plano com o recorte do rosto (C09)
            xx, ww, yy = (list(xx) + [b.get("y", r["y"])])[:3] if isinstance(xx, list) else (xx, r["w"], b.get("y", r["y"]))
            hh = int(round(ww * H / W / 2)) * 2
            # "tapar": [[máscara.png, desde], ...]: texto que a fonte escreve na tela e invade o recorte do Raul (C30: o
            # placar escrito à esquerda; a linha mais comprida passa por cima do ombro dele). A máscara (tamanho da fonte,
            # branco = texto) vai para o removelogo, que refaz SÓ esses pixels com os vizinhos, a partir de "desde" (segundos
            # da fonte). O delogo, que preenche um retângulo com as bordas, deixava um risco do pescoço atravessando o ombro
            tapa = "".join("removelogo=f='%s'%s," % (caminho(m).replace("\\", "/").replace(":", "\\:"),
                                                     ":enable='gte(t,%.3f)'" % (d - a) if d > a else "")
                           for m, d in b.get("tapar", []) if d < z)
            filtros.append("[%d:v]trim=start=%.4f:end=%.4f,setpts=PTS-STARTPTS,fps=%d,trim=end_frame=%d,setpts=PTS-STARTPTS,%scrop=%d:%d:%d:%d,scale=%d:%d:flags=lanczos,setsar=1[v%d_%d];"
                           % (e, a - o, z - o, fps, nq, tapa, ww, hh, xx, yy, W, H, i, k))
        filtros.append("%sconcat=n=%d:v=1:a=0%s[v%d];" % ("".join("[v%d_%d]" % (i, k) for k in range(len(pedacos))), len(pedacos),
                                                          ",tpad=stop_mode=clone:stop=%d" % nr if nr else "", i))
        filtros.append(
            "[%d:a]atrim=start=%.4f:end=%.4f,asetpts=PTS-STARTPTS,afade=t=in:d=%s,afade=t=out:st=%.4f:d=%s,"
            "adelay=delays=%d:all=1,apad=whole_dur=%.4f,atrim=end=%.4f[a%d];"
            % (e, s0 - o, s1 - o, FADE, s1 - s0 - b.get("fade_fim", FADE), b.get("fade_fim", FADE), round((s0 - t0) * 1000), dur, dur, i))
        rot += "[v%d][a%d]" % (i, i)
        off += dur

    if barrados:
        raise SystemExit("⛔ ponta em fala, acima de %d dB: %s\n   Mude o bloco para a pausa mais perto. Sem pausa, confira o "
                         "envelope de 5 ms e escreva o motivo em \"fala_ok\" no bloco." % (cfg.get("limite", LIMITE), ", ".join(barrados)))
    n = len(blocos)
    # a voz sai do filtro direto em PCM (raul_bruto.wav). Antes ela era tirada do AAC do raul.mp4: uma geração de perda a
    # mais, somada ao AAC da fonte, ao do render e ao da prévia, deixava a voz "vibrada", com cara de estourada (C23, 05/10)
    # "espelho": true no cortes.json espelha o vídeo na horizontal (o canal do Raul usa desde 23/10/2026, como teste de RPM:
    # o quadro deixa de ser idêntico ao do canal de origem). Texto gravado na fonte sai ao contrário: fora do recorte ou desfocado
    esp = ",hflip" if cfg.get("espelho", False) else ""
    fc = "".join(filtros) + "%sconcat=n=%d:v=1:a=1[v0][a0];[v0]null%s[v];[a0]asplit=2[a][ab]" % (rot, n, esp)
    mp4 = os.path.join(pasta, "assets", "raul.mp4")
    bruto = os.path.join(pasta, "assets", "raul_bruto.wav")
    # "veryfast" com CRF 14: mesmo tamanho e mesma qualidade que o "slow" num arquivo intermediário, em 1/4 do tempo (10/10)
    ent = [a for f in fontes for a in ("-ss", "%.3f" % janela[f][0], "-t", "%.3f" % (janela[f][1] - janela[f][0]), "-i", f)]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ent, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(fps),
                    "-c:a", "aac", "-b:a", "256k", mp4,
                    "-map", "[ab]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", bruto], check=True)
    normalizar(bruto, os.path.join(pasta, "assets", "raul.wav"))
    json.dump({"duracao": round(off, 3), "blocos": blocos}, open(os.path.join(pasta, "assets", "tempos.json"), "w",
              encoding="utf-8"), ensure_ascii=False, indent=1)
    print("montagem: %.2f s em %d blocos → %s" % (off, n, os.path.relpath(mp4)))
    # ⛔ Imagem do Raul nunca trava com o áudio andando (dono do canal, 10/10/2026: "isso não pode acontecer em hipótese alguma").
    # Pega o quadro parado de propósito ("congela"/PARADO, o do C44) e a fonte que congela a imagem. Onde a fonte troca de
    # câmera, vai a imagem real daquele instante: a outra pessoa bem recortada no rosto, ou o plano aberto. Só um
    # gráfico ou slide em tela cheia ("cheio"), que não é o Raul, pode ficar parado: "parado_ok": "motivo" no bloco.
    from travada import travadas
    cfg_b = {b["id"]: b for b in cfg["blocos"]}
    ruins = []
    for a, z in travadas(mp4):
        bl = next((b for b in blocos if b["inicio"] <= a < b["inicio"] + b["dur"]), blocos[-1])
        if not cfg_b.get(bl["id"], {}).get("parado_ok"):
            ruins.append("%.2f–%.2f s (%.2f s, bloco %s, fonte %.2f)" % (a, z, z - a, bl["id"], bl["fonte"][0] + a - bl["inicio"]))
    if ruins:
        raise SystemExit("⛔ imagem parada no raul.mp4: %s\n   Use a imagem real daquele instante (a outra pessoa recortada no rosto, ou o plano aberto)."
                         % "; ".join(ruins))


if __name__ == "__main__":
    main()
