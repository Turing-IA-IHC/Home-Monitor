"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to controlate life time of data
"""

import sys
import logging
from time import time

import Misc
from Misc import singleton
from enum import Enum, unique

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from requests import get, post, put

import json
from json import JSONEncoder
import pickle
import ast

import re

from multiprocessing import Process, Value

@unique
class PoolStates(Enum):
    ACTIVE = 0
    QUARANTINE = 1

@unique
class SourceType(Enum):
    CONTROLLER = 0
    CLASSIFIER = 1
    @staticmethod
    def parse(T:str):
        if 'SourceType.CONTROLLER' == str(T) or 'CONTROLLER' == str(T).upper() or str(SourceType.CONTROLLER) == str(T):
            return SourceType.CONTROLLER
        elif 'SourceType.CLASSIFIER' == str(T) or 'CLASSIFIER' == str(T).upper() or str(SourceType.CLASSIFIER) == str(T):
            return SourceType.CLASSIFIER
        else:
            return None

class Data():
    """ Structure to represent a data to proccess 
        A source like a Cam could send diferent data from same input,
        example: Original, only a person, only a skeleton.
        In that case controller will be like: cams, cams/person, cams/skeleton
    """
    
    id = str(time())           # ID of data, the pool itself change this value
    source:SourceType = None   # Module type generator of data
    born = time()              # Time used to life of data
    state = PoolStates.ACTIVE  # State used to life of data
    controller = ''            # Source of data
    device = ''                # Physical device identifier
    classifier = ''            # Source of data
    data = None                # Data to analize
    aux = None                 # Auxiliar data

    def getJson(self):
        j = {
            'id' : self.id,
            'controller' : self.controller,
            'device' : self.device,
            'born' : self.born,
            'data' : self.data,
            'aux': self.aux,
        }
        return j

@singleton
class DataPool(Resource):
    """ Class to controlate life time of data """
    def __init__(self):
        """ Start class variables """
        self.URL = ""               # URL to start Pool
        self.TimeDiff = 0           # Defference between pool server and local time

        self.pool = []              # Store of data
        self.countData = 0          # Amount of data received

        self.T0 = 10                # Seconds to keep data in active
        self.T1 = self.T0 + 10      # Seconds to keep data in quarentine
        
        self.loggingLevel:int = 0   # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log

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

    def get(self):
        """ Return all active data:
        Controller and device coulbe Exp Reg.
        Ex. 'CamController' for single or 'CamController.*?' for all from CamController """
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        parser.add_argument('source')
        parser.add_argument('controller')
        parser.add_argument('device')
        parser.add_argument('classifier')
        parser.add_argument('limit')
        parser.add_argument('lastTime')
        args = parser.parse_args()
        
        id = args.id
        source = args.source
        controller = args.controller
        device = args.device
        classifier = args.classifier
        limit = int(args.limit)
        lastTime = float(args.lastTime)

        id = '' if id == None else id
        source = '' if source == None else source
        controller = '' if controller == None else controller
        device = '' if device == None else device
        classifier = '' if classifier == None else classifier
        limit = -1 if limit == None else limit
        lastTime = 0 if lastTime == None else lastTime

        result = self.pool[:]
                
        if id != '':
            idRE = re.compile('^' + id + '$')
            result = list(filter(lambda d: idRE.match(d.id) != None, result))
        
        if device != '':
            deviceRE = re.compile('^' + device + '$')
            result = list(filter(lambda d: deviceRE.match(d.device) != None, result))
        
        if controller != '':
            controllerRE = re.compile('^' + controller + '$')
            result = list(filter(lambda d: controllerRE.match(d.controller) != None, result))
            
        if classifier != '':
            classifierRE = re.compile('^' + classifier + '$')
            result = list(filter(lambda d: classifierRE.match(d.classifier) != None, result))
        
        if source != '':
            result = list(filter(lambda d: SourceType.parse(d.source) == SourceType.parse(source), result))
            
        if lastTime > 0:
            result = list(filter(lambda d: d.born >= lastTime, result))
        
        if limit > -1:
            result = result[-limit:]
        
        result = list(filter(lambda d: d.state == PoolStates.ACTIVE, result))
        result = list(map(lambda d: d.getJson(), result))
        result.insert(0, {'timeQuery' : time()})

        return result

    def post(self):
        """ Load data in pool """
        try:             
            parser = reqparse.RequestParser()
            parser.add_argument('id')
            parser.add_argument('source')
            parser.add_argument('controller')
            parser.add_argument('device')
            parser.add_argument('classifier')
            parser.add_argument('data')
            parser.add_argument('aux')
            args = parser.parse_args()

            data = Data()
            
            if SourceType.parse(args.source) == SourceType.CONTROLLER:
                data.source = SourceType.CONTROLLER
                data.controller = args.controller
                data.device = args.device
            elif SourceType.parse(args.source) == SourceType.CLASSIFIER:
                data.id = args.id
                data.source = SourceType.CLASSIFIER
                data.classifier = args.classifier
                pass
            
            data.id = str(time()) 
            data.data = args.data
            data.aux = args.aux
            data.born = time()
            self.append(data)
            self.pop()

            message = 'ok'
        
        except:
            logging.exception('Unexpected writting data in pool. :: Err: {}.'.format(str(sys.exc_info()[0])))
            message = 'Unexpected writting data in pool. :: Err: {}.'.format(str(sys.exc_info()[0]))

        return message

    def put(self):
        """ Exec commands on pool """
        parser = reqparse.RequestParser()
        parser.add_argument('command')
        args = parser.parse_args()
        message = ''
        if args.command == 'time':
            message = time()
        elif args.command == 'isLive':
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
        """ Start api for data pool """

        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)

        app = Flask(__name__)
        log = logging.getLogger('werkzeug')
        log.setLevel(self.loggingLevel + 10)
        app.logger = logging.getLogger()
        api = Api(app)
        api.add_resource(DataPool, 
            '/pool',
            '/pool/<string:controller>', 
            methods=['get', 'post', 'put'])        
        #'/pool/<string:har>/<string:class>/<string:id>', 

        app.run()
        logging.info('Pool api stoped.')

    """ Functions to interact with Pool """

    def sendCommand(self, command):
        """ Function generic to send commands to pool """
        x = put(self.URL, data={'command': command}).json()
        return x

    def getTime(self):
        """ Get system time in pool server """
        x = self.sendCommand('time')
        return float(x)

    def getTimeDiff(self):
        """ Get diference between system time in pool server and local time """
        t_server = self.getTime()
        t_local = time()
        t_diff = t_server - t_local
        return t_diff

    def isLive(self):
        """ Shows if pool is living """
        try:
            x = self.sendCommand('isLive')
            return bool(x)
        except:
            logging.error(str(sys.exc_info()[0]))
            return False

    def count(self):
        """ Returns the size of pool """
        x = self.sendCommand('count')
        return int(x)

    def sendData(self, controller, device, data, aux=None):
        """ Send data to pool """
        p = post(self.URL, data={
            'source': SourceType.CONTROLLER,
            'controller' : controller, 
            'device': device, 
            'data': self.serialize(data),
            'aux':aux
            })
            
        return p

    def sendDetection(self, classifier, idData, classes, aux=None):
        """ Send detection data to pool """
        p = post(self.URL, data={
            'source': SourceType.CLASSIFIER,
            'classifier' : classifier, 
            'id': idData, 
            'data': self.serialize(classes),
            'aux':aux
            })
        return p

    def getData(self, idData='', source:SourceType=None, controller='', device='', classifier='', limit=-1, lastTime=0):
        """ Get data from pool """
        g = get(self.URL, params={
            'id': idData, 
            'source': source, 
            'controller': controller, 
            'device': device, 
            'classifier': classifier, 
            'limit': limit,
            'lastTime': lastTime
            }).json()

        for i in range(1, len(g)):
            g[i]['data'] = self.deserialize(g[i]['data'])

        return g

    def serialize(self, data):
        """ Serialize to transfer estructures and objects """
        f = pickle.dumps(data, protocol=0) # protocol 0 is printable ASCII
        return str(f)

    def deserialize(self, data:str):
        """ Deserialize from transfered estructures and objects """
        o = pickle.loads(ast.literal_eval(data))
        return o

