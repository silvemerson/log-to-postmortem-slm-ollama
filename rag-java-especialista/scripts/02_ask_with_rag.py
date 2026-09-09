#!/usr/bin/env python3
"""
02_ask_with_rag.py
-------------------
Faz a MESMA pergunta de 01_ask_without_rag.py, mas agora com RAG: busca no
índice vetorial (output/index.json, gerado por 00_build_index.py) os chunks
mais relevantes e injeta esse contexto no prompt antes de perguntar ao SLM.

Uso:
    python3 scripts/02_ask_with_rag.py
    python3 scripts/02_ask_with_rag.py "sua pergunta aqui"

Variáveis de ambiente (opcionais):
    MODEL        - modelo do Ollama para gerar a resposta (default: qwen2.5:3b)
    EMBED_MODEL  - modelo do Ollama para gerar embeddings (default: nomic-embed-text)
    OLLAMA_HOST  - endereço da API do Ollama (default: http://localhost:11434)
"""

import sys

from common import (
    MODEL,
    OLLAMA_HOST,
    call_ollama_generate,
    check_ollama,
    get_embedding,
    load_index,
    retrieve_top_k,
)
from common import EMBED_MODEL

# Mesma pergunta padrão do script 01, para permitir comparação direta.
DEFAULT_QUESTION = (
    "Como devo implementar uma busca em uma lista de 30 pedidos no time Orders? "
    "Qual algoritmo e qual classe devo usar?"
)

# Corpus pequeno (poucas dezenas de chunks) -> vale a pena recuperar um pouco
# mais que o "top-3" clássico para não perder um chunk relevante que ficou
# embolado em score com os outros do mesmo documento. Em um corpus maior,
# volte para 3-4 e considere técnicas de reranking.
TOP_K = 5


def build_prompt(question: str, context_chunks: list) -> str:
    """Monta o prompt "aumentado": contexto recuperado + pergunta.

    Instrui o modelo a se basear no contexto fornecido em vez de "chutar"
    conhecimento genérico — esse é o coração do RAG.
    """
    context_text = "\n\n".join(
        f"[Fonte: {chunk['source']} | Seção: {chunk['heading']}]\n{chunk['text']}"
        for chunk in context_chunks
    )
    return f"""Você é um engenheiro Java sênior especialista no time Orders. Responda à pergunta abaixo de forma objetiva e prática, em português, baseando-se PRIORITARIAMENTE no contexto fornecido (documentação interna da squad). Se o contexto não cobrir algo, diga isso claramente em vez de inventar.

--- CONTEXTO RECUPERADO ---
{context_text}
--- FIM DO CONTEXTO ---

Pergunta: {question}"""


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or DEFAULT_QUESTION

    check_ollama(OLLAMA_HOST)
    index = load_index()

    print("================================================================")
    print(" COM RAG (modelo respondendo com contexto recuperado)")
    print("================================================================")
    print(f"Pergunta: {question}")
    print()

    # 1. Embedda a pergunta com o mesmo modelo usado para indexar os documentos
    question_embedding = get_embedding(OLLAMA_HOST, EMBED_MODEL, question)

    # 2. Recupera os chunks mais similares (busca por similaridade de cosseno)
    top_matches = retrieve_top_k(question_embedding, index, k=TOP_K)

    print(f"Chunks recuperados (top {TOP_K}):")
    for chunk, score in top_matches:
        print(f"  - [{score:.3f}] {chunk['source']} → {chunk['heading']}")
    print()

    # 3. Monta o prompt aumentado com o contexto recuperado
    context_chunks = [chunk for chunk, _score in top_matches]
    prompt = build_prompt(question, context_chunks)

    # 4. Gera a resposta final com o modelo de texto
    answer = call_ollama_generate(OLLAMA_HOST, MODEL, prompt)

    print("Resposta:")
    print(answer)
    print("================================================================")


if __name__ == "__main__":
    main()
