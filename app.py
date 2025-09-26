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

# --- SOLUÇÃO DE PERFORMANCE: CACHE EM MEMÓRIA ---
_cache = {}
CACHE_TIMEOUT = timedelta(minutes=5) # Define que os dados ficarão em cache por 5 minutos

def get_cached_excel_data(caminho_arquivo, num_linhas=None):
    """
    Função especialista que busca dados do cache ou lê o arquivo Excel se o cache estiver expirado.
    """
    cache_key = f"{caminho_arquivo}_{num_linhas}"
    agora = datetime.now()

    # Se o dado está no cache e não expirou, retorna imediatamente.
    if cache_key in _cache:
        dados, timestamp = _cache[cache_key]
        if agora - timestamp < CACHE_TIMEOUT:
            print(f"CACHE HIT: Retornando dados rápidos para {os.path.basename(caminho_arquivo)}")
            return dados

    # Se não está no cache ou expirou, lê o arquivo (operação lenta).
    print(f"CACHE MISS: Lendo arquivo {os.path.basename(caminho_arquivo)} do disco.")
    try:
        df = pd.read_excel(caminho_arquivo, nrows=num_linhas)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        dados_limpos = df.replace({np.nan: None}).to_dict(orient="records")
        
        # Armazena os novos dados e o tempo atual no cache.
        _cache[cache_key] = (dados_limpos, agora)
        return dados_limpos
        
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


# --- API de Dados (AGORA USANDO O CACHE) ---

@app.route("/acumulado_72h")
def acumulado_72h():
    # Esta função ainda lê o arquivo diretamente para garantir o cálculo mais recente.
    # Otimizações futuras podem cachear este resultado também.
    try:
        df = pd.read_excel(EXCEL_PLUVIOMETRIA)
        df['data_hora'] = pd.to_datetime(df['data_hora'])
        limite_tempo = datetime.now() - timedelta(hours=72)
        df_recente = df[df['data_hora'] >= limite_tempo]
        acumulado = df_recente['Precipitação'].sum()
        return jsonify({'acumulado_72h': round(acumulado, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# SENSORES DE UMIDADE
@app.route("/dados_json")
def dados_json():
    return jsonify(get_cached_excel_data(EXCEL_SENSORES))

@app.route("/dados_iniciais")
def dados_iniciais():
    return jsonify(get_cached_excel_data(EXCEL_SENSORES, num_linhas=20))

# PLUVIOMETRIA
@app.route("/pluviometria_json")
def pluviometria_json():
    return jsonify(get_cached_excel_data(EXCEL_PLUVIOMETRIA))

@app.route("/pluviometria_iniciais")
def pluviometria_iniciais():
    return jsonify(get_cached_excel_data(EXCEL_PLUVIOMETRIA, num_linhas=20))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

