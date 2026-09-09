# Roteiro de Apresentação — O log não sai da rede (log-to-postmortem-slm-ollama)

**Palestrante:** Emerson Silva · 4Linux
**Tempo total estimado:** 22–25 min + perguntas (alvo: 25 min)
**Formato:** prints reais (não é demo ao vivo) — os 6 prints usados vêm de `assets/`, gerados a partir do repositório

> **Numeração:** 1 entrada = 1 slide real do `postmortem-rag-local.md` (20 no total). Se o deck mudar, reconfira contando os blocos — não conte `---` do frontmatter.

---

## Slide 1 — Título (1 min)

> **Tom:** direto, sem "bom dia, meu nome é...". O título é a tese inteira da talk.

"O log não sai da rede. Hoje eu vou te mostrar dois momentos: primeiro, transformar um log de erro num rascunho de postmortem. Depois, transformar o mesmo SLM genérico num especialista — os dois rodando 100% na sua máquina, sem mandar nada pra nuvem."

---

## Slide 2 — Quem sou eu (1 min)

"Emerson Silva, engenheiro DevOps/SRE na 4Linux. Autor de dois livros — Kubernetes para Iniciantes e Mentes Automatizadas, sobre IA em ambientes Kubernetes e DevOps. Community Lead de Kubernetes na DougBrazil e organizador do chapter da CNCF aqui em Campinas."

---

## Slide 3 — Agenda (30 seg)

"Seis partes rápidas: o problema que motivou isso, por que SLM local em vez de LLM de nuvem, a primeira demo — log virando postmortem —, depois uma pergunta que separa fine-tuning de RAG, a segunda demo — o mesmo SLM virando especialista —, e fecho com o que aprendi testando de verdade."

---

## Slide 4 — 3h da manhã, o banco caiu (2 min)

> **Tom:** cenário concreto, não abstrato — todo SRE já viveu isso.

"Cenário clássico: o pager toca, você abre vinte linhas de stack trace, e precisa virar isso em causa provável, severidade, e um rascunho de postmortem pra reunião de amanhã. Óbvio que uma IA ajudaria aqui."

"Mas pensa no que tem dentro desse log: hostname interno, IP, às vezes nome de cliente. Se você cola isso numa IA de nuvem, isso tudo virou payload de uma API de terceiro. A pergunta não é 'IA ajuda'. É: dá pra ter essa ajuda sem o log sair da rede?"

---

## Slide 5 — SLM local, via Ollama (2 min)

"A resposta é rodar um SLM — Small Language Model — local, via Ollama. Não é um LLM menor por acidente, é feito pra ser pequeno: poucos bilhões de parâmetros, roda até em CPU, cabe no seu laptop."

"Três vantagens práticas: privacidade — nada sai da rede; custo — zero por token; e disponibilidade — funciona sem internet, exatamente na hora que você mais precisa, no meio do incidente. Pra tarefas estruturadas com contexto contido, tipo 'analisa esse log', um SLM já entrega resultado útil."

---

## Slide 6 — Docker + Ollama, dois containers (1 min)

"A stack é simples: dois containers, Ollama expondo a API na porta 11434, e Open WebUI se quiser conversar com o modelo pelo navegador. `docker compose up -d` sobe os dois, o modelo é baixado uma vez com `ollama pull` e fica em volume persistente."

"E os scripts são Python puro — só `urllib` e `json` da standard library. Nem `pip install` pra acompanhar a demo."

---

## Slide 7 — Demo 1: de log a postmortem (1 min)

"Primeira demo: um log real de timeout de conexão com PostgreSQL passa por dois scripts. O primeiro analisa e estrutura o problema. O segundo pega essa análise e gera um rascunho de postmortem em Markdown. Os dois passando pelo mesmo SLM local."

---

## Slide 8 — O log que vamos analisar (1.5 min)

> **Print real:** `samples/error.log`.

"Esse é o log: a API de pedidos tenta conectar no Postgres, tenta de novo com backoff, três tentativas, e cai — timeout de conexão, o lote inteiro vai pra dead-letter queue. É o tipo de log que qualquer SRE já viu de madrugada."

---

## Slide 9 — Passo 1: análise estruturada (2 min)

> **Print real:** saída de `python3 scripts/01_analyze_log.py`.

"O script manda esse log pro modelo com um prompt pedindo exatamente 4 coisas: causa provável, componente afetado, severidade, e uma recomendação inicial. Repara que a resposta vem estruturada, pronta pra colar numa investigação — não é um parágrafo solto."

---

## Slide 10 — Passo 2: o rascunho de postmortem (2 min)

> **Print real:** `postmortem.md` renderizado.

"Segundo script pega essa análise, mais o log original, e gera um postmortem completo: resumo, timeline com os timestamps reais, causa raiz, impacto, ações corretivas e preventivas."

"E repara o topo do documento: ele é marcado como RASCUNHO, com o aviso de que precisa de revisão humana antes de publicar. Isso não é detalhe — é a régua de tudo que eu vou mostrar hoje."

---

## Slide 11 — E se eu quiser um especialista? (1 min)

"Isso já ajuda pra log genérico. Mas e se eu quiser que o modelo conheça as convenções do MEU time — nomes de classe internos, regras de nomenclatura, coisas que não estão em nenhum lugar público? A resposta óbvia parece ser fine-tuning. Não é a primeira escolha."

---

## Slide 12 — Fine-tuning vs. RAG (1.5 min)

"Fine-tuning ensina estilo e formato muito bem. Mas não é confiável pra injetar conhecimento novo — exige dataset curado, pipeline de treino, avaliação. É trabalho de ML de verdade."

"RAG — Retrieval-Augmented Generation — resolve o mesmo problema sem treinar nada: busca o trecho certo de um documento real por similaridade e entrega isso como contexto antes da resposta. Fine-tuning fixa comportamento. RAG ancora em fatos. Pra conhecimento específico, RAG vence primeiro."

---

## Slide 13 — Demo 2: SLM genérico vs. SLM + RAG (1 min)

"Segunda demo. Montei uma base de conhecimento local: documentação geral de algoritmos em Java, mais um documento de convenções de uma squad fictícia — coisas que nenhum modelo pré-treinado teria como saber. Um script indexa essa base com embeddings. Outros dois fazem a mesma pergunta, um sem contexto, outro com."

---

## Slide 14 — Construindo o índice vetorial (1 min)

> **Print real:** `00_build_index.py` — 5 documentos, 22 chunks.

"Cada seção dos documentos vira um chunk, cada chunk vira um vetor via embeddings do próprio Ollama. Tudo local, nada de API externa pra isso também."

---

## Slide 15 — Sem RAG (1.5 min)

> **Print real:** `01_ask_without_rag.py`.

"Pergunto: como buscar em uma lista de 30 pedidos no time Orders? Resposta plausível, de livro-texto — ArrayList, indexOf. Mas zero menção a qualquer convenção do time, porque isso simplesmente não existe no que o modelo aprendeu."

---

## Slide 16 — Com RAG (2 min)

> **Print real:** `02_ask_with_rag.py` — chunks recuperados + resposta.

"Mesma pergunta, agora com RAG. Antes da resposta, mostro os chunks recuperados com o score de similaridade — deixa transparente o 'porquê' da resposta. E agora o modelo cita `LinearSearchUtil.find()`, o pacote certo, e raciocina certo sobre o limite de 50 elementos — porque a resposta veio ancorada no documento real da squad."

---

## Slide 17 — O bug que quase estragou a demo (1.5 min)

> **Tom:** credibilidade técnica — mostra que isso foi testado de verdade, não só idealizado.

"Achei um problema real montando isso: o embedding de cada trecho só usava o texto da seção, não o título do documento. Resultado: o trecho certo — 'Escolha de algoritmo de busca' — perdia posição no ranking, porque só o título do documento mencionava 'squad Orders'."

"Corrigi incluindo o título do documento no embedding de cada chunk. A lição: chunking bem feito importa tanto quanto o modelo que você escolhe."

---

## Slide 18 — RAG reduz alucinação. Não elimina. (1.5 min)

"E um achado favorito: numa das rodadas, o modelo respondeu certíssimo sobre PriorityBlockingQueue e a política de ordenação — e começou a frase dizendo que o time Orders era 'da Alibaba Cloud'. Detalhe inventado, não existe em lugar nenhum do contexto."

"Mesma lição do rascunho de postmortem: RAG ancora a resposta em fatos reais, mas não elimina alucinação. Revisão humana continua obrigatória."

---

## Slide 19 — Quando usar / quando não usar (1.5 min)

"Pra fechar o raciocínio: funciona bem pra tarefas estruturadas com contexto contido, ambientes com restrição de privacidade, e como primeira passada que economiza tempo do plantão."

"Não substitui revisão humana em decisão crítica, contexto amplo que o modelo não tem, ou remediação automática sem humano no loop. Regra prática: o SLM acelera. Não decide por você."

---

## Slide 20 — Obrigado! (30 seg)

_[link do repositório na tela]_

"Obrigado! O repositório está aberto, com os dois labs prontos pra rodar. Fico por aqui pras perguntas."

---

## Backup / perguntas frequentes esperadas

- **"Por que não usar GPT-4/Claude na nuvem?"** → o log de erro pode conter hostname interno, IP, dado de cliente — não deveria virar payload de API de terceiro. Ver seção "3h da manhã" do deck.
- **"RAG substitui fine-tuning de vez?"** → não sempre — fine-tuning ainda ganha quando o que você precisa é estilo/formato consistente sem repetir prompt longo. Pra conhecimento específico e mutável, RAG é mais barato de iterar.
- **"Isso roda em produção hoje?"** → é material de demo/laboratório, testado de ponta a ponta localmente — não tem cache incremental de embeddings, reranking, nem lida com corpus grande. Bom próximo passo se alguém perguntar "e pra escalar?".
- **"Qual modelo vocês usam?"** → `phi3` no lab de postmortem, `qwen2.5:3b` no lab de RAG (mais forte em código, mesmo porte). Ambos testados de verdade, com `gemma2:2b` como terceiro ponto de comparação.
