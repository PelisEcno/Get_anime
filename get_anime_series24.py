from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Función para obtener la info de un anime desde su slug
def obtener_info_anime(slug):
    url = f"https://ww7.series24.org/series/{slug}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None  # Si la página no existe, devuelve None

    soup = BeautifulSoup(response.text, "html.parser")

    # Obtener título
    titulo_tag = soup.select_one("h1.h1.ttl")
    titulo = titulo_tag.text.strip() if titulo_tag else "No encontrado"

    # Obtener sinopsis
    sinopsis_tag = soup.find("div", class_="summary")
    sinopsis = sinopsis_tag.find("p").text.strip() if sinopsis_tag else "No encontrada"

    # Obtener imagen
    imagen_tag = soup.find("div", class_="title-img")
    imagen = imagen_tag.find("img")["src"] if imagen_tag else "No encontrada"

    # Obtener episodios
    episodios = []
    for cap in soup.select(".episodes .episode"):
        nombre_tag = cap.find("span", class_="fwb link-co")
        enlace_tag = cap.find("a")

        nombre = nombre_tag.text.strip() if nombre_tag else "Sin nombre"
        enlace = enlace_tag["href"] if enlace_tag else "Sin enlace"

        episodios.append({"nombre": nombre, "enlace": enlace})

    return {"titulo": titulo, "sinopsis": sinopsis, "imagen": imagen, "episodios": episodios}

# Ruta para obtener info de un anime por su slug
@app.route('/api/gnula/anime/<slug>', methods=['GET'])
def obtener_anime(slug):
    datos = obtener_info_anime(slug)
    if datos:
        return jsonify(datos)
    else:
        return jsonify({"error": "Anime no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)