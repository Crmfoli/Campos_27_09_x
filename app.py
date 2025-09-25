from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np

app = Flask(__name__)

# --- Caminhos para os dois arquivos Excel ---
BASE_DIR = os.path.dirname(__file__)
EXCEL_FILE_SENSORES = os.path.join(BASE_DIR, "dados_sensores.xlsx")
EXCEL_FILE_PLUVIOMETRIA = os.path.join(BASE_DIR, "pluviometria.xlsx") # <- Novo arquivo


# Rota inicial -> login
@app.route("/")
def index():
    return render_template("index.html")


# Rota de login
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    token = request.form.get("api_token")
    senha = request.form.get("senha")
    if email and token and senha:
        return redirect(url_for("mapa"))
    else:
        return redirect(url_for("index"))


# Rota do mapa
@app.route("/mapa")
def mapa():
    return render_template("mapa.html")


# Rota da página de dados
@app.route("/dados")
def dados():
    return render_template("dados.html")

# --- Funções de dados para SENSORES ---

@app.route("/dados_json")
def dados_json():
    try:
        df = pd.read_excel(EXCEL_FILE_SENSORES)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        df_sem_nan = df.replace({np.nan: None})
        return jsonify(df_sem_nan.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/dados_cabecalho")
def dados_cabecalho():
    try:
        df = pd.read_excel(EXCEL_FILE_SENSORES, nrows=0) 
        return jsonify(df.columns.tolist())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Novas rotas para o arquivo de PLUVIOMETRIA ---

@app.route("/pluviometria_json")
def pluviometria_json():
    try:
        df = pd.read_excel(EXCEL_FILE_PLUVIOMETRIA)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        df_sem_nan = df.replace({np.nan: None})
        return jsonify(df_sem_nan.to_dict(orient="records"))
    except FileNotFoundError:
        return jsonify({"error": "Arquivo pluviometria.xlsx não encontrado."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/pluviometria_cabecalho")
def pluviometria_cabecalho():
    try:
        df = pd.read_excel(EXCEL_FILE_PLUVIOMETRIA, nrows=0) 
        return jsonify(df.columns.tolist())
    except FileNotFoundError:
        return jsonify({"error": "Arquivo pluviometria.xlsx não encontrado."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
