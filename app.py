from flask import Flask, render_template, request
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# O domínio base com a versão atual (v4)
ENDPOINT_API = "https://api.jikan.moe/v4"
TIMEOUT = 8  # timeout para requisições

def buscar_animes(termo):
    """Busca animes em paralelo"""
    try:
        res = requests.get(
            f"{ENDPOINT_API}/anime",
            params={'q': termo, 'limit': 10, 'sfw': 'true'},
            timeout=TIMEOUT
        )
        return res.json() if res.status_code == 200 else {"data": []}
    except:
        return {"data": []}

def buscar_personagens(termo):
    """Busca personagens em paralelo"""
    try:
        res = requests.get(
            f"{ENDPOINT_API}/characters",
            params={'q': termo, 'limit': 10, 'sfw': 'true'},
            timeout=TIMEOUT
        )
        return res.json() if res.status_code == 200 else {"data": []}
    except:
        return {"data": []}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/busca')
def buscar_anime(): # Removido o argumento nome_anime
    termo = request.args.get('q')
    
    if not termo:
        return "Digite algo para buscar", 400

    # Executa as duas requisições em paralelo
    with ThreadPoolExecutor(max_workers=2) as executor:
        anime_future = executor.submit(buscar_animes, termo)
        char_future = executor.submit(buscar_personagens, termo)
        
        dados_anime = anime_future.result()
        dados_char = char_future.result()

    # filtrar apenas Hentai e Ecchi pelos gêneros
    safe_list = []
    for item in dados_anime.get('data', []):
        genres = item.get('genres', [])
        genre_names = [g.get('name', '').lower() for g in genres]
        
        # Remove apenas se for Hentai ou Ecchi
        if 'hentai' in genre_names or 'ecchi' in genre_names:
            continue
        safe_list.append(item)
    dados_anime['data'] = safe_list

    return render_template("resultado.html", anime=dados_anime, personagem=dados_char)


if __name__ == '__main__':
    app.run(debug=True)