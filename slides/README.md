# Slides — log-to-postmortem-slm-ollama

Mesmo padrão usado em `k8s-mentor/slides`: [Marp](https://marp.app/) + um roteiro separado com as falas.

- [`postmortem-rag-local.md`](postmortem-rag-local.md) — os slides em si (Marp), 21 slides, alvo de 22-26 min
- [`roteiro-postmortem-rag-local.md`](roteiro-postmortem-rag-local.md) — o que falar em cada slide, com timing
- [`assets/`](assets/) — prints reais copiados de `../img/` (ver tabela abaixo)

## Pré-requisito

```bash
npm install -g @marp-team/marp-cli
```

## Visualizar no browser com live reload

```bash
marp --watch postmortem-rag-local.md
```

## Exportar para PDF

```bash
marp postmortem-rag-local.md --pdf --allow-local-files -o postmortem-rag-local.pdf
```

## Exportar para HTML

```bash
marp postmortem-rag-local.md --html --allow-local-files -o postmortem-rag-local.html
```

## De onde vêm os prints em `assets/`

Todos copiados de `../img/`, que não é versionado (ver `.gitignore` da raiz) — se recriar os prints, repita a cópia com os nomes abaixo:

| Arquivo em `assets/`   | Origem (`../img/`) | Conteúdo                                      |
|-------------------------|---------------------|------------------------------------------------|
| `error-log.png`         | `03.png`            | `samples/error.log`                             |
| `analise-log.png`       | `04.png`            | saída de `01_analyze_log.py`                    |
| `postmortem-md.png`     | `06.png`            | `postmortem.md` renderizado                     |
| `build-index.png`       | `09.png`            | saída de `00_build_index.py` (lab RAG)          |
| `sem-rag.png`           | `10.png`            | saída de `01_ask_without_rag.py`                |
| `com-rag.png`           | `12.png`            | saída de `02_ask_with_rag.py`                   |

`docker-whale.png` é diferente: logo oficial da baleia do Docker (PNG com fundo transparente), usado só no slide de título (lockup "Docker Day Piracicaba"). `qrcode-contato.png` e `4linux-logo/logo-4linux.png` vêm do repositório de referência `palestras/dougbrasil-meetup-k8s-unifaat-atibaia` — o QR code aparece no slide final, a logo da 4Linux no rodapé de todos os slides (exceto a capa, que já tem a marca do evento) e no slide de "A 4Linux" (timeline da empresa, mesmo padrão do `k8s-mentor`).

## Se o texto do deck mudar de novo

Recontar os slides: `grep -c '^---$' postmortem-rag-local.md`, subtrair 2 (delimitadores do frontmatter). O roteiro assume 21 slides — atualize o cabeçalho do roteiro se esse número mudar.

## Nota sobre o slide de título (bug de renderização do Marp)

O lockup "baleia + Docker Day Piracicaba" no slide 1 usa dois blocos `<p>` separados (imagem e texto cada um no seu próprio parágrafo), não uma `<div>` com flexbox. Isso não é estético — é necessário: `display:flex; flex-direction:column` com uma `<img>` e um `<span>` dentro renderiza empilhado corretamente em qualquer navegador, mas **quebra especificamente no pipeline `marp --pdf`** (Puppeteer print-to-PDF), exibindo os elementos lado a lado em vez de empilhados. Confirmado isolando o problema: o mesmo HTML exportado (`--html`) renderiza certo num navegador de verdade; só o `--pdf` bugava. Se for mexer nesse trecho de novo, evite recriar esse combo flex-column com img+texto — prefira blocos `<p>`/`<div>` separados e `margin:0 auto` pra centralizar.
