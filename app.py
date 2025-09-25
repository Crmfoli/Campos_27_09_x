from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Página inicial (login)
@app.route("/")
def index():
    return render_template("index.html")

# Página do mapa
@app.route("/mapa")
def mapa():
    return render_template("mapa.html")

# Página de dados (lê últimos 20 registros do Excel)
@app.route("/dados")
def dados():
    df = pd.read_excel("dados_sensores.xlsx")
    ultimos = df.tail(20).to_dict(orient="records")
    colunas = df.columns.tolist()
    return render_template("dados.html", dados=ultimos, colunas=colunas)

if __name__ == "__main__":
    app.run(debug=True)
