from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# O domínio base com a versão atual (v4)
ENDPOINT_API = "https://api.jikan.moe/v4"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/busca')
def buscar_anime(): # Removido o argumento nome_anime
    termo = request.args.get('q')
    
    if not termo:
        return "Digite algo para buscar", 400

    # Busca em Animes
    res_anime = requests.get(f"{ENDPOINT_API}/anime", params={'q': termo, 'limit': 10})
    # Busca em Personagens
    res_char = requests.get(f"{ENDPOINT_API}/characters", params={'q': termo, 'limit': 10})

    # Verifica se as requisições deram certo antes de converter para json
    dados_anime = res_anime.json() if res_anime.status_code == 200 else {"data": []}
    dados_char = res_char.json() if res_char.status_code == 200 else {"data": []}

    return render_template("resultado.html", anime=dados_anime, personagem=dados_char)


if __name__ == '__main__':
    app.run(debug=True)