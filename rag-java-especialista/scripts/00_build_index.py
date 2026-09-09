#!/usr/bin/env python3
"""
00_build_index.py
------------------
Constrói o índice vetorial (RAG) a partir dos documentos em knowledge_base/.

Para cada arquivo Markdown, o texto é dividido em "chunks" (um por seção
'## Título') e cada chunk é convertido em um vetor de embedding via Ollama.
O resultado é salvo em output/index.json e consumido por 02_ask_with_rag.py.

Uso:
    python3 scripts/00_build_index.py

Variáveis de ambiente (opcionais):
    EMBED_MODEL  - modelo de embedding do Ollama (default: nomic-embed-text)
    OLLAMA_HOST  - endereço da API do Ollama (default: http://localhost:11434)

Pré-requisito: o modelo de embedding precisa estar baixado:
    docker exec ollama ollama pull nomic-embed-text
"""

import json
import sys

from common import (
    EMBED_MODEL,
    INDEX_FILE,
    KNOWLEDGE_BASE_DIR,
    OLLAMA_HOST,
    check_ollama,
    get_embedding,
    get_embedding_input,
    split_into_chunks,
)


def main() -> None:
    if not KNOWLEDGE_BASE_DIR.is_dir():
        print(f"ERRO: pasta de conhecimento não encontrada: {KNOWLEDGE_BASE_DIR}", file=sys.stderr)
        sys.exit(1)

    check_ollama(OLLAMA_HOST)

    markdown_files = sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))
    if not markdown_files:
        print(f"ERRO: nenhum arquivo .md encontrado em {KNOWLEDGE_BASE_DIR}", file=sys.stderr)
        sys.exit(1)

    print(f"Indexando {len(markdown_files)} documento(s) com o modelo de embedding '{EMBED_MODEL}' ...")
    print()

    index: list = []
    for md_file in markdown_files:
        chunks = split_into_chunks(md_file.read_text(encoding="utf-8"), source=md_file.name)
        print(f"  {md_file.name}: {len(chunks)} chunk(s)")
        for chunk in chunks:
            # Embute título do documento + título da seção + conteúdo, para o
            # embedding não perder o contexto geral do arquivo (veja o
            # comentário em common.split_into_chunks).
            chunk["embedding"] = get_embedding(OLLAMA_HOST, EMBED_MODEL, get_embedding_input(chunk))
            index.append(chunk)

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

    print()
    print(f"Índice gerado com {len(index)} chunk(s) no total.")
    print(f"Salvo em: {INDEX_FILE}")
    print()
    print("Próximo passo (compare os dois):")
    print("  python3 scripts/01_ask_without_rag.py")
    print("  python3 scripts/02_ask_with_rag.py")


if __name__ == "__main__":
    main()
