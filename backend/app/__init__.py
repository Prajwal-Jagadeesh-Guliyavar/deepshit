from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from celery import Celery
from config import Config

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # Register blueprints
    from app.routes import auth_bp, reports_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    return app

def make_celery(app=None):
    app = app or create_app()
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery