import re
import os
import glob
import json
import importlib

from api.models import *


class Driver(object):
    def __init__(self, ada, _module, settings):
        self.ada = ada
        self._module = _module
        self.settings = settings
        self.entities = Entities()

    def setup(self):
        self._module.setup(self.ada, self.settings, self)

    def get_entities(self, node_id="", child_id=""):
        entities = self.entities.get_entity(node_id=node_id, child_id=child_id)

        return entities


class DriverLoader(object):
    def __init__(self, ada):
        self.ada = ada
        self.drivers = {}

    def load_drivers(self):
        drivers_path = os.path.dirname(os.path.abspath(__file__))
        drivers = glob.glob(os.path.join(drivers_path,"*.py"))
        for driver in drivers:
            _module = driver.split("/")[-1].split(".")[0]
            if _module != "__init__":
                loaded_module = importlib.import_module("." + _module, package="drivers")
                r = Settings.query.filter(Module.name==_module).first()
                if not r:
                    m = Module(name=_module, active=True)
                    self.ada.db.session.add(m)
                    s = Settings(settings=json.dumps(loaded_module.DEFAULT_SETTINGS), module=m)
                    self.ada.db.session.add(s)
                    self.ada.db.session.commit()
                    r = s
                settings = json.loads(r.settings)
                self.drivers[_module] = Driver(self.ada, loaded_module, settings)

    def start(self):
        for d in self.drivers:
            self.drivers[d].setup()

    def get_entities(self, module="", node_id="", child_id=""):
        if not module:
            entities = []
            for driver in self.drivers:
                entities += self.drivers[driver].get_entities(node_id=node_id, child_id=child_id)
        else:
            entities = self.drivers[module].get_entities(node_id=node_id, child_id=child_id)

        return entities


class Entities(object):
    def __init__(self):
        self.entities = {}

    def get_entity(self, node_id="", child_id=""):
        entities = []
        if node_id != "":
            if child_id == "":
                for k in self.entities:
                    if k[0] == node_id:
                        entities.append(self.entities[k])
            else:
                for k in self.entities:
                    if k[0] == node_id and k[1] == child_id:
                        entities.append(self.entities[k])
        else:
            for k in self.entities:
                entities.append(self.entities[k])

        return entities

    def insert_entity(self, entity):
        key = (entity.node_id, entity.child_id)
        self.entities[key] = entity

        return True


class Entity(object):
    pass