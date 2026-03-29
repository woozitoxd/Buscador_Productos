import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_por_defecto')
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    
    # Intenta leer la URL de Render (Postgres), si no existe, usa la de XAMPP (MySQL)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False