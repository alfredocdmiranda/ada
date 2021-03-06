import json

from flask_restful import Resource, reqparse, fields, marshal

from api import app, api, auth, db
from .models import User, Settings, Module

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', required=True)
login_parser.add_argument('password', required=True)

settings_post_parser = reqparse.RequestParser()
settings_post_parser.add_argument('module', required=True, type=str)
settings_post_parser.add_argument('settings', required=True, type=dict)

sensor_put_parser = reqparse.RequestParser()
sensor_put_parser.add_argument('variable', required=True, type=int)
sensor_put_parser.add_argument('value', required=True, type=float)

user_fields = {"id": fields.Integer, "name": fields.String, "email": fields.String}

MOCK_NODES = [{"id": 1,
                  "protocol_version": 2.0,
                  "sketch_version": 0.1,
                  "sketch_name": "Mock Data 1",
                  "type": 17,
                  "battery_level": 100,
                  "sensors": [{"id": 1,
                               "description": "Temperature",
                               "values": [35.0],
                               "type": 6},
                              {"id": 2,
                               "description": "Light",
                               "values": [1, 6],
                               "type": 3}]
                  },
                 {"id": 2,
                  "protocol_version": 2.0,
                  "sketch_version": 0.1,
                  "sketch_name": "Mock Data 2",
                  "type": 17,
                  "battery_level": 12,
                  "sensors": [{"id": 1,
                               "description": "Temperature",
                               "values": [22.0],
                               "type": 6},
                              {"id": 2,
                               "description": "Light",
                               "values": [1, 6],
                               "type": 3}]
                  }]


def jsonify_nodes(entities):
    nodes = {}
    for e in entities:
        if e.node_id not in nodes:
            nodes[e.node_id] = {}
            nodes[e.node_id]['id'] = e.node_id
            nodes[e.node_id]['battery_level'] = e.battery_level
            nodes[e.node_id]['sketch_name'] = e.sketch_name
            nodes[e.node_id]['sketch_version'] = e.sketch_version
            nodes[e.node_id]['protocol_version'] = e.protocol_version
            nodes[e.node_id]['type'] = 17
            nodes[e.node_id]['sensors'] = {}

        nodes[e.node_id]['sensors'][e.child_id] = {
            "id": e.child_id,
            "description": "",
            "type": e.type,
            "values": {}
        }

        for v in e.values:
            nodes[e.node_id]['sensors'][e.child_id]['values'][v] = e.values[v]

    return list(nodes.values())


class ApiNodesList(Resource):
    @auth.jwt_required
    def get(self):
        e = app.ada.loader.get_entities(module='mysensors')
        nodes = jsonify_nodes(e)

        return nodes


class ApiNode(Resource):
    @auth.jwt_required
    def get(self, node_id):
        e = app.ada.loader.get_entities(module='mysensors', node_id=node_id)
        if e:
            node = jsonify_nodes(e)[0]
        else:
            node = {}

        return node


class ApiSensorsList(Resource):
    @auth.jwt_required
    def get(self, node_id):
        e = app.ada.loader.get_entities(module='mysensors', node_id=node_id)
        if e:
            sensors = jsonify_nodes(e)[0]['sensors']
        else:
            sensors = {}

        return sensors


class ApiSensor(Resource):
    @auth.jwt_required
    def get(self, node_id, sensor_id):
        e = app.ada.loader.get_entities(module='mysensors', node_id=node_id, child_id=sensor_id)
        if e:
            sensor = jsonify_nodes(e)[0]['sensors'][sensor_id]
        else:
            sensor = {}

        return sensor

    @auth.jwt_required
    def put(self, node_id, sensor_id):
        args = sensor_put_parser.parse_args()
        e = app.ada.loader.get_entities(module='mysensors', node_id=node_id, child_id=sensor_id)
        if e:
            entity = e[0]
            entity.update_value(args['variable'], args['value'])

        return {}


class ApiSettings(Resource):
    @auth.jwt_required
    def get(self):
        list_settings = Settings.query.all()
        list_settings = {s.module.name: json.loads(s.settings) for s in list_settings}
        return list_settings

    @auth.jwt_required
    def put(self):
        args = settings_post_parser.parse_args()
        settings = Settings.query.filter(Module.name == args['module']).first()
        settings.settings = json.dumps(args['settings'])
        db.session.add(settings)
        db.session.commit()


class ApiStatus(Resource):
    @auth.jwt_required
    def get(self):
        data = app.ada.sys_monitor
        system = {'server': {'temperature': data.temperature.current, 'disk_usage': data.disk_usage,
                             'platform': data.sys_info.system, 'arch': data.sys_info.machine, 'release': data.sys_info.release},
                  'ada': {'version': "0.1.0"}}

        return system


class ApiAuth(Resource):
    def post(self):
        args = login_parser.parse_args()
        user = User.query.filter(User.email==args.username).first()
        if user and args.password == user.password:
            auth_token = auth.encode_auth_token(user.id)
            return {'auth_token': auth_token.decode('utf-8')}
        else:
            return {'message': "Unauthorized"}, 401


class ApiUserMe(Resource):
    @auth.jwt_required
    def get(self):
        user = User.query.filter(User.id == payload).first()
        return marshal(user, user_fields)

api.add_resource(ApiNodesList, '/nodes')
api.add_resource(ApiNode, '/nodes/<int:node_id>')
api.add_resource(ApiSensorsList, '/nodes/<int:node_id>/sensors')
api.add_resource(ApiSensor, '/nodes/<int:node_id>/sensors/<int:sensor_id>')
api.add_resource(ApiSettings, '/settings')
api.add_resource(ApiStatus, '/status')
api.add_resource(ApiAuth, '/auth')
api.add_resource(ApiUserMe, '/users/me')