import os

import click
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from app.config import Config
from app.extensions import db, jwt

load_dotenv()

DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'docs')
)
SWAGGER_URL = '/docs'
OPENAPI_URL = '/openapi.yaml'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    from app.routes.appointments import appointments_bp
    from app.routes.auth import auth_bp
    from app.routes.clients import clients_bp
    from app.routes.health import health_bp
    from app.routes.pets import pets_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(pets_bp)
    app.register_blueprint(appointments_bp)

    @app.route(OPENAPI_URL)
    def openapi_spec():
        return send_from_directory(DOCS_DIR, 'openapi.yaml', mimetype='text/yaml')

    swagger_ui_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        OPENAPI_URL,
        config={'app_name': 'Sistema de Control Veterinario API'},
    )
    app.register_blueprint(swagger_ui_bp, url_prefix=SWAGGER_URL)

    with app.app_context():
        db.create_all()

    register_cli(app)

    return app


def register_cli(app):
    @app.cli.command('create-admin')
    @click.option('--name', prompt=True)
    @click.option('--email', prompt=True)
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(name, email, password):
        """Crea un usuario con rol admin."""
        from app.models.user import User

        email = email.strip().lower()
        if User.query.filter_by(email=email).first():
            click.echo(f'Ya existe un usuario con el email {email}')
            return

        user = User(name=name, email=email, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin "{email}" creado correctamente.')
