from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
BASE_DIR = os.path.dirname(__file__)
DB_FILE = os.path.join(BASE_DIR, "sensores.db")
DB_URL = f"sqlite:///{DB_FILE}"
engine = create_engine(DB_URL)

# --- NÍVEIS DE ALERTA (EXEMPLOS - DEVEM SER AJUSTADOS) ---
# Chuva acumulada em 72h (mm)
CHUVA_NIVEL_2 = 40.0  # Limite para Nível 2 (Atenção)
CHUVA_NIVEL_3 = 70.0  # Limite para Nível 3 (Alerta)
CHUVA_NIVEL_4 = 100.0 # Limite para Nível 4 (Alerta Máximo)

# Umidade Média do Solo (%) - os valores no seu excel estão como fração (ex: 0.41 = 41%)
UMIDADE_NIVEL_3 = 0.42 # 42% - Umidade para Nível 3 se combinado com chuva
UMIDADE_NIVEL_4 = 0.45 # 45% - Umidade para Nível 4 se combinado com chuva


def inicializar_banco_de_dados():
    if not os.path.exists(DB_FILE):
        print("="*50)
        print(f"BANCO DE DADOS NÃO ENCONTRADO EM: {DB_FILE}")
        print("Iniciando migração única dos arquivos Excel para o banco de dados...")
        print("="*50)
        try:
            excel_sensores = os.path.join(BASE_DIR, "dados_sensores.xlsx")
            excel_pluviometria = os.path.join(BASE_DIR, "pluviometria.xlsx")
            df_sensores = pd.read_excel(excel_sensores)
            df_pluviometria = pd.read_excel(excel_pluviometria)
            df_sensores.to_sql('sensores_umidade', engine, if_exists='replace', index=False)
            df_pluviometria.to_sql('pluviometria', engine, if_exists='replace', index=False)
            print("SUCESSO: Migração dos dados para o banco de dados concluída!")
        except Exception as e:
            print(f"ERRO CRÍTICO DURANTE A MIGRAÇÃO: {e}")
            exit()

inicializar_banco_de_dados()

# --- Rotas Principais da Aplicação (sem alterações) ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("email") and request.form.get("senha"):
        return redirect(url_for("mapa"))
    return redirect(url_for("index"))

@app.route("/mapa")
def mapa():
    return render_template("mapa.html")

@app.route("/dados")
def dados():
    return render_template("dados.html")

# --- API DE DADOS ---

def formatar_dataframe_para_json(df):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.replace({np.nan: None}).to_dict(orient="records")

# NOVA ROTA DE API PARA CÁLCULO DOS ALERTAS
@app.route("/api/status_alerta")
def status_alerta():
    try:
        # 1. Calcular chuva acumulada nas últimas 72h
        df_pluviometria = pd.read_sql_table('pluviometria', engine, parse_dates=['data_hora'])
        limite_tempo = datetime.now() - timedelta(hours=72)
        df_recente = df_pluviometria[df_pluviometria['data_hora'] >= limite_tempo]
        acumulado_chuva = df_recente['Precipitação'].sum()

        # 2. Obter a última leitura de umidade do solo
        df_sensores = pd.read_sql_query("SELECT * FROM sensores_umidade ORDER BY data_hora DESC LIMIT 1", engine)
        umidade_media = None
        if not df_sensores.empty:
            # Pega todas as colunas de profundidade e calcula a média da última leitura
            colunas_umidade = [col for col in df_sensores.columns if 'profundidade' in col]
            if colunas_umidade:
                umidade_media = df_sensores[colunas_umidade].iloc[0].mean()

        # 3. Lógica para definir o nível de alerta
        nivel_alerta = 1  # Começa com o Nível 1 (Observação)

        # A lógica checa do mais grave para o mais brando
        if acumulado_chuva >= CHUVA_NIVEL_4 and umidade_media is not None and umidade_media >= UMIDADE_NIVEL_4:
            nivel_alerta = 4  # Nível 4 (Alerta Máximo)
        elif acumulado_chuva >= CHUVA_NIVEL_3 and umidade_media is not None and umidade_media >= UMIDADE_NIVEL_3:
            nivel_alerta = 3  # Nível 3 (Alerta)
        elif acumulado_chuva >= CHUVA_NIVEL_2:
            nivel_alerta = 2  # Nível 2 (Atenção)

        return jsonify({
            'nivel_alerta': nivel_alerta,
            'acumulado_chuva_72h': round(acumulado_chuva, 2),
            'umidade_media_solo': round(umidade_media, 3) if umidade_media is not None else None,
        })
        
    except Exception as e:
        print(f"ERRO na API de alerta: {e}")
        return jsonify({"error": "Erro ao calcular alerta.", "details": str(e)}), 500


# --- Rotas antigas e de dados para gráficos (sem alterações) ---
@app.route("/dados_json")
def dados_json():
    df = pd.read_sql_table('sensores_umidade', engine)
    return jsonify(formatar_dataframe_para_json(df))

@app.route("/pluviometria_json")
def pluviometria_json():
    df = pd.read_sql_table('pluviometria', engine)
    return jsonify(formatar_dataframe_para_json(df))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)