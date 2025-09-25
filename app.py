# Adicionamos 'redirect' e 'url_for' para redirecionar o usuário
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Rota principal ('/') que exibe a página de login (sem alterações)
@app.route('/')
def home():
    return render_template('index.html')

# Rota '/login' que recebe os dados e AGORA REDIRECIONA
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    api_token = request.form.get('api_token')
    senha = request.form.get('senha')

    print("--- Tentativa de Acesso Recebida ---")
    print(f"E-mail: {email}")
    print(f"API Token: {api_token}")
    print("-----------------------------------")

    #
    # NESTE PONTO, VOCÊ FARIA A VALIDAÇÃO REAL DOS DADOS
    #
    
    # Se a validação for bem-sucedida, redirecionamos para a página do mapa
    # A linha abaixo foi a principal alteração nesta função
    return redirect(url_for('pagina_do_mapa'))

# --- NOVA ROTA PARA A PÁGINA DO MAPA ---
# Esta é a nova função que vai renderizar a página com o mapa
@app.route('/mapa')
def pagina_do_mapa():
    """Renderiza a página que conterá o mapa."""
    return render_template('mapa.html')


if __name__ == '__main__':
    app.run(debug=True)
