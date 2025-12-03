from flask import Flask
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Declarations to insert before the create_app function:
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)


def create_app(test_config=None):
    app = Flask(__name__)

    # A secret for signing session cookies
    app.config["SECRET_KEY"] = "93220d9b340cf9a6c39bac99cce7daf220167498f91fa"
    
    # Database configuration - use environment variables for Docker
    db_host = os.getenv('DB_HOST', 'mysql.lab.it.uc3m.es')
    db_port = os.getenv('DB_PORT', '3307')
    db_user = os.getenv('DB_USER', 'microblog_user')
    db_password = os.getenv('DB_PASSWORD', 'microblog_password')
    db_name = os.getenv('DB_NAME', 'microblog_db')
    
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # Register blueprints
    # (we import main from here to avoid circular imports in the next lab)
    from . import main
    from . import auth
    from . import model

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(model.User, int(user_id))
    
    return app
