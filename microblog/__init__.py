from flask import Flask


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
    
    # Code to place inside create_app, after the other app.config assignment
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "mysql+pymysql://26_webapp_29:mx4ZAdkY@mysql.lab.it.uc3m.es/26_webapp_29a"

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
