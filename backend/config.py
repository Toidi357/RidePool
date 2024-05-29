from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os

# from flask_lt import run_with_lt


app = Flask(__name__)

# run_with_lt(app, "ridepool-35l")
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db" # where to store:///nameofdb.db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app) 
bcrypt = Bcrypt(app)


app.config['SECRET_KEY'] = os.urandom(24)

app.app_context().push()
