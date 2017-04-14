from flask_restful import Resource, reqparse

from api import app, api

# parser = reqparse.RequestParser()
# parser.add_argument('variable')
# parser.add_argument('value')


class ApiNodesList(Resource):
    def get(self):
        nodes = []

        return nodes


class ApiNode(Resource):
    def get(self, node_id):
        sensor = {}
        sensor["id"] = 1
        sensor["protocol_version"] = '2.0'
        sensor["sketch_version"] = '0.1'
        sensor["sketch_name"] = 'Temperature'
        sensor["type"] = 17
        sensor["battery_level"] = '80'
        sensor["children"] = []
        return sensor


class ApiSensorsList(Resource):
    def get(self, node_id):
        children = {}
        for i in app.gateway.sensors[node_id].children:
            print(app.gateway.sensors[node_id].children[i].__dict__)
            children[i] = {}
            children[i]["id"] = app.gateway.sensors[node_id].children[i].id
            children[i]["description"] = app.gateway.sensors[node_id].children[i].description
            children[i]["type"] = app.gateway.sensors[node_id].children[i].type
            children[i]["values"] = app.gateway.sensors[node_id].children[i].values
        return children


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
