from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
BASE_DIR = os.path.dirname(__file__)
DB_FILE = os.path.join(BASE_DIR, "sensores.db")
DB_URL = f"sqlite:///{DB_FILE}"
engine = create_engine(DB_URL)

# --- NÍVEIS DE ALERTA (ESCALA REDUZIDA PARA MAIOR DIVERSIDADE) ---
# **Valores anteriores comentados para referência**
# CHUVA_NIVEL_2 = 40.0
# CHUVA_NIVEL_3 = 70.0
# CHUVA_NIVEL_4 = 100.0
# UMIDADE_NIVEL_3 = 0.42 # 42%
# UMIDADE_NIVEL_4 = 0.45 # 45%

# **NOVOS VALORES MAIS SENSÍVEIS (AJUSTE CONFORME NECESSÁRIO)**
CHUVA_NIVEL_2 = 20.0  # Nível Atenção (Amarelo) a partir de 20mm
CHUVA_NIVEL_3 = 35.0  # Nível Alerta (Vermelho) a partir de 35mm
CHUVA_NIVEL_4 = 50.0  # Nível Alerta Máximo (Roxo) a partir de 50mm
UMIDADE_NIVEL_3 = 0.38 # 38% de umidade para ajudar a disparar o Nível 3
UMIDADE_NIVEL_4 = 0.40 # 40% de umidade para ajudar a disparar o Nível 4

# --- OTIMIZAÇÃO: Carrega os dados na memória uma única vez ---
DF_PLUVIOMETRIA = pd.DataFrame()
DF_SENSORES = pd.DataFrame()

def carregar_dados_para_memoria():
    global DF_PLUVIOMETRIA, DF_SENSORES
    try:
        DF_PLUVIOMETRIA = pd.read_sql_table('pluviometria', engine, parse_dates=['data_hora'])
        DF_SENSORES = pd.read_sql_table('sensores_umidade', engine, parse_dates=['data_hora'])
        print(f"SUCESSO: {len(DF_PLUVIOMETRIA)} pontos de dados carregados para a simulação.")
    except Exception as e:
        print(f"ERRO ao carregar dados para a memória: {e}")

def inicializar_banco_de_dados():
    if not os.path.exists(DB_FILE):
        print("Iniciando migração dos arquivos Excel...")
        try:
            pd.read_excel(os.path.join(BASE_DIR, "dados_sensores.xlsx")).to_sql('sensores_umidade', engine, if_exists='replace', index=False)
            pd.read_excel(os.path.join(BASE_DIR, "pluviometria.xlsx")).to_sql('pluviometria', engine, if_exists='replace', index=False)
            print("Migração concluída.")
        except Exception as e:
            print(f"ERRO CRÍTICO DURANTE A MIGRAÇÃO: {e}")
            exit()

inicializar_banco_de_dados()
carregar_dados_para_memoria()

# --- Rotas Principais ---
@app.route("/")
def index(): return render_template("index.html")

@app.route("/login", methods=["POST"])
def login(): return redirect(url_for("mapa"))

@app.route("/mapa")
def mapa(): return render_template("mapa.html")

@app.route("/dados")
def dados():
    # Captura o índice da simulação passado como parâmetro na URL
    indice = request.args.get('indice', default=None)
    # Envia o índice para o template poder usá-lo no JavaScript
    return render_template("dados.html", indice_simulacao=indice)

# --- API ---
@app.route("/api/info_simulacao")
def info_simulacao():
    return jsonify({'total_pontos': len(DF_PLUVIOMETRIA)})

@app.route("/api/status_alerta")
def status_alerta():
    try:
        indice = request.args.get('indice', default=None, type=int)
        if DF_PLUVIOMETRIA.empty: return jsonify({"error": "Dados não carregados no servidor."}), 500

        if indice is not None and 0 <= indice < len(DF_PLUVIOMETRIA):
            data_atual = DF_PLUVIOMETRIA.iloc[indice]['data_hora']
            ponto_atual_sensores = DF_SENSORES.iloc[indice]
        else:
            data_atual = DF_PLUVIOMETRIA.iloc[-1]['data_hora']
            ponto_atual_sensores = DF_SENSORES.iloc[-1]

        limite_tempo = data_atual - timedelta(hours=72)
        df_recente = DF_PLUVIOMETRIA[(DF_PLUVIOMETRIA['data_hora'] > limite_tempo) & (DF_PLUVIOMETRIA['data_hora'] <= data_atual)]
        acumulado_chuva = df_recente['Precipitação'].sum()

        colunas_umidade = [col for col in DF_SENSORES.columns if 'profundidade' in col]
        umidade_media = ponto_atual_sensores[colunas_umidade].mean() if colunas_umidade else None
        
        nivel_alerta = 1
        if acumulado_chuva >= CHUVA_NIVEL_4 and umidade_media is not None and umidade_media >= UMIDADE_NIVEL_4: nivel_alerta = 4
        elif acumulado_chuva >= CHUVA_NIVEL_3 and umidade_media is not None and umidade_media >= UMIDADE_NIVEL_3: nivel_alerta = 3
        elif acumulado_chuva >= CHUVA_NIVEL_2: nivel_alerta = 2

        return jsonify({
            'nivel_alerta': nivel_alerta, 'acumulado_chuva_72h': round(acumulado_chuva, 2),
            'umidade_media_solo': round(umidade_media, 3) if umidade_media is not None else None,
            'timestamp': data_atual.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e: return jsonify({"error": "Erro ao calcular alerta.", "details": str(e)}), 500

@app.route("/dados_json")
def dados_json():
    df = DF_SENSORES.copy()
    for col in df.select_dtypes(include=['datetime64[ns]']).columns: df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.replace({np.nan: None})
    return jsonify(df.to_dict(orient="records"))

@app.route("/pluviometria_json")
def pluviometria_json():
    df = DF_PLUVIOMETRIA.copy()
    for col in df.select_dtypes(include=['datetime64[ns]']).columns: df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.replace({np.nan: None})
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

