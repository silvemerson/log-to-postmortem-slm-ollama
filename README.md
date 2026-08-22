# log-to-postmortem-slm-ollama

Laboratório de IA **100% local** para DevOps/SRE: um SLM (Small Language Model) rodando via [Ollama](https://ollama.com) em Docker analisa um log de erro real e, na sequência, gera automaticamente um **rascunho de postmortem** — sem enviar nenhum dado para APIs externas.

Fluxo do lab:

```
samples/error.log ──▶ 01_analyze_log.py ──▶ output/analysis.json ──▶ 02_generate_postmortem.py ──▶ output/postmortem.md
                          (SLM via Ollama)                                (SLM via Ollama)
```

> Material de apoio de palestra técnica. Os prints da demo foram gerados com este repositório — sinta-se à vontade para reproduzir tudo na sua máquina.

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/) (v2, comando `docker compose`)
- Python 3.8+ (os scripts usam apenas a standard library — nenhum `pip install` necessário)
- GPU **não** é necessária — tudo roda em CPU (com GPU NVIDIA, veja o bloco comentado no `docker-compose.yml`)

## Passo a passo

### 1. Subir o ambiente

```bash
docker compose up -d
```

Isso sobe dois serviços:

| Serviço      | Porta | Função                                     |
|--------------|-------|--------------------------------------------|
| `ollama`     | 11434 | API de inferência local                    |
| `open-webui` | 3000  | Interface web para conversar com o modelo  |

### 2. Baixar o modelo SLM

O modelo é baixado **dentro do container** do Ollama (fica salvo em volume persistente, só precisa fazer uma vez):

```bash
docker exec ollama ollama pull phi3
```

Quer testar outro modelo? Baixe-o e ajuste a variável `MODEL`:

```bash
docker exec ollama ollama pull gemma2:2b
export MODEL=gemma2:2b
```

### 3. Rodar os scripts em ordem

```bash
# (opcional) copie e ajuste as variáveis de ambiente
cp .env.example .env

# Passo 1: análise do log de erro
python3 scripts/01_analyze_log.py

# Passo 2: rascunho de postmortem a partir da análise
python3 scripts/02_generate_postmortem.py
```

Resultados:

- `output/analysis.json` — resposta completa da API do Ollama com a análise do log
- `output/postmortem.md` — rascunho de postmortem em Markdown, pronto para revisão

Você também pode abrir o [Open WebUI](http://localhost:3000) e conversar com o modelo direto no navegador.

## LLM vs. SLM — e por que este lab usa Phi-3

**LLMs** (Large Language Models — GPT, Claude, Gemini…) têm dezenas ou centenas de bilhões de parâmetros: são mais capazes em raciocínio aberto, mas exigem infraestrutura pesada e, na prática, rodam em APIs de terceiros — ou seja, seus logs saem da sua rede.

**SLMs** (Small Language Models — [Phi-3](https://ollama.com/library/phi3), [Gemma 2B](https://ollama.com/library/gemma2), [Qwen](https://ollama.com/library/qwen2.5)…) têm poucos bilhões de parâmetros e cabem em uma máquina comum, rodando até em CPU. Para **tarefas estruturadas e com contexto contido** — como "analise este log e responda nestas 4 seções" — eles entregam resultado útil com três vantagens que interessam muito a times de operações:

1. **Privacidade**: logs de produção frequentemente contêm hostnames, IPs, dados de clientes. Aqui, nada sai da sua máquina.
2. **Custo**: zero custo por token, sem cota de API.
3. **Latência/disponibilidade previsíveis**: sem dependência de serviço externo — funciona até sem internet.

## Quando usar / quando não usar

**Funciona bem:**

- Tarefas estruturadas com contexto contido: classificar/resumir logs, extrair campos, gerar primeiro rascunho de postmortem, sugerir hipóteses de causa
- Ambientes com restrição de privacidade/compliance, onde dados não podem sair da rede
- Automação de "primeira passada" que economiza tempo do engenheiro de plantão

**Não use para:**

- Substituir revisão humana em decisões críticas — o postmortem gerado é um **rascunho**, e SLMs podem alucinar detalhes com confiança
- Análises que exigem contexto amplo que o modelo não tem (arquitetura do sistema, histórico de incidentes, mudanças recentes)
- Executar ações automáticas de remediação sem um humano no loop

Regra prática: o SLM **acelera** o trabalho do engenheiro; ele não o substitui.

## Estrutura do repositório

```
.
├── docker-compose.yml            # Ollama + Open WebUI, rede e volumes
├── .env.example                  # MODEL e OLLAMA_HOST
├── samples/
│   └── error.log                 # log de timeout de conexão com PostgreSQL
├── scripts/
│   ├── 01_analyze_log.py         # log -> análise estruturada (JSON)
│   └── 02_generate_postmortem.py # análise -> rascunho de postmortem (Markdown)
└── output/                       # arquivos gerados (ignorados pelo git)
```

## Créditos

**Emerson Silva** — DevOps/SRE Engineer

- Community Lead de Kubernetes na DougBrazil
- Organizador do CNCF Campinas

📝 Blog: [emerson-silva.blog.br](https://emerson-silva.blog.br) · 💼 LinkedIn: [linkedin.com/in/silvemerson](https://linkedin.com/in/silvemerson)
