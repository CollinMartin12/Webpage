import datetime
import dateutil.tz
####### here is all
from flask import Blueprint, render_template
import flask_login


from . import model

bp = Blueprint("main", __name__)


@bp.route("/")
@flask_login.login_required
def index():
    user = model.User(id=1, email="mary@example.com", name="mary", password="dummy", description="")
    posts = [
        model.Post(id=1, user_id=user.id, text="Test post", timestamp=datetime.datetime.now(dateutil.tz.tzlocal())),
        model.Post(id=2, user_id=user.id, text="Another post", timestamp=datetime.datetime.now(dateutil.tz.tzlocal())),
    ]
    return render_template("main/index.html", posts=posts)

