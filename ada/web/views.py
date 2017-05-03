import requests
from flask import render_template, flash, redirect, url_for, g, request
from flask_login import login_user, logout_user, current_user, login_required, UserMixin

from web import app, forms, login_manager


class User(UserMixin):
    def __init__(self, _id, name, email, token):
        self.id = _id
        self.name = name
        self.email = email
        self.token = token

    def get_id(self):
        return str(self.token)


@login_manager.user_loader
def load_user(token):
    url = "https://localhost:5001/users/me"
    headers = {"Authentication": "JWT "+token}
    r = requests.get(url, verify=False, headers=headers)
    if r.status_code == 401:
        return None
    user = User(r.json().get("id"), r.json().get("name"), r.json().get("email"), token)

    return user


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('login')


@app.before_request
def before_request():
    g.user = current_user


def get_api_request(url):
    headers = {"Authentication": "JWT " + g.user.token}
    r = requests.get(url, verify=False, headers=headers)

    return r.json()


def put_api_request(url, data):
    headers = {"Authentication": "JWT " + g.user.token}
    r = requests.put(url, verify=False, headers=headers, json=data)

    return r.json()


@app.route("/", methods=['GET'])
@login_required
def index():
    url = "https://localhost:5001/nodes"
    resp = get_api_request(url)
    view = 'dashboard'
    return render_template("index.html", view=view, nodes=resp)


@app.route("/nodes", methods=['GET'])
@login_required
def nodes():
    url = "https://localhost:5001/nodes"
    resp = get_api_request(url)
    view = 'nodes'
    return render_template("nodes.html", view=view, nodes=resp)


@app.route("/settings", methods=['GET'])
@login_required
def settings():
    url = "https://localhost:5001/settings"
    resp = get_api_request(url)
    view = 'settings'
    return render_template("settings.html", view=view, settings=resp)


@app.route("/settings/<_module>", methods=['POST'])
@login_required
def settings_update(_module):
    data = {'module': _module, 'settings': {}}
    for f in request.form:
        if not f == 'csrf_token':
            data['settings'][f] = request.form[f]
    url = "https://localhost:5001/settings"
    resp = put_api_request(url, data)
    return redirect('/settings')


@app.route("/status", methods=['GET'])
@login_required
def status():
    view = 'status'
    return render_template("status.html", view=view)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        url = "https://localhost:5001/auth"
        login = {'username': form.email.data, 'password': form.passwd.data}
        r = requests.post(url, verify=False, data=login)
        if r.status_code == 200:
            auth_token = r.json().get('auth_token')
            url = "https://localhost:5001/users/me"
            headers = {"Authentication": "JWT " + auth_token}
            r = requests.get(url, verify=False, headers=headers)
            user = User(r.json().get("id"), r.json().get("name"), r.json().get("email"), auth_token)
            login_user(user, remember=form.remember_me.data)

            return redirect(url_for('index'))
        elif r.status_code == 401:
            flash("Invalid username or password")

    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))