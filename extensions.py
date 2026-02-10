import mysql.connector
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from config import Config

jwt = JWTManager()
bcrypt = Bcrypt()

def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
