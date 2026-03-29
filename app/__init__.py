from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Inicializamos el objeto SQLAlchemy (sin asignarle la app todavía)
db = SQLAlchemy()

def create_app():
    # Creamos la instancia de Flask
    app = Flask(__name__)
    
    # Le cargamos la configuración que armamos en config.py
    app.config.from_object(Config)
    
    # Inicializamos las extensiones con la app
    db.init_app(app)
    
    # Acá registraremos las rutas (endpoints) más adelante
    with app.app_context():
        # Importamos las rutas y los modelos
        from . import routes
        from . import models # Antes se llamaba db.py, con SQLAlchemy es mejor llamarlo models.py
        
        # Crea las tablas en la base de datos si no existen
        db.create_all()
        
    return app