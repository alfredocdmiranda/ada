from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config')
CORS(app)

api = Api(app)
db = SQLAlchemy(app)

from api import views, models
