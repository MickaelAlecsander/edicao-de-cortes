# Uso: python acha_frase.py ARQ.vtt "frase" [...]  -> tempo (h:mm:ss.s) da 1a palavra de cada ocorrência,
# usando os tempos por palavra da legenda automática do YouTube (<hh:mm:ss.mmm><c>palavra</c>).
import re, sys, unicodedata
if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
    sys.exit("uso: python acha_frase.py ARQ.vtt \"frase\" [...]  -> tempo (h:mm:ss.s) da 1ª palavra de cada ocorrência, pelos tempos por palavra da legenda automática do YouTube")
def norm(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
words, t0 = [], None
for l in open(sys.argv[1], encoding='utf-8'):
    m = re.match(r'(\d+):(\d+):(\d+\.\d+) -->', l)
    if m: t0 = int(m[1])*3600 + int(m[2])*60 + float(m[3]); continue
    if '<c>' not in l: continue
    first = re.match(r'([^<]+)<', l)
    if first and first[1].strip(): words += [(t0, w) for w in first[1].split()]
    for ts, w in re.findall(r'<(\d+:\d+:\d+\.\d+)><c>([^<]*)</c>', l):
        h, mi, s = ts.split(':'); words += [(int(h)*3600 + int(mi)*60 + float(s), x) for x in w.split()]
ws = [norm(re.sub(r'[^\w]', '', w)) for _, w in words]
for frase in sys.argv[2:]:
    alvo = [norm(re.sub(r'[^\w]', '', w)) for w in frase.split()]
    hits = [i for i in range(len(ws)) if ws[i:i+len(alvo)] == alvo]
    out = [f'{int(words[i][0]//3600)}:{int(words[i][0]%3600//60):02d}:{words[i][0]%60:04.1f}' for i in hits]
    print(f'{frase!r}: {out[:6]}')
