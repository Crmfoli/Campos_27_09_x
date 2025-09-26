from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)

# --- Constantes de Caminho dos Arquivos ---
BASE_DIR = os.path.dirname(__file__)
EXCEL_SENSORES = os.path.join(BASE_DIR, "dados_sensores.xlsx")
EXCEL_PLUVIOMETRIA = os.path.join(BASE_DIR, "pluviometria.xlsx")


# --- Funções Auxiliares de Leitura de Dados ---

def ler_e_tratar_excel(caminho_arquivo, num_linhas=None):
    """Lê um arquivo Excel e trata os dados para serem compatíveis com JSON."""
    try:
        df = pd.read_excel(caminho_arquivo, nrows=num_linhas)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        df_limpo = df.replace({np.nan: None})
        return df_limpo.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": f"Arquivo não encontrado: {os.path.basename(caminho_arquivo)}"}
    except Exception as e:
        return {"error": str(e)}

# --- Rotas Principais da Aplicação ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    senha = request.form.get("senha")
    if email and senha:
        return redirect(url_for("mapa"))
    return redirect(url_for("index"))

@app.route("/mapa")
def mapa():
    return render_template("mapa.html")

@app.route("/dados")
def dados():
    return render_template("dados.html")


# --- API de Dados ---

# Rota especialista para calcular o acumulado das últimas 72 horas
@app.route("/acumulado_72h")
def acumulado_72h():
    try:
        df = pd.read_excel(EXCEL_PLUVIOMETRIA)
        # Converte a coluna de data para o formato datetime
        df['data_hora'] = pd.to_datetime(df['data_hora'])
        # Calcula o tempo limite (72 horas atrás)
        limite_tempo = datetime.now() - timedelta(hours=72)
        # Filtra o dataframe para pegar apenas os registros recentes
        df_recente = df[df['data_hora'] >= limite_tempo]
        # Soma a precipitação do período filtrado
        acumulado = df_recente['Precipitação'].sum()
        return jsonify({'acumulado_72h': round(acumulado, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# SENSORES DE UMIDADE
@app.route("/dados_json")
def dados_json():
    return jsonify(ler_e_tratar_excel(EXCEL_SENSORES))

@app.route("/dados_iniciais")
def dados_iniciais():
    return jsonify(ler_e_tratar_excel(EXCEL_SENSORES, num_linhas=20))

# PLUVIOMETRIA
@app.route("/pluviometria_json")
def pluviometria_json():
    return jsonify(ler_e_tratar_excel(EXCEL_PLUVIOMETRIA))

@app.route("/pluviometria_iniciais")
def pluviometria_iniciais():
    return jsonify(ler_e_tratar_excel(EXCEL_PLUVIOMETRIA, num_linhas=20))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
