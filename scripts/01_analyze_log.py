#!/usr/bin/env python3
"""
01_analyze_log.py
-----------------
Passo 1 do lab: envia o log de erro para um SLM rodando localmente no Ollama
e pede uma análise estruturada (causa provável, componente afetado,
severidade e recomendação inicial).

Uso:
    python3 scripts/01_analyze_log.py

Variáveis de ambiente (opcionais, veja .env.example):
    MODEL        - modelo do Ollama (default: phi3)
    OLLAMA_HOST  - endereço da API do Ollama (default: http://localhost:11434)

Somente standard library: urllib.request para HTTP e json para JSON —
nada de "pip install" para acompanhar a demo.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# --- Configuração -----------------------------------------------------------
MODEL = os.environ.get("MODEL", "phi3")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Diretório raiz do repo (funciona mesmo se o script for chamado de outro lugar)
ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT_DIR / "samples" / "error.log"
OUTPUT_FILE = ROOT_DIR / "output" / "analysis.json"


def check_ollama(host: str, model: str) -> None:
    """Verifica se o Ollama está acessível (GET /api/tags) antes de prosseguir.

    Em caso de falha, imprime as dicas de troubleshooting e encerra com erro.
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
        print(f"  3. O modelo foi baixado?            docker exec ollama ollama pull {model}", file=sys.stderr)
        print(f"  4. A porta 11434 está livre/mapeada? curl {host}/api/tags", file=sys.stderr)
        sys.exit(1)


def build_prompt(log_content: str) -> str:
    """Monta o prompt estruturado com as 4 seções pedidas ao modelo."""
    return f"""Você é um engenheiro SRE experiente. Analise o log de erro abaixo e responda em português, de forma objetiva, com exatamente estas 4 seções:

1. CAUSA PROVÁVEL: qual a causa mais provável do erro?
2. COMPONENTE AFETADO: qual serviço/componente foi afetado?
3. SEVERIDADE: classifique como baixo, médio, alto ou crítico (e justifique em 1 frase).
4. RECOMENDAÇÃO INICIAL: qual o primeiro passo de investigação/mitigação?

--- LOG ---
{log_content}
--- FIM DO LOG ---"""


def call_ollama(host: str, model: str, prompt: str, timeout: int) -> dict:
    """Faz o POST em /api/generate e devolve a resposta JSON completa da API.

    "stream": False -> resposta completa em um único JSON, mais fácil de tratar.
    O módulo json cuida do escaping do log (aspas, quebras de linha etc.).
    """
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        f"{host}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
        print("ERRO: a requisição ao Ollama falhou.", file=sys.stderr)
        print(f"Verifique se o modelo '{model}' está disponível: docker exec ollama ollama list", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    # --- Pré-checagens ------------------------------------------------------
    if not LOG_FILE.is_file():
        print(f"ERRO: arquivo de log não encontrado: {LOG_FILE}", file=sys.stderr)
        sys.exit(1)

    check_ollama(OLLAMA_HOST, MODEL)

    # --- Montagem do prompt -------------------------------------------------
    log_content = LOG_FILE.read_text(encoding="utf-8")
    prompt = build_prompt(log_content)

    # --- Requisição para o Ollama -------------------------------------------
    print(f"Analisando {LOG_FILE} com o modelo '{MODEL}' via {OLLAMA_HOST} ...")
    print()

    response = call_ollama(OLLAMA_HOST, MODEL, prompt, timeout=300)

    # --- Saída --------------------------------------------------------------
    # Salva a resposta completa da API (JSON) para o próximo script consumir
    OUTPUT_FILE.write_text(json.dumps(response, ensure_ascii=False), encoding="utf-8")

    print("================================================================")
    print(f" ANÁLISE DO LOG (modelo: {MODEL})")
    print("================================================================")
    # Exibe apenas o texto gerado pelo modelo (campo "response" da API)
    print(response.get("response", ""))
    print("================================================================")
    print()
    print(f"Análise salva em: {OUTPUT_FILE}")
    print("Próximo passo:    python3 scripts/02_generate_postmortem.py")


if __name__ == "__main__":
    main()
