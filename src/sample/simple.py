from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

VERSION = '1.0.0'

class Probes:
    def __init__(self):
        self.readiness = False
        self.liveness = False

    def simulate_db_up(self):
        self.readiness = True

    def simulate_db_down(self):
        self.readiness = False


probes = Probes()


class VersionCheck(Resource):
    def get(self):
        return {
            'version': '{}'.format(VERSION),
        }


class Liveliness(Resource):
    def get(self):
        return {
            'Alive': probes.liveness,
        }


class Readyness(Resource):
    def get(self):
        return {
            'Ready': probes.readiness,
        }


api.add_resource(VersionCheck, '/version')
api.add_resource(Liveliness, '/livelyness')
api.add_resource(Readyness, '/readyness')


if __name__ == '__main__':
    probes.liveness = True
    probes.simulate_db_up()
    app.run(debug=True)
