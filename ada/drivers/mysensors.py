from drivers import Entity

INFO = {'name': "MySensors"}
SETTINGS = {'device': str, 'baudrate': int}
DEFAULT_SETTINGS = {'device': "/dev/ttyUSB0", 'baudrate': 115200}


def setup(ada, settings, driver):
    import mysensors.mysensors as mysensors

    gateway = mysensors.SerialGateway(settings['device'], event_callback=None, persistence=False,
                                      protocol_version="2.0", baud=settings['baudrate'])
    bridge = Bridge(driver.entities, gateway)
    gateway.event_callback = bridge.event
    gateway.start()


class Bridge(object):
    def __init__(self, entities, gateway):
        self.gateway = gateway
        self.entities = entities

    def event(self, message):
        print(message.__dict__)
        if message.type == 1:
            key = (int(message.node_id), int(message.child_id))
            if key not in self.entities.entities:
                entity = MySensorsDeviceEntity(self.gateway, key[0], key[1])
                self.entities.insert_entity(entity)

            entity = self.entities.get_entity(key[0], key[1])[0]
            entity.values[int(message.sub_type)] = message.payload
        elif message.type == 0 and (message.sub_type not in [17,18]):
            key = (int(message.node_id), int(message.child_id))
            if key not in self.entities.entities:
                entity = MySensorsDeviceEntity(self.gateway, key[0], key[1], int(message.sub_type))
                self.entities.insert_entity(entity)
        elif message.type == 3 and message.sub_type == 0:
            entities = self.entities.get_entity(node_id=int(message.node_id))
            for e in entities:
                e.battery_level = message.payload


class MySensorsDeviceEntity(Entity):
    def __init__(self, gateway, node_id, child_id, _type):
        self.gateway = gateway
        self.node_id = node_id
        self.child_id = child_id
        self.type = _type
        self.protocol_version = gateway.sensors[node_id].protocol_version
        self.sketch_name = gateway.sensors[node_id].sketch_name
        self.sketch_version = gateway.sensors[node_id].sketch_version
        self.battery_level = gateway.sensors[node_id].battery_level
        self.values = {}

    def update_value(self, variable, value):
        print("Updating", variable, value)
        print("Values", self.values, type(variable))
        self.values[variable] = value
        self.gateway.set_child_value(self.node_id, self.child_id, variable, value)
        print(self.gateway.sensors[self.node_id].children[self.child_id].values)

    def __repr__(self):
        return "<node_id={} child_id={}>".format(self.node_id, self.child_id)