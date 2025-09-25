from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Caminho do Excel
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "dados_sensores.xlsx")


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
        df = pd.read_excel(EXCEL_FILE)
        # Converte valores 'NaN' (Not a Number) do pandas para 'None' em Python.
        # Isso é necessário porque 'NaN' não é um valor JSON válido, mas 'None' é convertido para 'null'.
        df_sem_nan = df.where(pd.notnull(df), None)
        return jsonify(df_sem_nan.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
