from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Función para obtener la info de un anime desde su slug
def obtener_info_anime(slug):
    url = f"https://ww7.series24.org/series/{slug}/"
    print(f"Consultando URL: {url}")  # Verificar la URL generada
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers)
        print(f"Estado de la respuesta: {response.status_code}")  # Verificar si la página responde
        
        if response.status_code != 200:
            return None

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

    except Exception as e:
        print(f"Error al obtener el anime: {e}")
        return None

# Ruta para obtener info de un anime por su slug desde la URL
@app.route('/api/gnula/anime', methods=['GET'])
def obtener_anime():
    slug = request.args.get('slug')  # Obtener el slug desde la URL
    if not slug:
        return jsonify({"error": "Falta el parámetro 'slug'"}), 400

    datos = obtener_info_anime(slug)
    if datos:
        return jsonify(datos)
    else:
        return jsonify({"error": "Anime no encontrado"}), 404

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    app.run(debug=True, host="0.0.0.0", port=5000)
