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

    # Busca em Animes (SFW)
    res_anime = requests.get(
        f"{ENDPOINT_API}/anime",
        params={'q': termo, 'limit': 10, 'sfw': 'true'}  # evita conteúdo NSFW
    )
    # Busca em Personagens (SFW)
    res_char = requests.get(
        f"{ENDPOINT_API}/characters",
        params={'q': termo, 'limit': 10, 'sfw': 'true'}
    )

    # Verifica se as requisições deram certo antes de converter para json
    dados_anime = res_anime.json() if res_anime.status_code == 200 else {"data": []}
    dados_char = res_char.json() if res_char.status_code == 200 else {"data": []}

    # filtro extra: remover animes com classificação adulta/NSFW
    if "data" in dados_anime:
        safe_list = []
        for item in dados_anime["data"]:
            rating = item.get("rating", "").lower() if item.get("rating") else ""
            # ratings que começam com R (R18, Rx, Hentai etc) serão descartados
            if rating.startswith("r") or "hentai" in rating:
                app.logger.debug(f"anime removido por rating: {item.get('title')} ({rating})")
                continue
            safe_list.append(item)
        dados_anime["data"] = safe_list

    # função auxiliar para verificar se um personagem só aparece em animes seguros
    def char_is_sfw(char):
        # consulta detalhes completos para obter lista de animes
        r = requests.get(f"{ENDPOINT_API}/characters/{char['mal_id']}/full")
        if r.status_code != 200:
            return True  # não dá pra verificar, manter
        payload = r.json().get("data", {})
        for entry in payload.get("anime", []):
            anime_id = entry.get("anime", {}).get("mal_id")
            if not anime_id:
                continue
            r2 = requests.get(f"{ENDPOINT_API}/anime/{anime_id}")
            if r2.status_code != 200:
                continue
            rating = r2.json().get("data", {}).get("rating", "").lower()
            if rating.startswith("r") or "hentai" in rating:
                app.logger.debug(f"personagem {char.get('name')} removido porque aparece em anime NSFW (id {anime_id})")
                return False
        return True

    # aplicar filtro nos personagens
    if "data" in dados_char:
        dados_char["data"] = [c for c in dados_char["data"] if char_is_sfw(c)]

    return render_template("resultado.html", anime=dados_anime, personagem=dados_char)


if __name__ == '__main__':
    app.run(debug=True)