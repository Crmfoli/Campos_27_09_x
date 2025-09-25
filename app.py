from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Alterado de volta para ler o ficheiro .xlsx
DATA_FILE = os.path.join(os.path.dirname(__file__), "dados_sensores.xlsx")


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


# Rota que entrega os dados do Excel em JSON, tratando valores inválidos
@app.route("/dados_json")
def dados_json():
    try:
        # Usamos read_excel para ler o ficheiro .xlsx
        df = pd.read_excel(DATA_FILE)

        # A lógica para limpar os dados permanece a mesma, para garantir a compatibilidade com JSON
        
        # Converte colunas de data/hora para string.
        for col in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S').where(df[col].notna(), None)

        # CORREÇÃO DEFINITIVA:
        # 1. Converte todo o DataFrame para o tipo 'object'.
        # 2. Substitui todos os valores nulos (NaN, NaT, etc.) por None do Python.
        # Isto garante que não haja tipos de dados incompatíveis com JSON.
        df_final = df.astype(object).where(pd.notnull(df), None)
        
        return jsonify(df_final.to_dict(orient="records"))
    except FileNotFoundError:
        print(f"Erro: O ficheiro de dados '{DATA_FILE}' não foi encontrado.")
        return jsonify({"error": "Ficheiro de dados não encontrado no servidor."})
    except Exception as e:
        print(f"Erro ao processar o ficheiro de dados: {e}") # Log do erro no terminal
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
