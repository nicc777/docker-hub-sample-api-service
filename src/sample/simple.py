from flask import Flask
from flask_restful import Resource, Api
from datetime import datetime
import socket

app = Flask(__name__)
api = Api(app)

VERSION = '2.0.0'

class Probes:
    def __init__(self):
        self.readiness = False
        self.liveness = False

    def simulate_db_up(self):
        self.readiness = True

    def simulate_db_down(self):
        self.readiness = False


probes = Probes()
probes.liveness = True
probes.readiness = True

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)


class VersionCheck(Resource):
    def get(self):
        return {
            'version': '{}'.format(VERSION),
            'timestamp': '{}'.format(datetime.now().isoformat()),
            'features': [
                'Readiness can be toggled',
            ],
            'hostname': hostname,
            'ip_address': ip_address,
        }


class Liveness(Resource):
    def get(self):
        status = 410
        if probes.liveness is True:
            status = 200
        return {'Alive': probes.liveness,}, status


class Readiness(Resource):
    def get(self):
        status = 410
        if probes.readiness is True:
            status = 200
        return {'Ready': probes.readiness,}, status


class ToggleReadiness(Resource):
    def get(self):
        probes.readiness = not probes.readiness
        return {'CommandStatus': 'Ok',}


api.add_resource(VersionCheck, '/version')
api.add_resource(Liveness, '/liveness')
api.add_resource(Readiness, '/readiness')
api.add_resource(ToggleReadiness, '/admin/readiness-toggle')


if __name__ == '__main__':
    app.run(debug=True)
