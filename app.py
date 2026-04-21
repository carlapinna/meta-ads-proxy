from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Permette chiamate da tiiny.site e Notion

META_API_BASE = "https://graph.facebook.com/v19.0/ads_archive"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/ads", methods=["GET"])
def ads():
    # Prende tutti i parametri dalla richiesta del browser e li gira a Meta
    params = dict(request.args)

    try:
        resp = requests.get(META_API_BASE, params=params, timeout=30)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": {"message": "Timeout — riprova"}}), 504
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@app.route("/proxy", methods=["GET"])
def proxy_next_page():
    # Gestisce la paginazione: riceve l'URL completo della "next page" di Meta
    url = request.args.get("url")
    if not url:
        return jsonify({"error": {"message": "Parametro 'url' mancante"}}), 400
    if not url.startswith("https://graph.facebook.com"):
        return jsonify({"error": {"message": "URL non consentito"}}), 403
    try:
        resp = requests.get(url, timeout=30)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
