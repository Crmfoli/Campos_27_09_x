from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS (SOLUÇÃO 3) ---
BASE_DIR = os.path.dirname(__file__)
DB_FILE = os.path.join(BASE_DIR, "sensores.db")
DB_URL = f"sqlite:///{DB_FILE}"
engine = create_engine(DB_URL)

def inicializar_banco_de_dados():
    """
    Função especialista que verifica se o banco de dados existe.
    Se não existir, lê os arquivos Excel uma única vez e migra os dados.
    """
    if not os.path.exists(DB_FILE):
        print("="*50)
        print(f"BANCO DE DADOS NÃO ENCONTRADO EM: {DB_FILE}")
        print("Iniciando migração única dos arquivos Excel para o banco de dados...")
        print("Este processo pode demorar um pouco, mas só acontece uma vez.")
        print("="*50)
        
        try:
            # Caminhos para os arquivos Excel originais
            excel_sensores = os.path.join(BASE_DIR, "dados_sensores.xlsx")
            excel_pluviometria = os.path.join(BASE_DIR, "pluviometria.xlsx")

            # Lê os dados dos arquivos Excel
            df_sensores = pd.read_excel(excel_sensores)
            df_pluviometria = pd.read_excel(excel_pluviometria)

            # Salva os dataframes como tabelas no banco de dados SQLite
            df_sensores.to_sql('sensores_umidade', engine, if_exists='replace', index=False)
            df_pluviometria.to_sql('pluviometria', engine, if_exists='replace', index=False)

            print("SUCESSO: Migração dos dados para o banco de dados concluída!")
        except Exception as e:
            print(f"ERRO CRÍTICO DURANTE A MIGRAÇÃO: {e}")
            # Se a migração falhar, o programa para para evitar mais erros.
            exit()

# Executa a verificação e possível migração assim que a aplicação inicia
inicializar_banco_de_dados()

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


# --- API DE DADOS (AGORA LENDO DO BANCO DE DADOS) ---

def formatar_dataframe_para_json(df):
    """Trata os dados lidos do banco para serem compatíveis com JSON."""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.replace({np.nan: None}).to_dict(orient="records")

@app.route("/acumulado_72h")
def acumulado_72h():
    try:
        # A consulta SQL é muito mais rápida do que processar com pandas
        df = pd.read_sql_table('pluviometria', engine, parse_dates=['data_hora'])
        limite_tempo = datetime.now() - timedelta(hours=72)
        df_recente = df[df['data_hora'] >= limite_tempo]
        acumulado = df_recente['Precipitação'].sum()
        return jsonify({'acumulado_72h': round(acumulado, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# SENSORES DE UMIDADE
@app.route("/dados_json")
def dados_json():
    df = pd.read_sql_table('sensores_umidade', engine)
    return jsonify(formatar_dataframe_para_json(df))

@app.route("/dados_iniciais")
def dados_iniciais():
    df = pd.read_sql_query("SELECT * FROM sensores_umidade LIMIT 20", engine)
    return jsonify(formatar_dataframe_para_json(df))

# PLUVIOMETRIA
@app.route("/pluviometria_json")
def pluviometria_json():
    df = pd.read_sql_table('pluviometria', engine)
    return jsonify(formatar_dataframe_para_json(df))

@app.route("/pluviometria_iniciais")
def pluviometria_iniciais():
    df = pd.read_sql_query("SELECT * FROM pluviometria LIMIT 20", engine)
    return jsonify(formatar_dataframe_para_json(df))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


