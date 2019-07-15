"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to controlate life time of data
"""

from time import time, sleep

from enum import Enum, unique
from Misc import singleton

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask.logging import default_handler
from requests import get, post, put

import json
from json import JSONEncoder

from multiprocessing import Process, Value

@unique
class PoolStates(Enum):
    ACTIVE = 0
    QUARANTINE = 1

class Data():
    """ Structure to represent a data to proccess 
        A source like a Cam could send diferent data from same input,
        example: Original, only a person, only a skeleton.
        In that case controller will be like: cams, cams/person, cams/skeleton
    """
    def __init__(self, controller, data):
        self.id = str(time())           # ID of data, the pool itself change this value
        self.controller = controller    # Source of data
        self.born = time()              # Time used to life of data
        self.state = PoolStates.ACTIVE  # State used to life of data
        self.data = data                # Data to analize

    def getJson(self):
        j = {
            'id' : self.id,
            'controller' : self.controller,
            'born' : self.born,
            'data' : self.data
        }
        return j


@singleton
class DataPool(Resource):
    """ Class to controlate life time of data """
    def __init__(self):
        """ Start class variables """
        self.URL = ""

        self.pool = []          # Store of data
        self.countData = 0      # Amount of data received

        self.T0 = 10            # Seconds to keep data in active
        self.T1 = self.T0 + 10  # Seconds to keep data in quarentine

    def append(self, data:Data):
        """ Add new data to the pool """
        data.id += '-' + str(len(self.pool))
        self.countData += 1
        self.pool.append(data)

    def pop(self):
        """ Move data if life time is over """
        for p in self.pool:
            if time() - p.born > self.T1:
                self.pool.remove(p)
            elif time() - p.born > self.T0:
                p.state = PoolStates.QUARANTINE

    def get(self, controller=''):
        """ Return all active data """
        #TODO: Recibir momento de consulta para traer solo los más recientes a ese momento
        result = []
        if controller != '':
            result = list(filter(lambda d: d.state == PoolStates.ACTIVE, self.pool))
        else:
            result = self.pool
        
        result = list(map(lambda d: d.getJson(), self.pool))
        return result

    def post(self):
        """ Load data in pool """
        parser = reqparse.RequestParser()
        parser.add_argument('controller')
        parser.add_argument('data')
        args = parser.parse_args()
        data = Data(args.controller, args.data)
        message = 'ok'
        self.append(data)
        return message

    def put(self):
        """ Exec commands on pool """
        parser = reqparse.RequestParser()
        parser.add_argument('command')
        args = parser.parse_args()
        message = ''
        if args.command == 'isLive':
            message = True
        elif args.command == 'pop':
            self.pop()
            message = 'ok'
        elif args.command == 'count':
            message = len(self.pool)
        else:
            message = 'Bad command name'

        return message

    def start(self):
        print('Starting pool api in ' + self.URL)
        """ Start api for data pool """
        app = Flask(__name__)            
        #TODO: Write log in a file
        """
        handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.removeHandler(default_handler)
        """
        api = Api(app)
        api.add_resource(DataPool, 
            '/pool',
            '/pool/<string:controller>', 
            methods=['get', 'post', 'put'])        
        #'/pool/<string:har>/<string:class>/<string:id>', 

        app.run()

    def sendCommand(self, command):
        """ Function generic to send commands to pool """
        x = put(self.URL, data={'command': command}).json()
        return x

    def isLive(self):
        """ Shows if pool is living """
        x = self.sendCommand('isLive')
        return bool(x)
        #TODO: put a timer to controller timeout to means no live

    def count(self):
        """ Returns the size of pool """
        x = self.sendCommand('count')
        return int(x)

    def sendData(self, controller, data):
        """ Send data to pool """
        p = post(self.URL, data={'controller' : controller, 'data': data})
        return p
