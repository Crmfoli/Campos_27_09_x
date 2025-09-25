from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

# rota principal
@app.route("/")
def index():
    return render_template("dados.html")

# rota para fornecer os dados em JSON
@app.route("/dados_json")
def dados_json():
    excel_path = os.path.join(os.getcwd(), "dados_sensores.xlsx")
    
    try:
        df = pd.read_excel(excel_path)
        # pega só os 10 últimos registros
        df = df.tail(10)
        data = df.to_dict(orient="records")
        return jsonify(data)
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == "__main__":
    app.run(debug=True)

