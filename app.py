from flask import Flask, render_template, request, redirect, url_for, jsonify
import openpyxl  # Usaremos openpyxl diretamente para eficiência
import os
from datetime import datetime  # Para formatar datas corretamente

app = Flask(__name__)

# Caminho do Excel
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "dados_sensores.xlsx")

# ALTERAÇÃO: Função auxiliar otimizada para ler o Excel linha por linha
def processar_excel(filepath, max_rows=None):
    """Lê um arquivo Excel de forma eficiente, sem carregar tudo na memória."""
    try:
        workbook = openpyxl.load_workbook(filepath, read_only=True)
        sheet = workbook.active
        
        # Pega o cabeçalho da primeira linha
        header = [cell.value for cell in sheet[1]]
        data = []
        
        # Itera sobre as linhas de dados
        # min_row=2 para pular o cabeçalho
        for i, row in enumerate(sheet.iter_rows(min_row=2)):
            if max_rows and i >= max_rows:
                break
            
            row_dict = {}
            for col_name, cell in zip(header, row):
                value = cell.value
                # Formata a data se for do tipo datetime
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                
                # openpyxl já retorna None para células vazias, o que é perfeito para JSON
                row_dict[col_name] = value
            data.append(row_dict)
            
        return data
    finally:
        # Garante que o arquivo seja fechado
        if 'workbook' in locals():
            workbook.close()


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


# ALTERAÇÃO: Rota atualizada para usar o leitor otimizado
@app.route("/dados_json")
def dados_json():
    try:
        data = processar_excel(EXCEL_FILE)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ALTERAÇÃO: Rota atualizada para usar o leitor otimizado
@app.route("/dados_iniciais")
def dados_iniciais():
    try:
        data = processar_excel(EXCEL_FILE, max_rows=20)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
