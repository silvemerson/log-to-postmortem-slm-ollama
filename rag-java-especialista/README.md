# rag-java-especialista

Segunda demo do lab: mostra a diferença entre um SLM **genérico** e um SLM **especialista via RAG** (Retrieval-Augmented Generation), usando o mesmo Ollama já configurado na raiz do repositório. Continua 100% local — a base de conhecimento nunca sai da sua máquina.

O tema escolhido é "algoritmos em Java", mas o ponto central da demo não é ensinar algoritmos: é mostrar, ao vivo, que um SLM sem contexto **inventa uma resposta plausível porém genérica**, enquanto o mesmo SLM com RAG **cita a convenção real e específica do seu time** — que nenhum modelo pré-treinado poderia saber de antemão.

## Como funciona

```
knowledge_base/*.md ──▶ 00_build_index.py ──▶ output/index.json
                          (gera embeddings)

pergunta do usuário ──▶ 01_ask_without_rag.py ──▶ resposta genérica (baseline)

pergunta do usuário ──▶ 02_ask_with_rag.py ──▶ busca no índice (similaridade de cosseno)
                                              ──▶ injeta os chunks mais relevantes no prompt
                                              ──▶ resposta fundamentada no contexto
```

A base de conhecimento (`knowledge_base/`) tem 5 documentos:

- `01-complexidade-big-o.md`, `02-estruturas-de-dados.md`, `03-algoritmos-ordenacao.md`, `04-algoritmos-busca.md` — referência geral sobre algoritmos e estruturas de dados em Java (conhecimento que o modelo já teria, em maior ou menor grau).
- `05-convencoes-squad-orders.md` — **convenções fictícias de uma squad interna** (nomes de classes utilitárias, regras de nomenclatura, limites de tamanho de coleção). Isso é propositalmente "conhecimento que não existe em nenhum lugar público" — é o que faz o contraste sem RAG / com RAG ficar óbvio na demo.

## Pré-requisitos

Além do que já está descrito no README da raiz (Docker, Docker Compose, Python 3.8+), este lab precisa de um **modelo de embedding**:

```bash
docker exec ollama ollama pull nomic-embed-text
```

O modelo de texto (`MODEL`, default `qwen2.5:3b`) precisa ser baixado à parte do `phi3` usado no lab de postmortem — é um modelo diferente, escolhido por ter foco maior em código:

```bash
docker exec ollama ollama pull qwen2.5:3b
```

## Passo a passo

```bash
cd rag-java-especialista/scripts

# 1. Construir o índice vetorial a partir da base de conhecimento
python3 00_build_index.py

# 2. Baseline: pergunta sem nenhum contexto (o modelo "chuta" com o que já sabe)
python3 01_ask_without_rag.py

# 3. Mesma pergunta, agora com RAG (contexto recuperado do índice)
python3 02_ask_with_rag.py
```

Os dois últimos scripts aceitam uma pergunta customizada como argumento:

```bash
python3 02_ask_with_rag.py "Qual estrutura de dados devo usar para uma fila de prioridade de pedidos?"
```

## Variáveis de ambiente

| Variável      | Default                   | Uso                                    |
|---------------|----------------------------|-----------------------------------------|
| `MODEL`       | `qwen2.5:3b`               | Modelo de geração de texto              |
| `EMBED_MODEL` | `nomic-embed-text`         | Modelo de embedding (busca vetorial)    |
| `OLLAMA_HOST` | `http://localhost:11434`   | Endereço da API do Ollama               |

## O que observar na demo

1. Rode `01_ask_without_rag.py` e mostre que a resposta é plausível, "de livro-texto", mas não menciona nada da squad Orders — porque isso não existe no pré-treinamento do modelo.
2. Rode `02_ask_with_rag.py` e mostre a lista de **chunks recuperados** (com o score de similaridade) antes da resposta final — isso deixa o "porquê" da resposta transparente para a plateia.
3. Compare as duas respostas lado a lado: a segunda deve citar a classe interna correta (`LinearSearchUtil`/`BinarySearchUtil`) e a regra de decisão (limite de 50 elementos) exatamente como descrito em `05-convencoes-squad-orders.md`.

## Detalhe de implementação que vale comentar na palestra

O embedding de cada chunk inclui o **título do documento**, não só o texto da seção (veja `common.split_into_chunks`). Sem isso, uma seção específica como "Escolha de algoritmo de busca" nunca menciona explicitamente "squad Orders" — só o título do documento o faz — e acaba perdendo posição no ranking de similaridade para perguntas que citam "time Orders". É um exemplo real (e reproduzível) de como o desenho do chunking afeta a qualidade do RAG na prática, não só a teoria.

## Alucinação mesmo com RAG (ótimo gancho para a palestra)

Em um dos testes, pedindo para ordenar pedidos no "time Orders", o `qwen2.5:3b` respondeu corretamente sobre `OrderSortingPolicy`, `PriorityBlockingQueue` e as convenções de nomenclatura — mas começou a resposta com "No time Orders da **Alibaba Cloud**...", um detalhe que não existe em nenhum lugar do contexto (nem no restante do repositório). RAG reduz alucinação porque ancora a resposta em fatos reais, mas **não elimina**: o modelo ainda pode inventar detalhes fora do que foi recuperado. É a mesma mensagem do lab de postmortem — o rascunho gerado por IA sempre precisa de revisão humana antes de ser usado.

## Limitações conhecidas (também vale mencionar)

- O corpus é pequeno de propósito (didático). Em um corpus real, maior, valeria a pena reduzir `TOP_K` de volta para 3-4 e considerar técnicas de *reranking*.
- SLMs pequenos (ex: `gemma2:2b`) às vezes erram o raciocínio mesmo com o contexto certo em mãos (ex: confundir o limiar de 50 elementos). `qwen2.5:3b` e `phi3` se saíram consistentemente melhor nos testes deste lab — mais um motivo prático para a seção "LLM vs. SLM" do README principal.
- Assim como no lab de postmortem, isto é uma demonstração de RAG, não um sistema de produção: sem cache de embeddings incrementais, sem lidar com arquivos muito grandes, sem reranking.
