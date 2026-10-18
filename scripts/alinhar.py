# -*- coding: utf-8 -*-
"""Alinhador forçado (torchaudio MMS_FA): início/fim de cada palavra de um texto JÁ conhecido.

    python alinhar.py <fonte> <ini> <fim> "<texto>" [--letras] [--pausas]

Não transcreve: o texto vem pronto (o do Whisper local conferido no ouvido, ou o TEXTO do roteiro); o modelo só diz ONDE
cada letra está. É o juiz de tempo desde 12/10/2026 (C67): nas 6 pontas difíceis, os tempos de palavra bateram com 0 a
17 ms de erro e o vale DENTRO de "ami|go" saiu certo, onde o Whisper esticava palavra sobre a pausa e completava palavra
cortada. O `pausas.py` usa ele para dizer se um vale do áudio cai ENTRE duas palavras ou DENTRO de uma. Tempos em segundos
absolutos da fonte. O modelo olha o áudio em quadros de 20 ms, então nada aqui é mais fino que 20 ms.
  · "*" no texto = fala que não está no texto (pedaço de palavra na ponta da janela, fala de outra pessoa, trecho
    incerto). Ex.: "* judicial já fica e os fornecedores dessa empresa *". Só no trecho de fato incerto: "*" no lugar
    de palavra conhecida deixa o modelo puxar a vizinha (no C67 o "m" de "sim" foi parar no "mas" seguinte).
  · Acento e pontuação saem sozinhos (MMS_FA só conhece a-z e '); número vai por extenso sozinho (`por_extenso`).
  · O "h" do começo da palavra sai (é mudo em português): no C84 o modelo punha o "h" de "Herança" dentro da pausa de
    −60 dB antes da palavra, e o vale saía "DENTRO de Herança (entre 'h' e 'e')", um falso ✗.
  · Letra dobrada vira uma ("Lemann" → "leman", "isso" → "iso"): o CTC exige um branco entre duas letras iguais, e no
    C84 a 2ª letra do "nn" caía depois da pausa seguinte, um falso "DENTRO de Lemann (entre 'n' e 'n')".
  · score = probabilidade média do modelo nas letras da palavra (0 a 1). Abaixo de 0,1 o modelo NÃO achou a palavra
    (não foi dita, foi dita diferente, ou é outra voz por cima): ele a espreme num canto qualquer, e o rótulo do vale
    vizinho sai marcado com "??" (re-ouvir antes de confiar).
  · Duas vozes: o MMS é fraco no apresentador (C67: 0,02 no "alto" do Vilela). Com duas pessoas, quem fala se confere
    na imagem e no ouvido, e o rótulo perto da troca de voz vale menos.
  · --letras mostra o tempo de cada letra (útil para sílaba: o "g" de "ami|go"). É o pico de 20 ms em que o modelo
    "dispara" a letra, não a duração do som; em p/t/k o pico costuma cair na oclusão (silêncio) antes do estouro.
  · --pausas lista os vales do áudio (envelope de 5 ms abaixo de −40 dB, 20 ms ou mais) e o rótulo de cada um.
    O FIM que o modelo dá é o começo do último som (CTC marca a letra num pico de 20 ms), não o fim acústico: a vogal
    final costuma seguir 0,1–0,3 s depois. Por isso a ponta de corte vem do vale, e o alinhador só diz qual vale serve.
Modelo: 1,2 GB em ~/.cache/torch/hub/checkpoints/model.pt (baixa sozinho na 1ª vez).
"""
import re
import subprocess
import sys
import unicodedata

import numpy as np
import torch
import torchaudio

SR = 16000
FRACA = 0.1  # score abaixo disso = o modelo não achou a palavra (texto ≠ áudio, ou outra voz)
BUNDLE = torchaudio.pipelines.MMS_FA
_modelo = None
UN = ("zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete "
      "dezoito dezenove").split()
DEZ = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
CEM = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()


def extenso(n):
    if n < 20:
        return UN[n]
    if n < 100:
        return DEZ[n // 10] + ("" if n % 10 == 0 else " e " + UN[n % 10])
    if n < 1000:
        return "cem" if n == 100 else CEM[n // 100] + ("" if n % 100 == 0 else " e " + extenso(n % 100))
    for base, um, varios in ((10 ** 9, "um bilhão", "bilhões"), (10 ** 6, "um milhão", "milhões"), (1000, "mil", "mil")):
        if n >= base:
            q, r = divmod(n, base)
            cab = um if q == 1 else extenso(q) + " " + varios
            return cab if r == 0 else cab + (" e " if r < 100 or r % 100 == 0 else " ") + extenso(r)


def por_extenso(texto):
    """"R$90" → "noventa reais", "13,75%" → "treze vírgula setenta e cinco por cento", "1.700" → "mil e setecentos"."""
    def num(m):
        inteiro, _, dec = m.group().partition(",")
        s = extenso(int(inteiro.replace(".", "")))
        if dec:
            s += " vírgula" + " zero" * (len(dec) - len(dec.lstrip("0"))) + (" " + extenso(int(dec)) if dec.strip("0") else "")
        return s
    texto = re.sub(r"R\$\s*(\d[\d.]*(?:,\d+)?(?:\s+(?:mil|milh\w+|bilh\w+))?)", r"\1 reais", texto)
    texto = re.sub(r"(\d[\d.]*(?:,\d+)?)\s*%", r"\1 por cento", texto)
    return re.sub(r"\d[\d.]*(?:,\d+)?", num, texto)


def normaliza(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if c in BUNDLE.get_dict())  # a-z, ' e * ; tira acento, pontuação e o resto
    w = re.sub(r"^h(?=[aeiou])", "", w)  # "h" inicial é mudo ("herança" soa "erança"; C84)
    # letra dobrada vira uma: o CTC exige um "branco" entre duas letras iguais e empurrava a 2ª para depois da pausa
    # ("Leman|n" no C84 saía DENTRO de Lemann; o mesmo valia para isso, carro, nosso), e rr/ss são um som só
    return re.sub(r"([a-z])\1+", r"\1", w)

def audio(src, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % a, "-t", "%.3f" % (b - a), "-i", src, "-vn", "-ac", "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return torch.from_numpy(np.frombuffer(raw, np.int16).astype(np.float32) / 32768).unsqueeze(0)


def alinhar(src, a, b, texto):
    """[{w, s, e, score, letras: [(letra, s, e, score), ...]}] em segundos absolutos; "*" sai como w="*"."""
    global _modelo
    _modelo = _modelo or BUNDLE.get_model()  # com a coluna "*" (fala fora do texto)
    palavras = [(w, normaliza(w)) for w in por_extenso(texto).split()]
    palavras = [(w, n) for w, n in palavras if n]
    wav = audio(src, a, b)
    with torch.inference_mode():
        em, _ = _modelo(wav)
    spans = BUNDLE.get_aligner()(em[0], BUNDLE.get_tokenizer()([n for _, n in palavras]))
    q = wav.size(1) / em.size(1) / SR  # segundos por quadro (~0,02)
    out = []
    for (w, n), sp in zip(palavras, spans):
        score = sum(s.score * len(s) for s in sp) / sum(len(s) for s in sp)
        out.append({"w": w, "s": round(a + sp[0].start * q, 3), "e": round(a + sp[-1].end * q, 3), "score": round(score, 3),
                    "letras": [(c, round(a + s.start * q, 3), round(a + s.end * q, 3), round(s.score, 2)) for c, s in zip(n, sp)]})
    return out


def rotulo(p0, p1, palavras):
    """Onde o vale [p0, p1] cai: {"dentro", "antes", "depois", "ate", "fracas", "avisos", "txt"}.

    dentro = palavra com letra antes do vale E letra depois dele (oclusão do "g" de "ami|go", do "t" de "jei|to"): cortar
    ali come a palavra. O pico da última letra às vezes cai uns 20–60 ms DENTRO do silêncio seguinte (o "-cios" de
    "negócios" no C67): isso não conta como "depois", então o vale fica "entre".
    ate = a 1ª palavra achada depois do vale já começa dentro dele (f, s, x fracos ou oclusão de p/t/k): a ponta tem de
    ficar antes desse instante. Palavra fraca (score < FRACA) não conta aqui: o modelo a espreme em qualquer canto
    (o "as" do C67, que não foi dito, caiu dentro do vale depois de "brasileiros"). Letra fraca também não: o começo é
    a 1ª letra que o modelo ouviu de verdade (no C67 o "v" de "Você" saiu com 0,00 colado no fim de "empréstimo", meio
    segundo antes do resto da palavra, e fechava a pausa de 520 ms; os começos de verdade no vale deram 0,92 a 1,00).
    fracas = palavras perto que o modelo não achou no áudio: "??", re-ouvir antes de confiar no rótulo."""
    ws = [w for w in palavras if w["w"] != "*"]
    w = next((w for w in ws if any(l[1] < p0 + 0.01 for l in w["letras"]) and any(l[1] >= p1 - 0.02 for l in w["letras"])), None)
    ant = [v for v in ws if v["s"] < p0]
    dep = [v for v in ws if v["s"] >= p0]
    r = {"dentro": w and w["w"], "antes": [v["w"] for v in ant[-2:]], "depois": [v["w"] for v in dep[:2]], "ate": None,
         "avisos": ""}
    if w:
        l0 = [l for l in w["letras"] if l[1] < p0 + 0.01][-1][0]
        l1 = next(l for l in w["letras"] if l[1] >= p1 - 0.02)[0]
        base = "DENTRO de %s (entre '%s' e '%s')" % (w["w"], l0, l1)
    else:
        base = "entre %s | %s" % (ant[-1]["w"] if ant else "(início)", dep[0]["w"] if dep else "(fim)")
        forte = next((v for v in dep if v["score"] >= FRACA), None)
        l = forte and next((l for l in forte["letras"] if l[3] >= FRACA), None)
        if l and l[1] < p1:
            r["ate"] = l[1]
            r["avisos"] += "  · '%s' de %s já em %.3f (cortar antes)" % (l[0], forte["w"], l[1])
    perto = [v for v in ws if v["e"] > p0 - 0.1 and v["s"] < p1 + 0.1 or (not w and v in ant[-1:] + dep[:1])]
    r["fracas"] = ["%s %.2f" % (v["w"], v["score"]) for v in perto if v["score"] < FRACA]
    if r["fracas"]:
        r["avisos"] += "  ?? não achou: " + ", ".join(r["fracas"])
    r["txt"] = base + r["avisos"]
    return r


def vales(src, a, b, palavras, limite=-40.0, minimo=0.02):
    """[(p0, p1, dB mínimo, rótulo)]: cada vale do áudio (envelope de 5 ms) e onde ele cai segundo o alinhador."""
    x = audio(src, a, b)[0].numpy()
    db = 20 * np.log10(np.sqrt(np.mean(x[:len(x) // 80 * 80].reshape(-1, 80) ** 2, axis=1)) + 1e-9)  # 5 ms
    out, i = [], 0
    while i < len(db):
        if db[i] >= limite:
            i += 1
            continue
        j = i
        while j < len(db) and db[j] < limite:
            j += 1
        p0, p1 = a + i * 0.005, a + j * 0.005
        if p1 - p0 >= minimo:
            out.append((round(p0, 3), round(p1, 3), round(float(db[i:j].min()), 1), rotulo(p0, p1, palavras)["txt"]))
        i = j
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(args) != 4:
        sys.exit(__doc__)
    src, a, b, texto = args[0], float(args[1]), float(args[2]), args[3]
    ps = alinhar(src, a, b, texto)
    for p in ps:
        linha = "%-16s %9.3f %9.3f  %.2f" % (p["w"], p["s"], p["e"], p["score"])
        if "--letras" in sys.argv:
            linha += "   " + " ".join("%s:%.2f" % (c, s) for c, s, *_ in p["letras"])
        print(linha)
    if "--pausas" in sys.argv:
        print("\nvales (< -40 dB, >= 20 ms):")
        for p0, p1, fundo, rot in vales(src, a, b, ps):
            print("  %9.3f-%9.3f  %3.0f ms  %4.0f dB  %s" % (p0, p1, (p1 - p0) * 1000, fundo, rot))


if __name__ == "__main__":
    main()
