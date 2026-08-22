#!/usr/bin/env python3
"""
02_generate_postmortem.py
-------------------------
Passo 2 do lab: pega a análise gerada pelo script anterior (output/analysis.json)
e pede ao SLM um RASCUNHO de postmortem estruturado em Markdown.

Importante: o resultado é um rascunho para acelerar o trabalho do time —
ele SEMPRE precisa de revisão humana antes de ser publicado.

Uso:
    python3 scripts/02_generate_postmortem.py

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

ROOT_DIR = Path(__file__).resolve().parent.parent
ANALYSIS_FILE = ROOT_DIR / "output" / "analysis.json"
LOG_FILE = ROOT_DIR / "samples" / "error.log"
OUTPUT_FILE = ROOT_DIR / "output" / "postmortem.md"


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


def build_prompt(analysis_text: str, log_content: str) -> str:
    """Monta o prompt do postmortem: 6 seções fixas + regras anti-alucinação.

    Incluímos também o log original para dar contexto de timeline ao modelo.
    """
    return f"""Você é um engenheiro SRE escrevendo um RASCUNHO de postmortem de incidente.

Com base na análise técnica e no log abaixo, gere um postmortem em Markdown, em português, com exatamente estas seções:

## Resumo do incidente
## Timeline
## Causa raiz
## Impacto
## Ações corretivas
## Ações preventivas

Regras:
- Comece o documento com o título '# [RASCUNHO] Postmortem - Falha de conexão com banco de dados' e um aviso destacado de que este é um RASCUNHO gerado por IA e PRECISA de revisão humana antes de ser publicado.
- Na Timeline, use os timestamps reais presentes no log.
- Seja objetivo; onde faltar informação, escreva '(a confirmar pelo time)' em vez de inventar detalhes.

--- ANÁLISE TÉCNICA ---
{analysis_text}
--- LOG ORIGINAL ---
{log_content}
--- FIM ---"""


def call_ollama(host: str, model: str, prompt: str, timeout: int) -> dict:
    """Faz o POST em /api/generate e devolve a resposta JSON completa da API.

    "stream": False -> resposta completa em um único JSON, mais fácil de tratar.
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
    if not ANALYSIS_FILE.is_file():
        print(f"ERRO: análise não encontrada: {ANALYSIS_FILE}", file=sys.stderr)
        print("Rode primeiro: python3 scripts/01_analyze_log.py", file=sys.stderr)
        sys.exit(1)

    check_ollama(OLLAMA_HOST, MODEL)

    # --- Montagem do prompt -------------------------------------------------
    # Extrai só o texto da análise (campo "response" do JSON salvo pelo script 1)
    analysis = json.loads(ANALYSIS_FILE.read_text(encoding="utf-8"))
    analysis_text = analysis.get("response", "")
    log_content = LOG_FILE.read_text(encoding="utf-8")

    prompt = build_prompt(analysis_text, log_content)

    # --- Requisição para o Ollama -------------------------------------------
    print(f"Gerando rascunho de postmortem com o modelo '{MODEL}' via {OLLAMA_HOST} ...")
    print("(isso pode levar alguns minutos em CPU)")
    print()

    response = call_ollama(OLLAMA_HOST, MODEL, prompt, timeout=600)

    # --- Saída --------------------------------------------------------------
    # Salva apenas o Markdown gerado pelo modelo, pronto para leitura/revisão
    OUTPUT_FILE.write_text(response.get("response", ""), encoding="utf-8")

    print("Rascunho de postmortem gerado com sucesso!")
    print()
    print(f"  Arquivo: {OUTPUT_FILE}")
    print()
    print("Lembrete: este é um RASCUNHO gerado por IA.")
    print("Revise com o time antes de publicar.")


if __name__ == "__main__":
    main()
