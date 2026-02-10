# GestProy Backend API

Backend REST API para el sistema de gestion de proyectos GestProy.

## Tecnologias

- Python 3.10+
- Flask 3.0
- mysql-connector-python
- JWT para autenticacion

## Instalacion

```bash
cd gestproy

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python app.py
```

## Configuracion

Editar el archivo `.env`:

```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DATABASE=gestproy
JWT_SECRET_KEY=tu-clave-secreta
```

## Estructura

```
gestproy/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── auth/
├── usuarios/
├── proyectos/
├── roles/
├── miembros/
├── stakeholders/
├── procesos/
├── subprocesos/
├── tecnicas/
└── subproceso_tecnicas/
```

## Endpoints

### Autenticacion
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- GET /api/auth/me

### Proyectos
- GET /api/proyectos
- GET /api/proyectos/<id>
- POST /api/proyectos
- PUT /api/proyectos/<id>
- DELETE /api/proyectos/<id>

Cada modulo sigue el mismo patron CRUD.

## Uso

Todas las rutas (excepto login y registro) requieren:
```
Authorization: Bearer <token>
```
