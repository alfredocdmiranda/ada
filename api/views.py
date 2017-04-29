from flask_restful import Resource, reqparse, fields, marshal

from api import app, api, auth
from .models import User

parser = reqparse.RequestParser()
parser.add_argument('username', required=True)
parser.add_argument('password', required=True)

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


class ApiNodesList(Resource):
    @auth.jwt_required
    def get(self):
        nodes = MOCK_NODES

        return nodes


class ApiNode(Resource):
    @auth.jwt_required
    def get(self, node_id):
        if node_id == 1:
            node = MOCK_NODES[0]
        else:
            node = MOCK_NODES[1]
        return node


class ApiSensorsList(Resource):
    @auth.jwt_required
    def get(self, node_id):
        if node_id == 1:
            node = MOCK_NODES[0]
        else:
            node = MOCK_NODES[1]

        return node['sensors']


class ApiSensor(Resource):
    @auth.jwt_required
    def get(self, node_id, sensor_id):
        if node_id == 1:
            node = MOCK_NODES[0]
        else:
            node = MOCK_NODES[1]

        if sensor_id == 1:
            sensor = node['sensors'][0]
        else:
            sensor = node['sensors'][1]

        return sensor

    @auth.jwt_required
    def put(self, node_id, sensor_id):
        args = parser.parse_args()
        # print("{};{};1;0;{};{}".format(node_id,sensor_id,args['variable'],args['value']))
        app.gateway.set_child_value(node_id, sensor_id, args['variable'], args['value'])

        return


class ApiSettings(Resource):
    @auth.jwt_required
    def get(self):
        return {'gateway': {"port": "/dev/ttyACM0"}}


class ApiStatus(Resource):
    @auth.jwt_required
    def get(self):
        return {'server': {'temperature': 60, 'disk_usage': 90}}


class ApiAuth(Resource):
    def post(self):
        args = parser.parse_args()
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