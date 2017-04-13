from flask import render_template, flash, redirect, session, url_for, request, g, jsonify

from web import app


@app.route("/")
def index():
    view = 'dashboard'
    return render_template("index.html", view=view)

@app.route("/login")
def login():
    pass
