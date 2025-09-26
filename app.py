from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np

app = Flask(__name__)

# --- Caminhos dos Arquivos ---
BASE_DIR = os.path.dirname(__file__)
EXCEL_FILE_SENSORES = os.path.join(BASE_DIR, "dados_sensores.xlsx")
EXCEL_FILE_PLUVIOMETRIA = os.path.join(BASE_DIR, "pluviometria.xlsx")


# --- Funções Auxiliares de Leitura de Dados ---

def ler_e_tratar_excel(caminho_arquivo, num_linhas=None):
    """Lê um arquivo Excel e trata os dados para serem compatíveis com JSON."""
    try:
        df = pd.read_excel(caminho_arquivo, nrows=num_linhas)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        df_sem_nan = df.replace({np.nan: None, pd.NaT: None})
        return df_sem_nan.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": f"Arquivo não encontrado: {os.path.basename(caminho_arquivo)}"}
    except Exception as e:
        return {"error": str(e)}

def ler_cabecalho_excel(caminho_arquivo):
    """Lê apenas o cabeçalho de um arquivo Excel de forma eficiente."""
    try:
        df = pd.read_excel(caminho_arquivo, nrows=0)
        return df.columns.tolist()
    except Exception as e:
        return {"error": str(e)}


# --- Rotas da Aplicação ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    senha = request.form.get("senha")
    if email and senha:
        return redirect(url_for("mapa"))
    else:
        return redirect(url_for("index"))

@app.route("/mapa")
def mapa():
    return render_template("mapa.html")

@app.route("/dados")
def dados():
    return render_template("dados.html")

# --- Rotas da API de Dados ---

# Dados dos Sensores de Umidade
@app.route("/dados_json")
def dados_json():
    return jsonify(ler_e_tratar_excel(EXCEL_FILE_SENSORES))

@app.route("/dados_iniciais")
def dados_iniciais():
    return jsonify(ler_e_tratar_excel(EXCEL_FILE_SENSORES, num_linhas=20))

@app.route("/dados_cabecalho")
def dados_cabecalho():
    return jsonify(ler_cabecalho_excel(EXCEL_FILE_SENSORES))

# Dados de Pluviometria
@app.route("/pluviometria_json")
def pluviometria_json():
    return jsonify(ler_e_tratar_excel(EXCEL_FILE_PLUVIOMETRIA))

@app.route("/pluviometria_iniciais")
def pluviometria_iniciais():
    return jsonify(ler_e_tratar_excel(EXCEL_FILE_PLUVIOMETRIA, num_linhas=20))

@app.route("/pluviometria_cabecalho")
def pluviometria_cabecalho():
    return jsonify(ler_cabecalho_excel(EXCEL_FILE_PLUVIOMETRIA))

# NOVA ROTA: Retorna o valor total do acumulado de chuva
@app.route("/ultimo_acumulado")
def ultimo_acumulado():
    try:
        df = pd.read_excel(EXCEL_FILE_PLUVIOMETRIA)
        if 'Precipitação' in df.columns:
            # Soma todos os valores da coluna, tratando valores não numéricos
            acumulado = pd.to_numeric(df['Precipitação'], errors='coerce').sum()
            return jsonify({"acumulado": round(acumulado, 2)})
        else:
            return jsonify({"error": "Coluna 'Precipitação' não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


