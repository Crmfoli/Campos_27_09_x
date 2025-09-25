from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np

app = Flask(__name__)

# Caminho do Excel
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "dados_sensores.xlsx")


# Rota inicial -> login
@app.route("/")
def index():
    return render_template("index.html")


# Rota de login (simples, só redireciona para o mapa)
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    token = request.form.get("api_token")
    senha = request.form.get("senha")

    # Aqui você pode validar de verdade no futuro, por enquanto só redireciona
    if email and token and senha:
        return redirect(url_for("mapa"))
    else:
        return redirect(url_for("index"))


# Rota do mapa
@app.route("/mapa")
def mapa():
    return render_template("mapa.html")


# Rota dos dados (HTML com tabela dinâmica)
@app.route("/dados")
def dados():
    return render_template("dados.html")


# Rota que entrega todos os dados do Excel em JSON
@app.route("/dados_json")
def dados_json():
    try:
        df = pd.read_excel(EXCEL_FILE)
        # Converte colunas de data/hora para string
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Substitui NaN por None (que vira null em JSON)
        df_sem_nan = df.replace({np.nan: None})
        
        return jsonify(df_sem_nan.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ALTERAÇÃO: Nova rota que retorna apenas os 20 primeiros dados para um carregamento inicial rápido
@app.route("/dados_iniciais")
def dados_iniciais():
    try:
        # Lê apenas as 20 primeiras linhas, o que é muito mais rápido
        df = pd.read_excel(EXCEL_FILE, nrows=20) 
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        df_sem_nan = df.replace({np.nan: None})
        return jsonify(df_sem_nan.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



