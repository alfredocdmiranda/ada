import influxdb
import influxalchemy

from api import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(64))


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship("Module", back_populates="settings")
    settings = db.Column(db.String)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    settings = db.relationship("Settings", uselist=False, back_populates="module")
    active = db.Column(db.Boolean)


class Sensors(influxalchemy.Measurement):
    __measurement__ = 'sensors'