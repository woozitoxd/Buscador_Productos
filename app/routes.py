from flask import current_app as app, request, jsonify, render_template
import requests
from .models import HistorialBusqueda
from . import db

# --- RUTA DE LA INTERFAZ WEB ---
@app.route('/')
def home():
    # Esta ruta ahora devuelve el archivo HTML visual
    return render_template('index.html')

# --- RUTA DE LA API (JSON para Postman o el Frontend) ---
@app.route('/api/buscar', methods=['GET'])
def buscar_perfume():
    query = request.args.get('q')
    
    if not query:
        return jsonify({"error": "Por favor, ingresa un perfume a buscar usando el parámetro ?q="}), 400

    # Guardamos en la base de datos
    try:
        nueva_busqueda = HistorialBusqueda(termino=query)
        db.session.add(nueva_busqueda)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar en BD: {e}")

    api_key = app.config.get('SERPAPI_KEY')
    if not api_key:
        return jsonify({"error": "Falta configurar la SERPAPI_KEY en el .env"}), 500

    url = "https://serpapi.com/search"
    termino_busqueda = f"{query} site:juleriaque.com.ar OR site:parfumerie.com.ar OR site:rouge.com.ar"
    
    parametros = {
        "engine": "google",
        "q": termino_busqueda,
        "gl": "ar", 
        "hl": "es", 
        "api_key": api_key
    }

    try:
        respuesta = requests.get(url, params=parametros)
        
        if respuesta.status_code != 200:
            return jsonify({
                "error": f"SerpApi rechazó la petición (Código {respuesta.status_code})",
                "detalle": respuesta.json()
            }), respuesta.status_code
            
        datos_google = respuesta.json()
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Fallo crítico en la red", "detalle": str(e)}), 500

    resultados_limpios = []
    items = datos_google.get('organic_results', [])
    
    for item in items:
        resultado = {
            "titulo": item.get('title'),
            "link": item.get('link'),
            "descripcion": item.get('snippet')
        }
        resultados_limpios.append(resultado)

    return jsonify({
        "busqueda": query,
        "cantidad_resultados": len(resultados_limpios),
        "resultados": resultados_limpios
    })