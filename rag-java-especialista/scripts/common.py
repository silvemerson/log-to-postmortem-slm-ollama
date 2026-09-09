"""
common.py
---------
Funções compartilhadas pelos scripts do lab de RAG (00_build_index.py,
01_ask_without_rag.py, 02_ask_with_rag.py).

Mesma filosofia do lab de postmortem: só standard library (urllib + json),
nada de "pip install" para acompanhar a demo.
"""

import json
import math
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Tuple

# --- Configuração compartilhada ---------------------------------------------
# qwen2.5:3b como default aqui (em vez do phi3 do lab de postmortem): mesmo
# porte, mas com foco maior em código — combina melhor com o tema deste lab.
MODEL = os.environ.get("MODEL", "qwen2.5:3b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

ROOT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = ROOT_DIR / "knowledge_base"
INDEX_FILE = ROOT_DIR / "output" / "index.json"


def check_ollama(host: str) -> None:
    """Verifica se o Ollama está acessível (GET /api/tags) antes de prosseguir.

    Em caso de falha, imprime dicas de troubleshooting e encerra com erro.
    """
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=5):
            return  # respondeu -> Ollama está de pé
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
        print(f"ERRO: não foi possível conectar ao Ollama em {host}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Troubleshooting:", file=sys.stderr)
        print("  1. O ambiente está de pé?           docker compose up -d", file=sys.stderr)
        print("  2. O container está rodando?        docker ps | grep ollama", file=sys.stderr)
        print(f"  3. Os modelos foram baixados?       docker exec ollama ollama pull {MODEL}", file=sys.stderr)
        print(f"                                       docker exec ollama ollama pull {EMBED_MODEL}", file=sys.stderr)
        print(f"  4. A porta 11434 está livre/mapeada? curl {host}/api/tags", file=sys.stderr)
        sys.exit(1)


def get_embedding(host: str, model: str, text: str) -> List[float]:
    """Chama /api/embeddings do Ollama e devolve o vetor de embedding do texto.

    Endpoint estável desde as primeiras versões do Ollama que suportam
    embeddings (retorna {"embedding": [...]}).
    """
    body = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    request = urllib.request.Request(
        f"{host}/api/embeddings",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["embedding"]
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as exc:
        print(f"ERRO: falha ao gerar embedding com o modelo '{model}': {exc}", file=sys.stderr)
        print(f"Verifique se o modelo de embedding está disponível: docker exec ollama ollama pull {model}", file=sys.stderr)
        sys.exit(1)


def call_ollama_generate(host: str, model: str, prompt: str, timeout: int = 300) -> str:
    """Chama /api/generate com stream=False e devolve só o texto gerado."""
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        f"{host}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("response", "")
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
        print("ERRO: a requisição ao Ollama falhou.", file=sys.stderr)
        print(f"Verifique se o modelo '{model}' está disponível: docker exec ollama ollama list", file=sys.stderr)
        sys.exit(1)


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Similaridade de cosseno entre dois vetores, sem depender de numpy."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def split_into_chunks(markdown_text: str, source: str) -> List[dict]:
    """Divide um arquivo Markdown em chunks por seção ('## Título').

    Cada chunk carrega metadados (arquivo de origem, título do documento e
    título da seção) para facilitar mostrar, na demo, exatamente qual trecho
    foi recuperado.

    Importante: o título do documento (linha '# ...') é guardado à parte e
    propagado para TODOS os chunks do arquivo (veja get_embedding_input).
    Sem isso, uma seção específica como "Escolha de algoritmo de busca" nunca
    menciona "squad Orders" explicitamente — só o título do documento o faz —
    e acaba perdendo relevância na busca por similaridade para uma pergunta
    que cita "time Orders". É um exemplo real de ajuste fino de RAG: o
    contexto do documento como um todo importa, não só o texto literal do
    chunk.
    """
    lines = markdown_text.splitlines()

    doc_title = source
    start_index = 0
    if lines and lines[0].startswith("# "):
        doc_title = lines[0][2:].strip()
        start_index = 1

    chunks: List[dict] = []
    current_heading = "Introdução"
    current_lines: List[str] = []

    def flush() -> None:
        text = "\n".join(current_lines).strip()
        if text:
            chunks.append({"source": source, "title": doc_title, "heading": current_heading, "text": text})

    for line in lines[start_index:]:
        if line.startswith("## "):
            flush()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    flush()
    return chunks


def get_embedding_input(chunk: dict) -> str:
    """Texto que efetivamente vira embedding: título do doc + seção + conteúdo.

    Usado tanto na indexação (00_build_index.py) quanto, se necessário, em
    reprocessamentos futuros — centralizado aqui para as duas pontas nunca
    divergirem.
    """
    return f"{chunk['title']}\n{chunk['heading']}\n{chunk['text']}"


def load_index() -> List[dict]:
    """Carrega o índice vetorial gerado por 00_build_index.py."""
    if not INDEX_FILE.is_file():
        print(f"ERRO: índice não encontrado: {INDEX_FILE}", file=sys.stderr)
        print("Rode primeiro: python3 scripts/00_build_index.py", file=sys.stderr)
        sys.exit(1)
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def retrieve_top_k(question_embedding: List[float], index: List[dict], k: int = 3) -> List[Tuple[dict, float]]:
    """Retorna os k chunks do índice mais similares à pergunta, com o score."""
    scored = [(chunk, cosine_similarity(question_embedding, chunk["embedding"])) for chunk in index]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]
