# -*- coding: utf-8 -*-
"""MODELO do pos_cortar.py de cada corte (vem com assets/modelo/): preencha TEXTO, FALA e OUTRO.

    python $S/cortar.py . && python pos_cortar.py      # idempotente: o cortar.py refaz as palavras; rode depois de cada corte

A transcrição erra o tempo das palavras em até 0,4 s (C79–C84: o "né?" vinha 0,39 s antes, o "senador" 0,28 s depois) e
perde palavra na ponta do bloco (o "Ou" de "Ou Gustavo Lima", o "Se" de "Se aqui na empresa"). Então o texto de cada bloco
vem daqui (o do roteiro, com a escrita certa) e o tempo de cada palavra vem do alinhador MMS_FA sobre o áudio do bloco.
  · TEXTO: o que vai ao ar, com nomes, números e siglas certos ("Marcos Quebeco" do Whisper → "Mark Zuckerberg");
  · FALA: como a palavra se pronuncia, só para o alinhador ("6x1" → "6 por 1"; sem isso vira o token "seisxum"). Número
    com algarismo vai por extenso sozinho. A legenda fica com a escrita do TEXTO;
  · OUTRO: índices das palavras ditas pelo apresentador (saem com "quem": "apresentador", no cartão escuro da legenda).
O fim de cada palavra é o começo da seguinte (no máximo 0,9 s): o alinhador só marca o começo do som.
Bloco sem TEXTO fica com as palavras que o cortar.py tirou do palavras.json, realinhadas.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.environ.get("EDICAO_CORTES") or os.path.expanduser("~/.claude/skills/edicao-de-cortes"), "scripts"))   # scripts/ da skill
import torch  # noqa: E402
import alinhar as AL  # noqa: E402

TEXTO = {   # id do bloco → o texto que vai ao ar (exemplo do C84)
    "gancho": "Eu não quero que a gente entre naquela seara de: é só você acordar às 5 da manhã e trabalhar duro que "
              "você vai conseguir enriquecer.",
}
FALA = {"6x1": "6 por 1"}   # escrita → como se fala, só para o alinhador (a legenda fica com a escrita)
OUTRO = {}                  # {"bloco": {índices das palavras ditas pelo apresentador}}


def alinha(src, a, b, texto):
    """[(palavra escrita, início)]: cada palavra pode virar várias no extenso ("10%" → "dez por cento")."""
    AL._modelo = AL._modelo or AL.BUNDLE.get_model()
    orig, toks, dono = texto.split(), [], []
    for i, w in enumerate(orig):
        for n in (AL.normaliza(x).replace("-", "") for x in AL.por_extenso(FALA.get(w.strip(",.?!:;"), w)).split()):
            if n:
                toks.append(n)
                dono.append(i)
    wav = AL.audio(src, a, b)
    with torch.inference_mode():
        em, _ = AL._modelo(wav)
    spans = AL.BUNDLE.get_aligner()(em[0], AL.BUNDLE.get_tokenizer()(toks))
    q = wav.size(1) / em.size(1) / AL.SR
    ini = {}
    for d, sp in zip(dono, spans):
        ini.setdefault(d, a + sp[0].start * q)
    return [(w, ini[i]) for i, w in enumerate(orig) if i in ini]


p = "assets/tempos.json"
t = json.load(open(p, encoding="utf-8"))
for b in t["blocos"]:
    txt = TEXTO.get(b["id"]) or " ".join(w["w"] for w in b["palavras"])
    s0, s1 = b["audio"]
    ws = alinha(b["arquivo"], s0, s1, txt)
    corte = lambda x: round(x - b["fonte"][0] + b["inicio"], 3)   # tempo da fonte → tempo da montagem
    fim_bloco = round(b["inicio"] + b["dur"], 3)
    novo = []
    for k, (w, s) in enumerate(ws):   # o fim de cada palavra é o começo da seguinte (o alinhador só marca o começo do som)
        prox = ws[k + 1][1] if k + 1 < len(ws) else s1
        novo.append({"w": w, "s": corte(s), "e": min(corte(prox), corte(s) + 0.9, fim_bloco),
                     "quem": "apresentador" if k in OUTRO.get(b["id"], ()) else "raul"})
    novo[0]["w"] = novo[0]["w"][:1].upper() + novo[0]["w"][1:]
    if novo[-1]["w"][-1] in ",;":
        novo[-1]["w"] = novo[-1]["w"][:-1] + "."
    b["palavras"] = novo
json.dump(t, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for b in t["blocos"]:
    print("%-8s %6.2f | %s …" % (b["id"], b["inicio"], " ".join("%s@%.2f" % (w["w"], w["s"]) for w in b["palavras"][:6])))
