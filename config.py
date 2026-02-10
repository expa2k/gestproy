import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Ruben2004')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'gestproy')
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'tu-clave-secreta-cambiar-en-produccion')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
