# Slides — log-to-postmortem-slm-ollama

Mesmo padrão usado em `k8s-mentor/slides`: [Marp](https://marp.app/) + um roteiro separado com as falas.

- [`postmortem-rag-local.md`](postmortem-rag-local.md) — os slides em si (Marp), 20 slides, alvo de 22-25 min
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

## Se o texto do deck mudar de novo

Recontar os slides: `grep -c '^---$' postmortem-rag-local.md`, subtrair 2 (delimitadores do frontmatter). O roteiro assume 20 slides — atualize o cabeçalho do roteiro se esse número mudar.
