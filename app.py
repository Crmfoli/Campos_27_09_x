from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np

app = Flask(__name__)

# --- Caminhos para os arquivos Excel ---
BASE_DIR = os.path.dirname(__file__)
EXCEL_FILE_SENSORES = os.path.join(BASE_DIR, "dados_sensores.xlsx")
EXCEL_FILE_PLUVIOMETRIA = os.path.join(BASE_DIR, "pluviometria.xlsx")

# --- Função auxiliar para processar DataFrames ---
def processar_dataframe(df):
    """Converte datas para string e substitui NaN por None."""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.replace({np.nan: None})

# --- Rotas da Aplicação Principal ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    # Lógica de login simplificada
    return redirect(url_for("mapa"))

@app.route("/mapa")
def mapa():
    return render_template("mapa.html")

@app.route("/dados")
def dados():
    return render_template("dados.html")

# --- Rotas da API de Dados ---

# --- DADOS DOS SENSORES ---
@app.route("/dados_json")
def dados_json():
    """Retorna todos os dados dos sensores."""
    try:
        df = pd.read_excel(EXCEL_FILE_SENSORES)
        df_processado = processar_dataframe(df)
        return jsonify(df_processado.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/dados_iniciais")
def dados_iniciais():
    """NOVO: Retorna apenas os primeiros 20 registros dos sensores para carregamento rápido."""
    try:
        df = pd.read_excel(EXCEL_FILE_SENSORES, nrows=20)
        df_processado = processar_dataframe(df)
        return jsonify(df_processado.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- DADOS DE PLUVIOMETRIA ---
@app.route("/pluviometria_json")
def pluviometria_json():
    """Retorna todos os dados de pluviometria."""
    try:
        df = pd.read_excel(EXCEL_FILE_PLUVIOMETRIA)
        df_processado = processar_dataframe(df)
        return jsonify(df_processado.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/pluviometria_iniciais")
def pluviometria_iniciais():
    """NOVO: Retorna apenas os primeiros 20 registros de pluviometria."""
    try:
        df = pd.read_excel(EXCEL_FILE_PLUVIOMETRIA, nrows=20)
        df_processado = processar_dataframe(df)
        return jsonify(df_processado.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
