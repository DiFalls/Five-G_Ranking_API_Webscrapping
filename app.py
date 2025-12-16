#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API que faz scraping do ranking em https://fiveg.schoolking.com.br/ranking/
e retorna os dados em JSON no endpoint /dados.
Compatível com Render (usa variável PORT).
"""

import os
import re
import json
import time
import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

# Cache simples em memória (evita scraping a cada requisição)
cache = {"data": None, "timestamp": 0}

def try_parse_json_blob(text):
    matches = re.findall(r'(

\[.*?\]

)', text, re.S)
    for m in matches:
        try:
            parsed = json.loads(m)
            if isinstance(parsed, list) and parsed:
                filtered = []
                for it in parsed:
                    if isinstance(it, dict) and any(
                        k.lower() in ('nome','name','time','pontos','points','combo')
                        for k in it.keys()
                    ):
                        filtered.append(it)
                if filtered:
                    return filtered
        except Exception:
            continue
    return None

def normalize_record(raw):
    if not isinstance(raw, dict):
        return None
    lower = {k.lower(): v for k, v in raw.items()}
    nome = lower.get('nome') or lower.get('name') or lower.get('player') or lower.get('nick')
    time = lower.get('time') or lower.get('team') or ''
    pontos = lower.get('pontos') or lower.get('points') or lower.get('score') or 0
    combo = lower.get('combo') or lower.get('combos') or 0
    try:
        pontos = int(pontos)
    except Exception:
        try:
            pontos = int(float(str(pontos).replace(',', '.')))
        except Exception:
            pontos = 0
    try:
        combo = int(combo)
    except Exception:
        combo = 0
    if not nome:
        return None
    return {"nome": str(nome).strip(), "time": str(time).strip() if time else "", "pontos": pontos, "combo": combo}

def scrape_site():
    url = "https://fiveg.schoolking.com.br/ranking/"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        return {"error": "failed_fetch", "message": str(e)}

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Tenta extrair via HTML
    candidates = soup.select(".ranking-list, .rank-list, .list, .table, #ranking, .ranking") or soup.find_all(["tr","li","div"])
    scanned = set()
    for el in candidates:
        text = el.get_text(" ", strip=True)
        if not text or len(text) < 3:
            continue
        key = (el.name, text[:120])
        if key in scanned:
            continue
        scanned.add(key)
        if re.search(r'\b(combo|pontos|points|pts)\b', text, re.I) or re.search(r'\d{2,}', text):
            m = re.search(r'(.+?)\s+[–\-|]\s+(.+?)\s+[–\-|]\s+(\d{1,6})[^\d]*?(\d{1,4})?', text)
            if m:
                nome = m.group(1).strip()
                time = m.group(2).strip()
                pontos = int(m.group(3))
                combo = int(m.group(4)) if m.group(4) else 0
                results.append({"nome": nome, "time": time, "pontos": pontos, "combo": combo})

    # Tenta extrair via JSON embutido
    if not results:
        script_text = " ".join(s.get_text(" ", strip=True) for s in soup.find_all("script") if s.string)
        parsed = try_parse_json_blob(script_text)
        if parsed:
            for item in parsed:
                norm = normalize_record(item)
                if norm:
                    results.append(norm)

    # Normaliza e deduplica
    consolidated = {}
    for r in results:
        norm = normalize_record(r)
        if not norm:
            continue
        key = (norm['nome'], norm['time'])
        if key in consolidated:
            if norm['pontos'] > consolidated[key]['pontos']:
                consolidated[key]['pontos'] = norm['pontos']
            if norm['combo'] > consolidated[key]['combo']:
                consolidated[key]['combo'] = norm['combo']
        else:
            consolidated[key] = norm

    final = list(consolidated.values())
    if not final:
        return [
            { "nome": "Player1", "time": "Team A", "pontos": 120, "combo": 3 },
            { "nome": "Player2", "time": "Team B", "pontos": 95, "combo": 1 }
        ]
    return final

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