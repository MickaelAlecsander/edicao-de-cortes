# Pesquisa de conteúdo e download, sem tomar bloqueio

Esta é a etapa 1 (fonte): achar o tema, ler as candidatas, baixar a melhor faixa e deixar a fonte pronta para o corte.
Use sempre o `scripts/baixar.py` (`$S/baixar.py`). Ele já aplica as regras deste arquivo: um pedido por vez, folga
entre pedidos, o cliente certo para cada tipo de pedido, a faixa original da legenda e a parada no 429.

```bash
python $S/baixar.py --help            # todos os comandos
python $S/baixar.py teste             # confere a lógica sem rede (rode uma vez por máquina)
```

As pastas ficam na raiz do projeto (`--raiz`, padrão o diretório atual): `_fontes/` (mídia), `_pesquisa/` (listas,
legendas, palavras) e `_lixeira/` (o que sai).

Cada regra traz o porquê numa linha: a lição e de onde veio. "Futebol" é o projeto irmão de cortes de futebol, que
apanhou primeiro do bloqueio; "C20", "C44" etc. são cortes do canal do Raul.

---

## 0. Antes de começar

- [ ] Instalar ou atualizar: `pip install -U "yt-dlp[default]"`.
  - Porquê: o yt-dlp atual resolve o desafio em JavaScript do YouTube; versão velha perde formatos sem avisar direito.
- [ ] Ter o Deno ou o Node no PATH. Sem o Deno, o script passa `--js-runtimes node` sozinho.
- [ ] Ter `ffmpeg`, `ffprobe` e `numpy` (este só para o `opus` e o `teste`).
- [ ] Rodar `python $S/baixar.py teste` e ver "✓ teste ok".
- [ ] Conferir se não há outro download rodando na máquina (outra sessão, outro projeto):
  `tasklist | findstr yt-dlp` no Windows, `pgrep -a yt-dlp` no Linux ou no Mac.
  - Porquê: o limite é por IP, e a trava do script só segura os pedidos dele mesmo.

---

## 1. As regras que evitam o bloqueio

### 1.1 Um pedido por vez, espaçado, nunca em paralelo

- **Fazer um pedido de cada vez.** Nada de laço com threads, subagentes lendo o YouTube ao mesmo tempo ou duas sessões
  baixando juntas.
  - Futebol, 18/09/2026: 20 canais varridos com 6 a 8 pedidos em paralelo, mais 9 legendas seguidas, deram três dias
    de `HTTP Error 429`.
  - Outro dia do futebol: uma varredura com 8 threads tomou 429 logo depois.
  - Caça social do futebol: 28 contas do TikTok lidas em rajada, e 17 "não responderam". Lidas uma por vez,
    responderam.
- **Espaçar os pedidos.** A folga padrão é de 10 s (`--folga`). O script guarda a hora do último pedido em `%TEMP%`, e a
  folga vale até entre execuções diferentes. A trava `baixar_yt.trava` faz o segundo processo esperar a vez.
  - Canal do Raul, 13/10: com uns 10 s entre pedidos, a legenda passou. O `pt` traduzido, pedido em sequência, deu 429.
- **Ler texto antes de baixar mídia.** Primeiro a lista, depois a legenda, depois o áudio. O vídeo vem só depois da
  aprovação do roteiro.
  - Pedido de mídia é pesado (de 0,2 a 4 GB por fonte), e cada pedido conta para o limite. As pesquisas de tema de 09/10
    e de 12/10 escolheram tudo sem baixar nenhum vídeo.

### 1.2 O cliente certo para cada tipo de pedido

O cliente `player_client=web_safari,mweb` vale só para **listar** (regra de ouro 9). Para legenda e mídia ele
atrapalha, e o `baixar.py` já faz a troca.

| Pedido | Cliente | Porquê |
|---|---|---|
| Listar canal, aba ou busca; ler título, idioma, `channel_id` | `web_safari,mweb` (anti-bot) | É onde mora o 429 de rajada (futebol, 18/09). |
| Legenda (listar ou baixar) | padrão | O anti-bot responde "has no subtitles" para TODO vídeo. No futebol (18/09), o dia inteiro foi gasto concluindo "não existe material". No canal do Raul (13/10), a legenda com o anti-bot pediu PO Token. |
| Mídia (áudio e vídeo) | padrão | O anti-bot quebra o download com "GVS PO Token" e "Requested format is not available" (futebol, 18/09). |
| Resolução e formatos (`-F`) | padrão | O anti-bot mente 360p num vídeo de 1080p. Em 19/09, isso reprovou dois candidatos à toa. |
| Legenda quando o padrão pede "Sign in to confirm you're not a bot" | `web_embedded;skip=hls,dash` + `--ignore-no-formats-error` | Esse cliente não mente sobre legenda (futebol, 23/09). Sem a flag, a live recém-encerrada morre com "No video formats found!" antes de chegar à legenda: foram 10 dos 25 primeiros da fila. |

### 1.3 Na legenda, só a faixa original

- **Pedir `pt.*-orig`, nunca a faixa traduzida.**
  - A tradução é servida por outro caminho, muito mais estrangulado. No canal do Raul (13/10), o `pt` traduzido deu
    429 e o `pt-orig` passou.

---

## 2. Quando vier 429 (ou "Sign in to confirm")

- [ ] **Parar tudo:** este script, as outras sessões e os outros projetos da máquina. O `baixar.py` para sozinho e não
  tenta de novo.
- [ ] **Esperar.** IP marcado só cede com tempo.
  - Nos dias leves do futebol, esfriou em 5 a 10 min. Depois de rajada grande, levou dias (18/09: três dias cegos).
- [ ] **Não tentar "destravar".** Um projeto irmão, de cortes em turco, testou, e nada adiantou com o IP já marcado (está
  registrado no `_ytdlp.py` do futebol):
  - nove `player_client` diferentes;
  - `--cookies-from-browser` em seis navegadores. O Chrome cifra os cookies com App-Bound Encryption (desde a v127);
    o Edge falha com o banco travado e, destravado, cai no mesmo DPAPI;
  - PO Token pelo bgutil, com o servidor de pé e um token de verdade;
  - cookies de visitante tirados por curl, sem login.
- [ ] **Nunca digitar senha nem exportar cookies** da conta de ninguém para contornar o bloqueio.
- [ ] **Na volta, recomeçar pelo pedido mais importante**, um por vez.

Outros sinais:

- **Três vídeos seguidos "sem legenda" param o lote.** Antes de concluir que o material não existe, peça a legenda de um
  vídeo de CONTROLE que sabidamente tem uma. Se ele também falhar, é bloqueio.
  - Futebol, 23/09: com três leitores em paralelo, o YouTube passou a dizer "sem legenda" para todo vídeo, e uns 50
    candidatos viraram falso negativo.
- **403 no download de mídia não é 429.** Em geral é o link que expirou, e o script tenta de novo uma vez.
  - Canal do Raul: um 403 no vídeo passou na segunda tentativa, logo depois do áudio.
- **"Video unavailable": conferir as maiúsculas e as minúsculas do id antes de desistir** (ver 6.4).

---

## 3. Achar a fonte e o tema

### 3.1 O YouTube do Raul

- **Listar as três abas.** As lives (o Giro da Bolsa, por exemplo) ficam em `/streams`, não em `/videos`:
  ```bash
  python $S/baixar.py listar @investidorsardinha                    # /videos, os 60 mais novos
  python $S/baixar.py listar @investidorsardinha --aba streams
  python $S/baixar.py listar @investidorsardinha --aba shorts --n 200
  ```
  - Futebol, 18/09: a varredura olhou só `/videos` e concluiu "ele não falou do jogo". Ele falou cinco horas, numa live.
- **Contar com o modo plano sem data.** A ordem da lista dá a idade. A data e o idioma de um finalista saem do
  `info <id>`, um pedido por vídeo.
  - Pesquisa de 09/10: 937 shorts listados com views, nenhum com data.
- **Buscar** com `listar "ytsearch20:<termos>"`. Serve, por exemplo, para achar o vídeo longo de onde saiu um corte.
- **Nunca decidir o idioma pelo título.** O YouTube traduz o título para o idioma do navegador. O idioma vem do campo
  "idioma falado" do `info`.
  - Futebol, 18/09: um canal brasileiro apareceu na busca com o título em espanhol perfeito e pareceu o candidato do dia.
- **Usar os podcasts em que o Raul é convidado como fonte e como prova.** Os cortes oficiais deles (Cortes do
  Inteligência, Cortes do Flow) dizem quais trechos já viralizaram. Para achar o trecho dentro do episódio, baixe só a
  legenda do episódio e case sequências de 5 palavras do corte com ela; não baixe o episódio para procurar.
  - Pesquisa de 12/10: os 15 cortes mais vistos foram localizados assim. A régua dá a "prova" a isso, mas desconta 2
    pontos quando a fonte é de outra conta (`references/ranqueamento.md`).

### 3.2 Os Shorts e os Reels do próprio Raul

- **Usar só o material do próprio short ou Reel.** Pode mudar a ordem das falas, mas não pode puxar trecho do vídeo longo.
  - Pedido do dono do canal, 02/10. Shorts: `@investidorsardinha/shorts`. Reels: `instagram.com/oraulsena/reels`.
- **Preferir o mais visto do último mês.** O short ou o Reel do Raul com 300 mil views ou mais, do mesmo trecho, é a
  prova máxima da régua. Por isso a lista com views é a pesquisa mais barata que existe.
- **Ler a legenda dos shorts como a de qualquer vídeo** (`legenda <id>`, faixa `pt-orig`).

### 3.3 TikTok

- **Ler o perfil sem login, com o yt-dlp.**
  - Pesquisa de 09/10: 500 posts do `@oraulsena`, com views e data.
- **Listar pelo `channel_id`, não pelo `@`.** O `@oraulsena` direto dá erro no yt-dlp (12/10). O caminho:
  ```bash
  python $S/baixar.py info "https://www.tiktok.com/@oraulsena/video/<id>"   # mostra o channel_id
  python $S/baixar.py listar "tiktokuser:<channel_id>" --n 300
  ```
- **Contar com a legenda do TikTok em `por-PT` e sem a hora na deixa.** O `legenda <url>` pede `pt.*|por.*`, e o
  `vtt2txt.py` lê esse formato.
- **Ler uma conta por vez.** O TikTok não deu 429 nos registros, mas deixa de responder quando a leitura vem em rajada
  (os 17 de 28 da caça social).
- **Link curto** (`tiktok.com/t/<código>`): resolver antes com `curl -sIL <link>` e passar a URL final.
  - Futebol, 04/10: era o que fazia o link curto funcionar.

### 3.4 Instagram

- **Listar os Reels de um perfil pelo navegador logado.** Sem login, o perfil não lista. O modelo é o `reels_lista.mjs`
  do projeto:
  1. abrir o perfil com a skill `navegador-background` (sessão salva do site, modo `offscreen`);
  2. escutar as respostas `graphql`, `api/v1/clips` e `api/v1/feed` enquanto a página rola (umas 25 rolagens de
     2.400 px, com 2,2 s entre elas);
  3. juntar de cada mídia: `code`, views (`play_count`), curtidas, comentários, duração e legenda;
  4. tirar a data do `pk` quando o feed não traz o `taken_at`: `(pk >> 23) + 1314220021721` dá os milissegundos.
  - Só ler: nunca curtir, comentar nem seguir.
- **Deixar o login com a pessoa.** Se a sessão cair (muro de login), o modo `--login` do `navegador-background` abre uma
  janela visível e a própria pessoa digita. Nunca digitar nem pedir senha; nunca extrair cookies.
- **Para um Reel só, usar o yt-dlp sem login:**
  ```bash
  python $S/baixar.py info  "https://www.instagram.com/reel/<code>/"   # a descrição é a legenda do post
  python $S/baixar.py video "https://www.instagram.com/reel/<code>/"   # → _fontes/ig_<code>.mp4
  ```
  - Pesquisa de 09/10: a legenda de 70 Reels foi lida assim, sem login. Se o yt-dlp pedir login, volte ao navegador
    logado; não passe cookies.
- **Não procurar faixa Opus no Reel:** ele tem um arquivo só, com o áudio dentro. Use essa faixa e conte quantas
  compressões com perda ela atravessa até o final; o ideal é uma só, a do render.

---

## 4. Ler as candidatas só pelo texto

```bash
python $S/baixar.py legenda <id> [<id> ...]
# → _pesquisa/legendas/<id>.<faixa>.vtt e <id>.txt: blocos de ~15 s com [MM:SS] (ou [H:MM:SS])
```

- **Ler, grepar e escolher pelo `.txt`.** Para conferir à mão uma legenda baixada: `python $S/vtt2txt.py <arquivo.vtt>`.
- **Usar o tempo da legenda automática só para ACHAR o trecho.** Nunca para cortar, nunca como texto final. O texto do
  roteiro vem da transcrição do trecho (seção 7).

### 4.1 As armadilhas do `--sub-langs`

- **Escrever regex.** É `.*-orig`, nunca `*-orig`.
  - `*-orig` é regex inválida, e a chamada morre com "Wrong regex for subtitlelangs". No futebol (22/09), a constante
    ficou meses errada, e o fallback escondia o erro.
- **Lembrar que o casamento é da palavra inteira.** `pt-orig` não pega `pt-BR-orig`; o certo é `pt.*-orig`.
- **Contar com várias faixas.** A dublagem automática do YouTube ganha uma legenda própria, também marcada "(Original)".
  - No `TKU5mAOOtKA`: `ar-orig`, `en-US-orig`, `pt-BR-orig` e `es-orig`, e só a última é a fala real. Na caça de
    23/09, 361 de 1.748 vídeos tinham mais de uma faixa `-orig`.
- **Nunca ler o primeiro `.vtt` da pasta.** Na ordem alfabética, `ar` vem antes de `pt`.
  - Futebol, 23/09: 50 vídeos foram lidos em árabe, e a busca respondeu "não fala do assunto", sem erro.
  - O script escolhe a faixa do idioma falado (`%(language)s`), mostra qual leu e quais havia, e avisa quando a faixa
    lida não é a do idioma falado.
- **Desconfiar de `es-US-orig` ou `en-US-orig` num vídeo do Raul.** Em canal brasileiro, isso é dublagem.

### 4.2 Vídeo sem legenda

Para live recém-encerrada ou programa de rádio:
1. Baixar só o áudio (`audio <id>`).
2. Farejar com um Whisper local pequeno: `tiny`, com VAD e beam 1.
   - Futebol, 23/09: 16,5 vezes o tempo real (730 s de áudio em 44 s).
3. Onde apitar, transcrever com o `large-v3` só aquele trecho.

---

## 5. "Assistir" antes de escolher

O texto não mostra:
- a tela dividida com slide;
- outra pessoa na câmera;
- o gráfico em tela cheia;
- a legenda queimada na fonte;
- o texto do canal na tela ("Deixe o like na CONFIANÇA", no C84).

Tudo isso muda o corte. Por isso, olhe os finalistas antes de fechar o roteiro:

1. **Baixar uma cópia leve:** `python $S/baixar.py video <id> --altura 360` → `_fontes/<id>_360p.mp4`.
   - Esteira de 10/10: a cópia inteira em baixa sai em ~1 min, com uns 40 MB.
2. **Montar a folha de contato:** `python $S/folha_contato.py _fontes/<id>_360p.mp4 --cada 10` (ver
   `references/conferencias.md`). Sem o script, um quadro a cada 10 s, 30 por folha:
   ```bash
   ffmpeg -v error -i _fontes/<id>_360p.mp4 \
     -vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t,10)',scale=320:-2,tile=6x5" \
     -fps_mode vfr -q:v 3 _pesquisa/<id>_folha_%02d.jpg
   ```
   Cada folha cobre 5 min. O quadro k (a partir de 0) da folha p (a partir de 1) é o segundo ((p − 1) × 30 + k) × 10.
3. **Ler a folha junto com o `.txt` da legenda.** O `[MM:SS]` do texto diz qual quadro olhar.

Faça isso só com os finalistas: cada cópia é um pedido de mídia.

---

## 6. Baixar a fonte do corte

### 6.1 A ordem

1. **Antes da aprovação do roteiro:** `audio <id>` → `_fontes/<id>_audio.webm`. Serve para transcrever o trecho.
2. **Depois da aprovação:** `opus <id>`. Ele baixa o vídeo, mede o atraso e monta o `_fontes/<id>_opus.mkv`.
3. **Daí em diante, tudo sai do `_opus.mkv`:** transcrição, pausas, cortes e conferências.

### 6.2 Inteiro, nunca por trecho

- **Baixar sempre o arquivo inteiro e cortar local.** Nunca usar `--download-sections`.
  - Esteira de 10/10: o `--download-sections` travou 15 min e costuma morrer por timeout. Baixar inteiro e cortar
    local é mais rápido.
  - O futebol baixa por trecho (`precortar.py`), mas aqui não funcionou.
- **Vídeo:** a menor dimensão até 1080 (`-S res:1080`), o que pega também o short em pé, de 1080 × 1920; e o AAC 140
  junto, porque ele é a referência do atraso.

### 6.3 A melhor faixa de áudio: o Opus

- **Tirar a voz do Opus do YouTube** (formato 251, `.webm`), **nunca do AAC de 128k** do `.mp4`.
  - C23, 05/10: a voz soou "vibrada, com cara de estourada". As duas faixas diferem em −20 dB, e o AAC é a pior. Além
    disso, a voz era recomprimida mais três vezes. O dono do canal não sentiu tanta diferença com a troca, mas ela é
    barata e não piora nada, então ficou.
- **Montar o vídeo do `.mp4` com o Opus atrasado no mesmo tanto que o AAC.** O AAC vem ~35 a 36 ms atrasado em relação
  ao Opus.
  - C20: a transcrição e os vales foram medidos no `.webm`, e o corte foi feito no `.mp4`. Todas as pontas caíram 35 ms
    dentro da palavra vizinha.
- **O que o `opus` faz:**
  1. mede o atraso por correlação em 3 pontos (25%, 50% e 75% da fonte), com janelas de 20 s em 48 kHz. O `-ss` vai
     depois do `-i`, porque no AAC, antes do `-i`, ele errou ~60 ms (C44);
  2. usa a mediana: `ffmpeg -i <id>.mp4 -itsoffset <atraso> -i <id>_audio.webm -map 0:v -map 1:a -c copy <id>_opus.mkv`;
  3. mede de novo o `.mkv` contra o `.mp4` e grava o `_fontes/<id>_opus.json` com o atraso e o resíduo.
- **Esperar um resíduo abaixo de 1 ms.** O Matroska guarda o tempo em milissegundos, então 36,3 ms viram 36 ms.
- **Investigar se os 3 pontos discordam em mais de 2 ms ou se a força ficar abaixo de 0,5.** Pode ser trecho sem voz
  ou um corte da própria fonte.
- **Medir em cada fonte; nunca copiar o número.**
  - O projeto usou 35,3 ms (C20, C23). Nesta skill, a mesma fonte do C22 (`QhDX-BhJSnY`) mediu 36,3 ms.
- **Vídeo baixado sem áudio** (só o DASH): não há referência, e os dois começam em 0 (C49). O `video` do script sempre
  traz o 140, então isso só acontece com download feito à mão.
- **Somar o atraso nas palavras transcritas no `.webm`:**
  `python $S/baixar.py somar _pesquisa/<id>_palavras.json <atraso>` → `<id>_palavras_mkv.json`.
  Se a transcrição saiu do próprio `.mkv`, não há nada a somar.

### 6.4 O id do vídeo diferencia maiúscula de minúscula

- **Copiar o id da lista ou da URL; nunca redigitar.**
  - 17/10: o `Z99ri8YcCsY` (Z maiúsculo) deu "indisponível", e o horário das 12h saiu com um vídeo da reserva. À tarde,
    o `z99ri8YcCsY` (z minúsculo) era o vídeo certo e virou o C84.
- **No Windows, contar com a colisão de nomes.** O NTFS ignora a caixa, então dois ids que só diferem nela viram o
  mesmo arquivo na `_fontes/`. Se acontecer, renomeie um dos dois antes de baixar o outro.

---

## 7. Transcrição só do trecho útil, com o tempo absoluto na fonte

1. **Transcrever só os trechos candidatos**, com uma folga de 5 a 8 s de cada lado, pelo `transcrever_local.py` (ver
   `references/roteiro.md`). Ele já devolve `[{"w", "s", "e"}]` em segundos da FONTE:
   ```bash
   python $S/transcrever_local.py _fontes/<id>_audio.webm _pesquisa/<id>_palavras.json 1:24:54-1:31:46 1:40:02-1:43:40
   ```
   - Futebol: a legenda automática marca a palavra, não a respiração. A fronteira certa só se acha se estiver dentro do
     trecho.
   - Em CPU, o large-v3 leva de 1 a 2 vezes o tempo do áudio. A live inteira não cabe no dia.
2. **Manter o tempo ABSOLUTO na fonte**, nunca o do clipe. Se extrair um trecho à mão, some o início dele em todo
   tempo, e ponha o `-ss` depois do `-i`:
   `ffmpeg -v error -i <fonte> -ss 1:24:54 -to 1:31:46 -map 0:a:0 -ac 1 -ar 16000 -c:a pcm_s16le trecho.wav`.
   - O `cortes.json`, as pausas e as janelas falam a língua da fonte. Tempo de clipe pede uma conversão em cada
     ferramenta, e uma conversão esquecida vira ponta errada.
3. **Saber de qual arquivo saíram as palavras.** Antes da aprovação só existe o `.webm`: depois do `opus`, passe o
   `_palavras.json` pelo `somar` (6.3). Transcrição feita no `_opus.mkv` já está no tempo do corte.
4. **Lembrar quem dá o quê:** o Whisper dá o TEXTO; o tempo fino vem do MMS_FA e do envelope
   (`references/corte-e-fala.md`).
   - C29: o large-v3 pôs palavras até 1,4 s fora do lugar.
5. **Nunca usar arquivo temporário de nome fixo** em transcrição feita à mão.
   - 13/10: dois processos com o mesmo wav temporário fizeram o C77 sair com o texto do C78. O `transcrever_local.py`
     não usa arquivo temporário.
6. **Deixar folga no fim também na conferência da montagem** (1,5 s). Sem folga, o Whisper inventa a última palavra.

---

## 8. Depois de agendado: a fonte vai para a lixeira

```bash
python $S/baixar.py liberar <id> [<id> ...]     # _fontes/<id>* → _lixeira/fontes/
```

- **Rodar depois de agendar o corte**, ou quando o dono do canal reservar um corte pronto. Se ele pedir mudança depois
  da prévia, a fonte ainda está na `_fontes/`.
- **Contar com a exceção:** a fonte fica quando outro corte, ainda sem `renders/etapa3.mp4`, usa o mesmo id.
- **Nunca apagar de vez.** Quem esvazia a `_lixeira/` é o dono do canal.
  - Pedido de 13/10: "pra não termos tanto espaço ocupado". Cada fonte tem de 0,2 a 4 GB. O corte já tem o próprio
    `assets/raul.mp4`, e a fonte se baixa de novo pelo id.
- **Manter as legendas e as palavras** (`_pesquisa/legendas/`, `_pesquisa/<id>_palavras*.json`). Elas servem para
  achar frases depois e para reaproveitar a fonte sem transcrever de novo.

---

## Checklist da etapa

- [ ] Nenhum outro yt-dlp rodando na máquina.
- [ ] Listas do canal (`/videos`, `/streams`, `/shorts`), dos Reels e do TikTok, com views, sem baixar mídia.
- [ ] Legenda das candidatas, na faixa do idioma falado, lida pelo `.txt`.
- [ ] Folha de contato dos finalistas (cópia de 360p).
- [ ] `audio <id>` → trecho → transcrição em tempo absoluto → roteiro para aprovação.
- [ ] Depois do ok: `opus <id>`, com resíduo abaixo de 1 ms; tudo a partir do `_opus.mkv`.
- [ ] Palavras transcritas no `.webm` passaram pelo `somar`.
- [ ] Depois de agendado: `liberar <id>`.
- [ ] Se vier 429: parar, esperar e voltar um pedido por vez. Nada de cookies, PO Token ou troca de cliente.
