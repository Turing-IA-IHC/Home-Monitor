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
from datetime import datetime
from os.path import normpath

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')
import Misc
from Misc import singleton
from enum import Enum, unique

import requests
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

import json
from json import JSONEncoder
import pickle
import ast

import re

from multiprocessing import Process, Value

@unique
class SourceTypes(Enum):
    """ Enumerator to define the type of data: 
        CONTROLLER=10, RECOGNIZER = 20, ANALYZER = 30.
    """
    CONTROLLER = 10
    RECOGNIZER = 20
    ANALYZER = 30
    @staticmethod
    def parse(T:str):
        if 'SourceTypes.CONTROLLER' == str(T) or 'CONTROLLER' == str(T).upper() or str(SourceTypes.CONTROLLER.value) == str(T):
            return SourceTypes.CONTROLLER
        elif 'SourceTypes.RECOGNIZER' == str(T) or 'RECOGNIZER' == str(T).upper() or str(SourceTypes.RECOGNIZER.value) == str(T):
            return SourceTypes.RECOGNIZER
        elif 'SourceTypes.ANALYZER' == str(T) or 'ANALYZER' == str(T).upper() or str(SourceTypes.ANALYZER.value) == str(T):
            return SourceTypes.ANALYZER
        else:
            return None

    @staticmethod
    def toString(sourceType:int):
        if SourceTypes.CONTROLLER == sourceType:
            return 'CONTROLLER'
        elif SourceTypes.RECOGNIZER == sourceType:
            return 'RECOGNIZER'
        elif SourceTypes.ANALYZER == sourceType:
            return 'ANALYZER'
        else:
            return ''

@unique
class LogTypes(Enum):
    """ Enumerator to define the type of logs: 
        CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0.
    """
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    @staticmethod
    def parse(T:str):
        if 'LogTypes.CRITICAL' == str(T) or 'CRITICAL' == str(T).upper() or str(LogTypes.CRITICAL.value) == str(T):
            return LogTypes.CRITICAL
        elif 'LogTypes.ERROR' == str(T) or 'ERROR' == str(T).upper() or str(LogTypes.ERROR.value) == str(T):
            return LogTypes.ERROR
        elif 'LogTypes.WARNING' == str(T) or 'WARNING' == str(T).upper() or str(LogTypes.WARNING.value) == str(T):
            return LogTypes.WARNING
        elif 'LogTypes.INFO' == str(T) or 'INFO' == str(T).upper() or str(LogTypes.INFO.value) == str(T):
            return LogTypes.INFO
        elif 'LogTypes.DEBUG' == str(T) or 'DEBUG' == str(T).upper() or str(LogTypes.DEBUG.value) == str(T):
            return LogTypes.DEBUG
        elif 'LogTypes.NOTSET' == str(T) or 'NOTSET' == str(T).upper() or str(LogTypes.NOTSET.value) == str(T):
            return LogTypes.NOTSET
        else:
            return None
        
    @staticmethod
    def toString(logType:int):
        if LogTypes.CRITICAL == logType:
            return 'CRITICAL'
        elif LogTypes.ERROR == logType:
            return 'ERROR'
        elif LogTypes.WARNING == logType:
            return 'WARNING'
        elif LogTypes.INFO == logType:
            return 'INFO'
        elif LogTypes.DEBUG == logType:
            return 'DEBUG'
        elif LogTypes.NOTSET == logType:
            return 'NOTSET'
        else:
            return ''

@unique
class PoolStates(Enum):
    """ Enumerator to define state of data: ACTIVE=10 or QUARENTIVE=20
    """
    ACTIVE = 10
    QUARANTINE = 20
    @staticmethod
    def parse(T:str):
        if 'PoolStates.ACTIVE' == str(T) or 'ACTIVE' == str(T).upper() or str(PoolStates.ACTIVE) == str(T):
            return PoolStates.ACTIVE
        elif 'PoolStates.QUARANTINE' == str(T) or 'QUARANTINE' == str(T).upper() or str(PoolStates.QUARANTINE) == str(T):
            return PoolStates.QUARANTINE
        else:
            return None
    
    @staticmethod
    def toString(poolState:int):
        if PoolStates.ACTIVE == poolState:
            return 'ACTIVE'
        elif PoolStates.QUARANTINE == poolState:
            return 'QUARANTINE'
        else:
            return ''

class Data():
    """ Structure to represent and transmit data in whole system.
        It could be any type of 'SourceTypes'.
    """
    id = str(time())                # ID of data, the pool itself change this value
    born = time()                   # Time used to life of data
    source_type:SourceTypes = None  # Module type generator of data: CONTROLLER, RECOGNIZER, ANALYZER.
    source_name:str = ''            # Name of the data generating component: camController, InfarctRecognizer...
    source_item:str = ''            # Name of item where data born: LivingRoom-Cam1
    package:str = ''                # To group data
    data = None                     # Data to analize
    aux = None                      # Auxiliar data
    state = PoolStates.ACTIVE       # State used to crontrolate the life time of data

    def getJson(self, dataPlain=False, auxPlain=False):
        """
        Returns a string with JSon format which represents this object.
        """
        j = {
            'id'            : self.id,
            'born'          : self.born,
            'source_type'   : str(self.source_type),
            'source_name'   : self.source_name,
            'source_item'   : self.source_item,
            'package'       : self.package,
            'data'          : self.data if dataPlain else self.serialize(self.data),
            'aux'           : self.aux if auxPlain else self.serialize(self.aux),
            'state'         : str(self.state),
        }
        return j

    def parse(self, dataStr:str, dataPlain=False, auxPlain=False):
        """
        Returns a Data object from Json string
        """
        j = json.loads(dataStr)
        d:Data = Data()
        d.id = j['id']
        d.born = j['born']
        d.source_type = SourceTypes.parse(j['source_type'])
        d.source_name = j['source_name']
        d.source_item = j['source_item']
        d.package = j['package']
        d.data = j['data'] if dataPlain else self.deserialize(j['data'])
        d.aux = j['aux'] if auxPlain else self.deserialize(j['aux'])
        d.state = PoolStates.parse(j['state'])
        return d

    def fromDict(self, dict):
        """ Creates a Data object using values into a dictionary """
        self.id = Misc.hasKey(dict, 'id', self.id)
        self.born = Misc.hasKey(dict, 'born', self.born)
        self.source_type = Misc.hasKey(dict, 'source_type', self.source_type)
        self.source_name = Misc.hasKey(dict, 'source_name', self.source_name)
        self.source_item = Misc.hasKey(dict, 'source_item', self.source_item)
        self.package = Misc.hasKey(dict, 'package', self.package)
        self.data = Misc.hasKey(dict, 'data', self.data)
        self.aux = Misc.hasKey(dict, 'aux', self.aux)
        self.state = Misc.hasKey(dict, 'state', self.state)
        return self
    
    def toString(self, dataPlain=False, auxPlain=False):
        """ Returns text Json Representation """
        x = JSONEncoder().encode(self.getJson(dataPlain, auxPlain))
        return x #'{' + x + '}'

    def toFile(self, path:str="./"):
        """ Save data into file.
            aux var must have 't', 'ext' values            
            Formats availables:
                image: image captured using cv2 of openCV
        """
        aux = self.strToJSon(self.aux)
        t = Misc.hasKey(aux,'t','')
        ext = Misc.hasKey(aux,'ext','')
        f = ''
        if t == 'image':
            from cv2 import cv2
            f = normpath(path + "/" + str(self.id) + "." + ext)
            cv2.imwrite(f, self.data)

        return f

    def strToJSon(self, str:str):
        """ Return an JSon object from a string """
        if str == None:
            return None
        return json.loads(str)

    def valueOf(self, key):
        """ Returns the value of a property """
        if key == 'id':
            return self.id
        elif key == 'born':
            return self.born
        elif key == 'source_type':
            return self.source_type
        elif key == 'source_name':
            return self.source_name
        elif key == 'source_item':
            return self.source_item
        elif key == 'package':
            return self.package
        elif key == 'data':
            return self.data
        elif key == 'aux':
            return self.aux
        elif key == 'state':
            return self.state
        else:
            return None

    def serialize(self, data):
        """ Serialize to transfer estructures and objects """
        f = pickle.dumps(data, protocol=0) # protocol 0 is printable ASCII
        return str(f)

    def deserialize(self, data:str):
        """ Deserialize from transfered estructures and objects """
        o = pickle.loads(ast.literal_eval(data))
        return o


@singleton
class Binnacle():

    def __init__(self):
        """ This method will be removed by singleton pattern """
        pass

    def loggingSettings(self, loggingLevel:LogTypes=logging.INFO, loggingFile=None, loggingFormat=None):
        """ Set default logging """
        if loggingLevel == None:
            loggingLevel = logging.INFO
        if loggingFormat == None:
            loggingFormat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=(LogTypes.parse(str(loggingLevel))).value,
            filename=loggingFile, 
            format=loggingFormat)

    def loggingConf(self, config):
        """ Prepare configuration of log """
        LOGGINGLEVEL = Misc.hasKey(config, 'LOGGING_LEVEL', None)   # Logging level to write
        LOGGINGFILE = Misc.hasKey(config, 'LOGGING_FILE', None)     # Name of file where write log
        LOGGINGFORMAT = Misc.hasKey(config, 'LOGGING_FORMAT', None) # Format to show the log
        self.loggingSettings(LOGGINGLEVEL, LOGGINGFILE, LOGGINGFORMAT)

    def log(self, msg:str, logType):
        """ Put a message in Binnacle """
        logging.log(logType, msg)

    def logFromComponent(self, data:Data, logType:LogTypes):
        """ Put a message of components in Binnacle """
        msg:str='source_type: {}, source_comp: {}, source_name:{}, msg: {}, aux: {}'
        msg = msg.format(data.source_type, data.source_name, data.source_item, data.data, data.aux)
        self.log(msg, logType.value)
    
    def logFromCore(self, msg:str, logType:LogTypes, origin:str):
        """ Put a message of core in Binnacle """
        msg:str='origin: {}, msg: {}'.format(origin, msg)
        msg = msg.format(origin, msg)
        self.log(msg, logType.value)

    def errorDetail(self, msg:str=''):
        """ Returns a text whith error details """
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = exc_tb.tb_frame.f_code.co_filename
        return '{} :: {} :: {} :: {} :: {}'.format(msg, exc_obj, exc_type, fname, exc_tb.tb_lineno)

class CommPool():
    """ Class to allow communication between Data Pool and Components. """
    URL_BASE    = ""            # Url of Data Pool Service
    URL_TICKETS = "api/tickets" # Path to tickets pool
    URL_EVENTS  = "api/events"  # Path to events pool
    URL_ALERTS  = "api/alerts"  # Path to alerts pool
    URL_LOGS    = "api/logs"    # Path to logs pool
    CONFIG      = None          # Params from config file
    lastTime    = 0             # Time of last query

    def __init__(self, config, preferred_url="api/alerts", standAlone=False):
        """ Initialize object to communicate with Data Pool. """
        self.CONFIG = config
        self.STANDALONE = standAlone
        if self.STANDALONE:
            Binnacle().loggingConf(self.CONFIG)
        else:
            self.URL_BASE = Misc.hasKey(self.CONFIG,'URL_BASE','http://127.0.0.1:500')
            self.PREFERRED_URL = preferred_url        

    def send(self, data:Data):
        """ Allows send data to Data Pool.
            If only data.data is set, then the other values will be taken of config file.
        """

        if SourceTypes.parse(data.source_type) == None:
            data.source_type = Misc.hasKey(self.CONFIG, 'SOURCE_TYPE', None)
        if data.source_name == '':
            data.source_name = Misc.hasKey(self.CONFIG, 'SOURCE_NAME', None)

        url = self.URL_BASE
        if SourceTypes.parse(data.source_type) == SourceTypes.CONTROLLER:
            url += "/" + self.URL_TICKETS
        elif SourceTypes.parse(data.source_type) == SourceTypes.RECOGNIZER:
            url += "/" + self.URL_EVENTS
        elif SourceTypes.parse(data.source_type) == SourceTypes.ANALYZER:
            url += "/" + self.URL_ALERTS
        else:
            raise ValueError(Messages.bad_source_type)

        p = requests.post(url, data={'data' : data.toString()}).json()
        
        if p[0]['msg'] != 'ok':
            raise ValueError(p[0]['msg'])

        return p

    def receive(self, data:Data, limit=-1, lastTime=-1, onlyActive=True):
        """ Allows to query to Data Pool. """
        
        if lastTime == -1:
            lastTime = self.lastTime

        url = self.URL_BASE
        source_type = None if SourceTypes.parse(data.source_type) == None else data.source_type
        if source_type == SourceTypes.CONTROLLER:
            url += "/" + self.URL_TICKETS
        elif source_type == SourceTypes.RECOGNIZER:
            url += "/" + self.URL_EVENTS
        elif source_type == SourceTypes.ANALYZER:
            url += "/" + self.URL_ALERTS
        else:
            raise ValueError(Messages.bad_source_type)

        data.id = '' if data.id == None else data.id

        g = requests.get(url, params={
            'data' : data.toString(),
            'limit' : limit,
            'lastTime' : lastTime,
            'onlyActive': onlyActive
            }).json()

        if g[0]['msg'] != 'ok':
            raise ValueError(g[0]['msg'])

        for i in range(1, len(g)):
            g[i]['data'] = data.deserialize(g[i]['data'])
            g[i]['aux'] = data.deserialize(g[i]['aux'])

        self.lastTime = g[0]['queryTime']
        return g

    def logFromComponent(self, data:Data, logType:LogTypes):
        """ Put a message of components in Binnacle """        
        try:
            data.source_type = Misc.hasKey(self.CONFIG, 'SOURCE_TYPE', None) if SourceTypes.parse(str(data.source_type)) == None else data.source_type
            data.source_name = Misc.hasKey(self.CONFIG, 'SOURCE_NAME', '') if data.source_name == '' else data.source_name

            if self.STANDALONE:
                Binnacle().logFromComponent(data, logType)
            else:
                url = self.URL_BASE + "/" + self.URL_LOGS
                requests.post(url, data={'data' : data.toString(), 'logType': logType, 'isCore':False})
        except:
            logging.error(Binnacle().errorDetail(Messages.error_pool_log))
            
    def logFromCore(self, msg:str, logType:LogTypes, origin:str):
        """ Put a message of core in Binnacle """
        try:
            data=Data()
            data.id = 0
            data.source_type = None
            data.source_name = 'Core'
            data.source_item = 'CommPool'
            data.data = msg
            data.aux = origin

            if self.STANDALONE:
                Binnacle().logFromCore(data.data, logType, origin)
            else:
                url = self.URL_BASE + "/" + self.URL_LOGS
                requests.post(url, data={'data' : data.toString(dataPlain=True, auxPlain=True), 'logType': logType, 'isCore':True})
        except:
            logging.error(Binnacle().errorDetail(Messages.error_pool_log))
            
    def errorDetail(self, msg:str=''):
        """ Returns a text whith error details """
        return Binnacle().errorDetail(msg)

    """ Generics function to interact with pool """
    def sendCommand(self, command):
        """ Function generic to send commands to pool """
        url = self.URL_BASE + "/" + self.PREFERRED_URL
        x = requests.put(url, data={'command': command}).json()
        if x[0]['msg'] != 'ok':
            raise ValueError(x[0]['msg'])
        return x[0]['res']

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
        except Exception as ex:
            message = '{} :: Err: {}."'.format(Messages.error_pool_life, ex)
            self.logFromCore(message, LogTypes.ERROR, self.__class__.__name__)
            return False

    def count(self):
        """ Returns the size of pool """
        x = self.sendCommand('count')
        return x #int(x)

@singleton
class DataPool(Resource):
    """ Class to controlate life time of data """
    CONFIG = None           # Params from config file
    POOL_TICKETS = []       # Base of data received from Controllers
    POOL_EVENTS = []        # Base of data received from Recognizers
    POOL_ALERTS = []        # Base of data received from Analyzers
    LOGGINGLEVEL:int = 0    # Logging level to write
    LOGGINGFILE = None      # Name of file where write log
    LOGGINGFORMAT = None    # Format to show the log
    T1 = 30                 # Seconds to keep data in active
    T2 = T1 + 30            # Seconds to keep data in quarentine

    Count = 0               # Quantity of data received

    def __init__(self):
        """ This method will be removed by singleton pattern """
        pass

    def getPool(self, data:Data, limit=-1, lastTime=-1, onlyActive=True):

        id = '' if data.id == None else data.id
        package = '' if data.package == None else data.package
        source_type = None if SourceTypes.parse(data.source_type) == None else data.source_type
        source_name = '' if data.source_name == None else data.source_name
        source_item = '' if data.source_item == None else data.source_item
        limit = -1 if limit == None else int(limit)
        lastTime = -1 if lastTime == None else float(lastTime)

        pool = []

        if source_type == SourceTypes.CONTROLLER:
            pool = self.POOL_TICKETS
        elif source_type == SourceTypes.RECOGNIZER:
            pool = self.POOL_EVENTS
        elif source_type == SourceTypes.ANALYZER:
            pool = self.POOL_ALERTS
        else:
            raise ValueError(Messages.bad_source_type)

        if onlyActive:
            pool = list(filter(lambda d: PoolStates.parse(d.state) == PoolStates.ACTIVE, pool))

        if id != '':
            idRE = re.compile('^' + id + '$')
            pool = list(filter(lambda d: idRE.match(str(d.id)) != None, pool))
        
        if package != '' and source_type == SourceTypes.CONTROLLER:
            print('pool 1', len(pool), package)
            for p in pool:
                print(p.id, p.package)

        if package != '':
            pool = list(filter(lambda d: d.package == package, pool))

        if package != '' and source_type == SourceTypes.CONTROLLER:
            print('pool 2', len(pool), package)

        if source_name != '':
            source_nameRE = re.compile('^' + source_name + '$')
            pool = list(filter(lambda d: source_nameRE.match(d.source_name) != None, pool))
        
        if source_item != '':
            source_itemRE = re.compile('^' + source_item + '$')
            pool = list(filter(lambda d: source_itemRE.match(d.source_item) != None, pool))
        
        if lastTime > -1:
            pool = list(filter(lambda d: d.born >= lastTime, pool))
        
        if limit > -1:
            pool = pool[-limit:]

        return pool

    def append(self, data:Data):
        pool = []
        source_type = None if SourceTypes.parse(data.source_type) == None else data.source_type
        if source_type == SourceTypes.CONTROLLER:
            pool = self.POOL_TICKETS
        elif source_type == SourceTypes.RECOGNIZER:
            pool = self.POOL_EVENTS
        elif source_type == SourceTypes.ANALYZER:
            pool = self.POOL_ALERTS
        else:
            raise ValueError(Messages.bad_source_type)
        
        self.Count += 1
        data.id = self.Count
        data.born = time()
        pool.append(data)

    def nextId(self):
        """ Return next id of data in system """
        return self.Count + 1

    def pop(self):        
        """ Move data to Quarantine or remove if life time is over of all pools. """
        self.popPool(self.POOL_TICKETS)
        self.popPool(self.POOL_EVENTS)
        self.popPool(self.POOL_ALERTS)
        
    def popPool(self, pool):
        """ Move data to Quarantine or remove if life time is over of a pool. """
        try:
            for p in pool:
                if time() - p.born > self.T2:
                    self.Count -= 1
                    pool.remove(p)
                elif time() - p.born > self.T1:
                    p.state = PoolStates.QUARANTINE
        except:
            message = Binnacle().errorDetail(Messages.error_pool_pop)
            Binnacle().logFromCore(message, LogTypes.ERROR, self.__class__.__name__)

    def command(self, cmd:str):
        """ Exec commands on pool """
        message = ''
        if cmd == 'time':
            message = time()
        elif cmd == 'isLive':
            message = True
        elif cmd == 'pop':
            self.pop()
            message = 'ok'
        elif cmd == 'count':
            message = 'Total={}\tTickets={}\tEvents={}\tAlerts={}'.format(self.Count, len(self.POOL_TICKETS), len(self.POOL_EVENTS), len(self.POOL_ALERTS))
        else:
            message = Messages.bad_command_name

        return message
        
    def initialize(self, config):
        self.CONFIG = config
        self.LOGGINGLEVEL = int(self.CONFIG['LOGGING_LEVEL'])
        self.LOGGINGFORMAT = self.CONFIG['LOGGING_FORMAT']
        self.LOGGINGFILE = self.CONFIG['LOGGING_FILE']
        self.T1 = int(self.CONFIG['T1'])
        self.T2 = int(self.CONFIG['T2']) + self.T1

    def start(self):
        """ Start api for data pool """

        app = Flask(__name__)
        log = logging.getLogger('werkzeug')
        log.setLevel(self.LOGGINGLEVEL + 10)
        app.logger = logging.getLogger()
        api = Api(app)

        from ApiServices import ApiAlerts, ApiEvents, ApiTickets, ApiLogs
        
        Binnacle().loggingConf(self.CONFIG)
        Binnacle().logFromCore('Starting /tickets', LogTypes.INFO, self.__class__.__name__)
        api.add_resource(ApiTickets, '/tickets', methods=['get', 'post', 'put']) 
        Binnacle().logFromCore('Starting /events', LogTypes.INFO, self.__class__.__name__)
        api.add_resource(ApiEvents, '/events',   methods=['get', 'post', 'put']) 
        Binnacle().logFromCore('Starting /alerts', LogTypes.INFO, self.__class__.__name__)
        api.add_resource(ApiAlerts, '/alerts',   methods=['get', 'post', 'put']) 
        Binnacle().logFromCore('Starting /logs', LogTypes.INFO, self.__class__.__name__)
        api.add_resource(ApiLogs, '/logs',       methods=['post']) 
        
        app.run()
        Binnacle().logFromCore(Messages.pool_stoped, LogTypes.INFO, self.__class__.__name__)

@singleton
class Messages():
    """ Messages of system """
    def __init__(self):
        """ This method will be removed by singleton pattern """
        pass

    nothing_to_load = 'There are nothing to load. set a number between 1 and 15 un components param'

    misc_terminate_process = 'Press control + c to terminate.'

    bad_source_type = 'Bad source_type'
    bad_source_type_deteiled = 'Bad source_type. Expepected: {} and received: {}'
    bad_command_name = 'bad command name'
    config_no_file = 'Config file does not exits '
    
    pool_stoped = 'Pool api stoped'

    error_class_name = 'Must be set CLASS_NAME variable into config.yaml file'
    error_file_class = 'Must be set FILE_CLASS variable into config.yaml file'
    error_pool_writing = 'Unexpected error writing data in pool'
    error_pool_reading = 'Unexpected error reading data in pool'
    error_pool_pop = 'Unexpected error poping data in pool'
    error_pool_command = 'Unexpected error executing a command in pool'
    error_pool_life = 'Unexpected error checking state of pool'
    error_pool_log = 'Unexpected error writing a message in pool'
    error_pool_connection = 'Failed connecting to {}. Check previous Binnacle messages'

    system_start = 'Start the magic'
    system_start_components = 'Starting components with command: '
    system_start_heart_beat = 'All sub systems will keep alive ...'
    system_error_heart_beat = 'Ooops an error on heart beat ocurred'

    comp_starting = 'Starting component {}'
    comp_change = 'Something changed in {}. It will be {}.'
    comp_try_start = 'Trying to load a componen from path: {}'
    comp_load_error = 'Unexpected error loading component in folder'
    
    system_pool_error = 'Ooops an error on pool service ocurred'
    system_pool_start = 'System starting pool in url: '
    system_pool_restart = 'Pool service is stopped. System auto restart it'
    system_pool_started = 'Pool started in url: '

    system_controllers_error = 'Ooops an error on controllers service ocurred'
    system_controllers_start = 'System starting controllers service. Pool Url: '
    system_controllers_restart = 'Controllers service is stopped. System auto restart it'
    system_controllers_started = 'Controllers service started. Pool Url: '
    system_controllers_connect = 'Trying to connect to Pool ({}) from loader of Controllers ...'
    controller_start = 'Starting device controller {}'
    controller_started = 'Device controller {} started'
    controller_searching = 'Searching for new device controllers...'
    controller_stop = 'Loader of Controllers stoped'
    controller_error_send = 'Unexpected error sending data from device'
    controller_error_get = 'Unexpected error getting data from device'
    controller_error_stop = 'Pool not available controller will be stoped'
    controller_loading_model = 'Loadding model from {}'

    system_recognizers_error = 'Ooops an error on recognizers service ocurred'
    system_recognizers_start = 'System starting recognizers service. Pool Url: '
    system_recognizers_restart = 'Recognizers service is stopped. System auto restart it'
    system_recognizers_started = 'Recognizers service started. Pool Url: '
    system_recognizers_connect = 'Trying to connect to Pool ({}) from loader of Recognizers ...'
    recognizer_start = 'Starting activity recognizer {}'
    recognizer_started = 'Activity recognizer {} started'
    recognizer_searching = 'Searching for new activity recognizers...'
    recognizer_stop = 'Loader of Recognizers stoped'
    recognizer_error_send = 'Unexpected error sending data from recognizer'
    recognizer_error_get = 'Unexpected error getting data from recognizer'
    recognizer_error_stop = 'Pool not available activity recognizer will be stoped'

    system_analyzers_error = 'Ooops an error on analyzers service ocurred'
    system_analyzers_start = 'System starting analyzers service. Pool Url: '
    system_analyzers_restart = 'Analyzers service is stopped. System auto restart it'
    system_analyzers_started = 'Analyzers service started. Pool Url: '
    system_analyzers_connect = 'Trying to connect to Pool ({}) from loader of Abalyzers ...'
    analyzer_start = 'Starting activity analyzer {}'
    analyzer_started = 'Activity analyzer {} started'
    analyzer_searching = 'Searching for new activity analyzers...'
    analyzer_stop = 'Loader of Analyzers stoped'
    analyzer_error_send = 'Unexpected error sending data from analyzer'
    analyzer_error_get = 'Unexpected error getting data from analyzer'
    analyzer_error_stop = 'Pool not available activity analyzer will be stoped'
    analyzer_error_Channels = 'Unexpected error Loading channels'

    system_channels_error = 'Ooops an error on channels service ocurred'
    system_channels_start = 'System starting channels service. Pool Url: '
    system_channels_restart = 'Channels service is stopped. System auto restart it'
    system_channels_started = 'Channels service started. Pool Url: '
    system_channels_connect = 'Trying to connect to Pool ({}) from loader of Abalyzers ...'
    channel_start = 'Starting activity channel {}'
    channel_started = 'Activity channel {} started'
    channel_searching = 'Searching for new activity channels...'
    channel_stop = 'Loader of Channels stoped'
    channel_error_send = 'Unexpected error sending data from channel'
    channel_error_get = 'Unexpected error getting data from channel'
    channel_error_stop = 'Pool not available activity channel will be stoped'
    channel_error_put_msg = 'Unexpected error putting a new message in pool of messages'
