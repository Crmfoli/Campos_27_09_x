from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np

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
        # Converte colunas de data/hora para string no formato ISO
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        # Substitui NaN por None (que se torna null em JSON)
        df_limpo = df.replace({np.nan: None})
        return df_limpo.to_dict(orient="records")
    except FileNotFoundError:
        return {"error": f"Arquivo não encontrado: {os.path.basename(caminho_arquivo)}"}
    except Exception as e:
        return {"error": str(e)}

# --- Rotas Principais da Aplicação ---

@app.route("/")
def index():
    """Rota da página inicial de login."""
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    """Rota de validação de login (simplificada)."""
    email = request.form.get("email")
    senha = request.form.get("senha")
    if email and senha:
        return redirect(url_for("mapa"))
    return redirect(url_for("index"))

@app.route("/mapa")
def mapa():
    """Rota que serve a página do mapa."""
    return render_template("mapa.html")

@app.route("/dados")
def dados():
    """Rota que serve a página de dados com os gráficos."""
    return render_template("dados.html")


# --- API de Dados para os Gráficos (Frontend) ---

# SENSORES DE UMIDADE
@app.route("/dados_json")
def dados_json():
    dados = ler_e_tratar_excel(EXCEL_SENSORES)
    return jsonify(dados)

@app.route("/dados_iniciais")
def dados_iniciais():
    dados = ler_e_tratar_excel(EXCEL_SENSORES, num_linhas=20)
    return jsonify(dados)

# PLUVIOMETRIA
@app.route("/pluviometria_json")
def pluviometria_json():
    dados = ler_e_tratar_excel(EXCEL_PLUVIOMETRIA)
    return jsonify(dados)

@app.route("/pluviometria_iniciais")
def pluviometria_iniciais():
    dados = ler_e_tratar_excel(EXCEL_PLUVIOMETRIA, num_linhas=20)
    return jsonify(dados)


# --- Ponto de Entrada da Aplicação ---

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
