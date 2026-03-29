from flask import current_app as app, request, jsonify, render_template
import requests
from .models import HistorialBusqueda
from . import db
import re
from bs4 import BeautifulSoup

# --- 1. FUNCIÓN DE EXTRACCIÓN (REGEX) ---
def extraer_precio_regex(texto):
    if not texto: return None
    patron = r'\$\s?(\d{1,3}(\.\d{3})*(,\d+)?|\d+)'
    resultado = re.search(patron, texto)
    return resultado.group(0) if resultado else None

# --- 2. DEEP SCRAPING GENÉRICO ---
def obtener_precio_deep(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code != 200: return None
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Estrategia Meta: Buscar en etiquetas de SEO
        meta = soup.find("meta", property="product:price:amount") or soup.find("meta", itemprop="price")
        if meta and meta.get("content"):
            return f"$ {meta.get('content')}"

        # Estrategia Heurística: Buscar clases con 'price' o 'precio'
        tags = soup.find_all(class_=re.compile(r'price|precio|vtex-product-price', re.I))
        for t in tags:
            p = extraer_precio_regex(t.get_text())
            if p: return p
        return None
    except:
        return None

# --- 3. RUTA DE LA INTERFAZ (Única función 'inicio') ---
@app.route('/')
def inicio(): # Le cambié el nombre a 'inicio' para evitar el AssertionError
    return render_template('index.html')

# --- 4. RUTA DE LA API (Única función 'buscar') ---
@app.route('/api/buscar', methods=['GET'])
def buscar(): # Le cambié el nombre a 'buscar'
    query = request.args.get('q')
    modo = request.args.get('modo', 'general')
    
    if not query:
        return jsonify({"error": "Ingresa un perfume"}), 400

    # DB Log
    try:
        db.session.add(HistorialBusqueda(termino=query))
        db.session.commit()
    except:
        db.session.rollback()

    # SerpApi
    api_key = app.config.get('SERPAPI_KEY')
    url_serp = "https://serpapi.com/search"
    # Query optimizada para Argentina
    q_final = f'"{query}" perfume Argentina (site:.com.ar OR "tienda oficial")'
    
    params = {"engine": "google", "q": q_final, "gl": "ar", "hl": "es", "api_key": api_key}
    
    try:
        res = requests.get(url_serp, params=params)
        items = res.json().get('organic_results', [])
    except:
        return jsonify({"error": "Error de conexión"}), 500

    resultados = []
    for item in items:
        link = item.get('link')
        # Intentamos snippet primero
        precio = extraer_precio_regex(item.get('snippet', ''))
        
        # Deep Scraping si es necesario
        if modo == 'precios' and not precio:
            precio = obtener_precio_deep(link)

        # Si en modo precios no hay nada tras el deep scraping, mostramos un aviso 
        # para no "borrar" el resultado, pero que el usuario sepa qué pasa
        if modo == 'precios' and not precio:
            precio = "Ver precio en sitio"

        resultados.append({
            "titulo": item.get('title'),
            "link": link,
            "descripcion": item.get('snippet'),
            "precio": precio
        })

    # Ordenar por precio si corresponde
    if modo == 'precios':
        def val(x):
            nums = re.sub(r'[^\d]', '', x['precio'])
            return int(nums) if nums else 999999999
        resultados.sort(key=val)

    return jsonify({"resultados": resultados})