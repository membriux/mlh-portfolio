import os
from flask import Flask, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .backgrounds import get_random_background
from .profileInfo import get_profile_data


app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}".format(
    user=os.getenv("POSTGRES_USER"),
    passwd=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=5432,
    table=os.getenv("POSTGRES_DB"),
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class UserModel(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"


@app.route("/")
def index():
    homeData = get_profile_data("data/home.json")
    return render_template(
        "index.html",
        title="MLH Fellow",
        url=os.getenv("URL"),
        random_background=get_random_background(),
        homeData=homeData,
    )


@app.route("/<profile>")
def profile(profile):
    file = "data/{profile}.json".format(profile=profile)
    profile_data = get_profile_data(file)
    return render_template("profile.html", profile_data=profile_data)


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            return "Login Successful", 200
        else:
            return error, 418

    # TODO: Return a login page
    return render_template("login.html", action_type="login"), 200


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif UserModel.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        if error is None:
            new_user = UserModel(username, generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    # TODO: Return a restister page
    return render_template("login.html", action_type="register"), 200

@app.route("/health")
def health():
    return "Working!"


@app.route("/wflow")
def workflow():
    return "Workflow deployment worked!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
