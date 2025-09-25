from flask import Flask, render_template, request, redirect, url_for

# Inicializa a aplicação Flask
app = Flask(__name__)

# Rota principal ('/') que exibe a página de login
@app.route('/')
def home():
    """Renderiza o formulário de login inicial."""
    return render_template('index.html')

# Rota '/login' que recebe os dados do formulário e redireciona
@app.route('/login', methods=['POST'])
def login():
    """Recebe os dados do formulário e, se válidos, redireciona para o mapa."""
    email = request.form.get('email')
    api_token = request.form.get('api_token')
    senha = request.form.get('senha')

    # Imprime os dados no console do servidor (no Render, isso aparecerá nos logs)
    print("--- Tentativa de Acesso Recebida ---")
    print(f"E-mail: {email}")
    print(f"API Token: {api_token}")
    print("-----------------------------------")

    # Aqui entraria a sua lógica real de validação de usuário e senha.
    # Como é um exemplo, vamos redirecionar diretamente.
    
    # Redireciona o usuário para a função que exibe a página do mapa
    return redirect(url_for('pagina_do_mapa'))

# Nova rota para a página do mapa
@app.route('/mapa')
def pagina_do_mapa():
    """Renderiza a página que conterá o mapa."""
    return render_template('mapa.html')

# Inicia o servidor quando o script é executado
if __name__ == '__main__':
    app.run(debug=True)

