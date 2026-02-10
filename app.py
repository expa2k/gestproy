from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import jwt, bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:4200", "http://127.0.0.1:4200"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    from auth.routes import auth_bp
    from usuarios.routes import usuarios_bp
    from proyectos.routes import proyectos_bp
    from roles.routes import roles_bp
    from miembros.routes import miembros_bp
    from stakeholders.routes import stakeholders_bp
    from procesos.routes import procesos_bp
    from subprocesos.routes import subprocesos_bp
    from tecnicas.routes import tecnicas_bp
    from subproceso_tecnicas.routes import subproceso_tecnicas_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(proyectos_bp, url_prefix='/api/proyectos')
    app.register_blueprint(roles_bp, url_prefix='/api/roles')
    app.register_blueprint(miembros_bp, url_prefix='/api/miembros')
    app.register_blueprint(stakeholders_bp, url_prefix='/api/stakeholders')
    app.register_blueprint(procesos_bp, url_prefix='/api/procesos')
    app.register_blueprint(subprocesos_bp, url_prefix='/api/subprocesos')
    app.register_blueprint(tecnicas_bp, url_prefix='/api/tecnicas')
    app.register_blueprint(subproceso_tecnicas_bp, url_prefix='/api/subproceso-tecnicas')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
