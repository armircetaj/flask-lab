import click
from flask import Flask
from config import Config
from extensions import db, migrate, login_manager
from models import User
from blueprints.auth import app as bp_auth
from blueprints.frontend import app as bp_frontend
from blueprints.api import app as bp_api

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_frontend)
    app.register_blueprint(bp_api, url_prefix='/api')

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('password')
    def create_admin(username, password):
        if User.query.filter_by(username=username).first():
            print(f'User {username} already exists')
            return
        user = User(username=username, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f'Admin {username} created')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
