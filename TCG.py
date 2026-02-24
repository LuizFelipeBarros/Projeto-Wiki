from flask import Flask, render_template, flash, redirect
import random
import os
from tcgdexsdk import TCGdex, Query # Importa o SDK

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')

# Inicializa o SDK (pt para português)
tgc = TCGdex("pt")

@app.route('/')
def index():
    meus_boosters = [
        {"id": "swsh10", "name": "Astral Radiance (Palkia/Dialga)"},
        {"id": "swsh11", "name": "Lost Origin (Giratina)"},
        {"id": "swsh9", "name": "Brilliant Stars (Arceus/Charizard)"},
        {"id": "sv3", "name": "Obsidian Flames (Charizard ex)"},
        {"id": "swsh4", "name": "Vivid Voltage (Pikachu VMAX)"}
    ]
    return render_template('index.html', colecoes=meus_boosters)

@app.route('/abrir/<set_id>')
def abrir(set_id):
    try:
        # A forma correta de filtrar por set no SDK:
        query = Query().equal("set", set_id)
        cartas = tgc.card.listSync(query)

        if not cartas:
            flash("Nenhuma carta encontrada!")
            return redirect('/')

        pacotinho = random.sample(cartas, min(6, len(cartas)))
        return render_template('booster.html', cartas=pacotinho)

    except Exception as e:
        print(f"ERRO SDK: {e}")
        flash(f"Erro técnico: {e}")
        return redirect('/')

    except Exception as e:
        print(f"ERRO SDK: {e}")
        flash("Erro ao carregar o booster. Tente novamente!")
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
