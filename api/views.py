from flask_restful import Resource, reqparse

from api import app, api

# parser = reqparse.RequestParser()
# parser.add_argument('variable')
# parser.add_argument('value')


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
    def get(self):
        nodes = MOCK_NODES

        return nodes


class ApiNode(Resource):
    def get(self, node_id):
        if node_id == 1:
            node = MOCK_NODES[0]
        else:
            node = MOCK_NODES[1]
        return node


class ApiSensorsList(Resource):
    def get(self, node_id):
        if node_id == 1:
            node = MOCK_NODES[0]
        else:
            node = MOCK_NODES[1]

        # children = []
        # for i in node['children']:
        #     # print(app.gateway.sensors[node_id].children[i].__dict__)
        #     children.append({})
        #     children[-1]["id"] = app.gateway.sensors[node_id].children[i].id
        #     children[-1]["description"] = app.gateway.sensors[node_id].children[i].description
        #     children[-1]["type"] = app.gateway.sensors[node_id].children[i].type
        #     children[-1]["values"] = app.gateway.sensors[node_id].children[i].values

        return node['children']


class ApiSensor(Resource):
    def get(self, node_id, sensor_id):
        return {'type': 3}

    def put(self, node_id, sensor_id):
        args = parser.parse_args()
        # print("{};{};1;0;{};{}".format(node_id,sensor_id,args['variable'],args['value']))
        app.gateway.set_child_value(node_id, sensor_id, args['variable'], args['value'])

        return


class ApiSettings(Resource):
    def get(self):
        return {'gateway': {"port": "/dev/ttyACM0"}}


class ApiStatus(Resource):
    def get(self):
        return {'server': {'temperature': 60, 'disk_usage': 90}}


api.add_resource(ApiNodesList, '/nodes')
api.add_resource(ApiNode, '/nodes/<int:node_id>')
api.add_resource(ApiSensorsList, '/nodes/<int:node_id>/sensors')
api.add_resource(ApiSensor, '/nodes/<int:node_id>/sensors/<int:sensor_id>')
api.add_resource(ApiSettings, '/settings')
api.add_resource(ApiStatus, '/status')
