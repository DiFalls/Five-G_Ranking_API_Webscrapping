#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API que consome o ranking em https://fiveg.schoolking.com.br/ranking/ranking.php
e retorna os dados em JSON no endpoint /dados, com nome limpo e time separado.
"""

import os
import time
import re
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Cache simples em memória
cache = {"data": None, "timestamp": 0}

def extrair_time(nickname: str) -> str:
    """Extrai o conteúdo entre chaves { } como 'time'."""
    match = re.search(r"\{([^}]+)\}", nickname)
    return match.group(1).strip() if match else "Sem Time"

def limpar_nome(nickname: str) -> str:
    """Remove símbolos de time e espaços extras, deixando apenas o apelido."""
    nome = re.sub(r"\{.*?\}", "", nickname).strip()
    return nome

def scrape_site():
    url = "https://fiveg.schoolking.com.br/ranking/ranking.php"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return {"error": "failed_fetch", "message": str(e)}

    results = []
    for player in data:
        nickname = player.get("nickname", "").strip()
        results.append({
            "nome": limpar_nome(nickname),
            "time": extrair_time(nickname),
            "pontos": int(player.get("total_score", 0)),
            "combo": int(player.get("combo", 0))
        })

    if not results:
        # fallback se não houver dados
        return [
            { "nome": "Player1", "time": "Team A", "pontos": 120, "combo": 3 },
            { "nome": "Player2", "time": "Team B", "pontos": 95, "combo": 1 }
        ]
    return results

@app.route("/")
def home():
    return "API is running. Use /dados to get ranking data."

@app.route("/dados")
def dados():
    # Cache válido por 10 minutos
    if time.time() - cache["timestamp"] > 600 or cache["data"] is None:
        cache["data"] = scrape_site()
        cache["timestamp"] = time.time()
    return jsonify(cache["data"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
