#!/usr/bin/env python3
"""
01_ask_without_rag.py
----------------------
Linha de base da demo: faz a MESMA pergunta que 02_ask_with_rag.py, mas sem
nenhum contexto recuperado — só o conhecimento que o modelo já trouxe do
pré-treinamento. Serve para mostrar, ao vivo, a diferença entre um SLM
"genérico" e um SLM "especialista" (com RAG).

Uso:
    python3 scripts/01_ask_without_rag.py
    python3 scripts/01_ask_without_rag.py "sua pergunta aqui"

Variáveis de ambiente (opcionais):
    MODEL        - modelo do Ollama (default: qwen2.5:3b)
    OLLAMA_HOST  - endereço da API do Ollama (default: http://localhost:11434)
"""

import sys

from common import MODEL, OLLAMA_HOST, call_ollama_generate, check_ollama

# Pergunta padrão: propositalmente sobre algo que só está documentado na
# convenção INTERNA da squad Orders (knowledge_base/05-convencoes-squad-orders.md).
# Um modelo sem RAG não tem como saber a resposta "certa" para esse contexto.
DEFAULT_QUESTION = (
    "Como devo implementar uma busca em uma lista de 30 pedidos no time Orders? "
    "Qual algoritmo e qual classe devo usar?"
)


def build_prompt(question: str) -> str:
    return f"""Você é um engenheiro Java sênior. Responda à pergunta abaixo de forma objetiva e prática, em português.

Pergunta: {question}"""


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or DEFAULT_QUESTION

    check_ollama(OLLAMA_HOST)

    print("================================================================")
    print(" SEM RAG (modelo respondendo só com o que já sabe)")
    print("================================================================")
    print(f"Pergunta: {question}")
    print()

    prompt = build_prompt(question)
    answer = call_ollama_generate(OLLAMA_HOST, MODEL, prompt)

    print(answer)
    print("================================================================")


if __name__ == "__main__":
    main()
