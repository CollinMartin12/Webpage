from microblog import create_app
from microblog.model import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Tables created successfully!")