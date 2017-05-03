import os
import threading

import yaml
from OpenSSL import crypto

import web, api, drivers

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE_DB = os.path.join(SCRIPT_PATH, "ada.db")
SETTINGS_FILE = os.path.join(SCRIPT_PATH, "settings.yaml")


class Ada(object):
    def __init__(self):
        self.config = self.load_settings()
        self.modules = []

    @staticmethod
    def load_settings():
        if not os.path.exists(SETTINGS_FILE):
            default_settings = {'influxdb': {'host': '127.0.0.1', 'port': 9999},
                                'sqlite': DEFAULT_SQLITE_DB}
            with open(SETTINGS_FILE, 'w') as f:
                yaml.dump(default_settings, f, default_flow_style=False)

        with open(SETTINGS_FILE) as f:
            text = f.read()

        settings = yaml.load(text)
        settings['root'] = os.path.dirname(os.path.abspath(__file__))

        return settings


class Module(object):
    def __init__(self, name, target, kwargs=None):
        self.name = name
        self.target = target
        self.kwargs = kwargs

    def start(self):
        self.thread = threading.Thread(target=self.target, kwargs=self.kwargs)
        self.thread.start()


def gen_certificate(cert_file, key_file):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 1024)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "  "
        cert.get_subject().ST = " "
        cert.get_subject().L = " "
        cert.get_subject().O = " "
        cert.get_subject().OU = " "
        cert.get_subject().CN = " "
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha1')

        with open(cert_file, "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        with open(key_file, "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))


def create_db():
    api.db.create_all()
    admin_user = api.models.User(name="Admin", email="admin@ada", password="admin12345")
    api.db.session.add(admin_user)
    api.db.session.commit()


def bootstrap(ada):
    cert_file = os.path.join(ada.config['root'], "ada.crt")
    key_file = os.path.join(ada.config['root'], "ada.key")
    if not os.path.exists(ada.config['sqlite']):
        print("Creating Database...")
        create_db()

    if not os.path.exists(cert_file) and not os.path.exists(key_file):
        print("Generating self-signed certificate...")
        gen_certificate(cert_file, key_file)

if __name__ == '__main__':
    ada = Ada()
    bootstrap(ada)
    ada.db = api.db

    context = ('ada.crt', 'ada.key')
    kwargs = {'host': "0.0.0.0", 'port': 5000, 'ssl_context': context, 'threaded': True}
    ada.modules.append(Module("Web", web.app.run, kwargs))
    kwargs = {'host': "0.0.0.0", 'port': 5001, 'ssl_context': context, 'threaded': True}
    ada.modules.append(Module("Api", api.app.run, kwargs))
    d = drivers.DriverLoader(ada)
    d.load_drivers()
    d.start()

    for m in ada.modules:
        m.start()