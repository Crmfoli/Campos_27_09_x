from flask import Flask, render_template, request, jsonify

# Inicializa a aplicação Flask
app = Flask(__name__)

# Rota principal ('/') que exibe a página de login
@app.route('/')
def home():
    """Renderiza o nosso arquivo HTML como a página inicial."""
    return render_template('index.html')

# Rota '/login' que recebe os dados do formulário via POST
@app.route('/login', methods=['POST'])
def login():
    """Recebe os dados do formulário enviado pelo navegador."""
    email = request.form.get('email')
    api_token = request.form.get('api_token')
    senha = request.form.get('senha')

    # Imprime os dados no console do servidor (no Render, isso aparecerá nos logs)
    print("--- Tentativa de Acesso Recebida ---")
    print(f"E-mail: {email}")
    print(f"API Token: {api_token}")
    print(f"Senha: {senha}") # Em uma aplicação real, NUNCA imprima senhas!
    print("-----------------------------------")

    # Aqui você colocaria sua lógica de validação
    # Por exemplo: verificar se o usuário e senha estão corretos no banco de dados

    # Retorna uma resposta para o navegador em formato JSON
    return jsonify({
        'status': 'sucesso',
        'message': 'Dados recebidos com sucesso no servidor!'
    })

# Inicia o servidor quando o script é executado diretamente
if __name__ == '__main__':
    app.run(debug=True)