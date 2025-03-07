from flask import Flask, jsonify, request
import cloudscraper

app = Flask(__name__)

# Configuración de Proxies (Opcional, si sigue dando 403)
PROXIES = {
    "http": "http://usuario:contraseña@proxy_ip:puerto",
    "https": "http://usuario:contraseña@proxy_ip:puerto",
}

# Función para obtener la info de un anime desde su slug
def obtener_info_anime(slug):
    url = f"https://ww7.series24.org/series/{slug}".strip("/")
    print(f"➡️ Consultando URL: {url}")

    try:
        # Usar CloudScraper para evadir Cloudflare
        scraper = cloudscraper.create_scraper()

        # Headers con Referer falso para evitar bloqueos
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://ww7.series24.org/",
            "Accept-Language": "es-ES,es;q=0.9",
        }

        # Hacer la solicitud con headers y (opcionalmente) proxies
        response = scraper.get(url, headers=headers)  # Si sigue fallando, usa: response = scraper.get(url, headers=headers, proxies=PROXIES)
        print(f"ℹ️ Estado de la respuesta: {response.status_code}")

        if response.status_code == 403:
            print("❌ Bloqueo de Series24 (403 Forbidden)")
            return {"error": "Acceso bloqueado por Series24"}

        # Procesar el HTML con BeautifulSoup
        from bs4 import BeautifulSoup
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
        print(f"🔥 Error inesperado: {e}")
        return {"error": "Fallo en la solicitud"}

# Ruta para obtener info de un anime por su slug desde la URL
@app.route('/api/gnula/anime', methods=['GET'])
def obtener_anime():
    slug = request.args.get('slug')  # Obtener el slug desde la URL
    if not slug:
        return jsonify({"error": "Falta el parámetro 'slug'"})

    datos = obtener_info_anime(slug)
    return jsonify(datos) if datos else jsonify({"error": "Anime no encontrado"}), 404

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    app.run(debug=True, host="0.0.0.0", port=5000)
