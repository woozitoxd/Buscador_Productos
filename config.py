import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_por_defecto')
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    
    # 1. Intenta leer la URL completa de Render (PostgreSQL)
    # 2. Si no existe, arma la de XAMPP (MySQL) usando las credenciales locales
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Corrección automática para SQLAlchemy 2.0 (postgres -> postgresql)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Configuración para tu XAMPP local
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        host = os.getenv('DB_HOST', 'localhost')
        name = os.getenv('DB_NAME', 'agregador_perfumes')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}/{name}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False