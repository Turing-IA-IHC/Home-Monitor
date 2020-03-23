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
    
    def toString(self, dataPlain=False, auxPlain=False):
        """ Returns text Json Representation """
        x = JSONEncoder().encode(self.getJson(dataPlain, auxPlain))
        return x #'{' + x + '}'

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

    def strToJSon(self, str:str):
        """ Return an JSon object from a string """
        return json.loads(str)

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

    def receive(self, data:Data, limit=-1, lastTime=-1):
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
            'lastTime' : lastTime
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
        return int(x)

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
    T0 = 30                 # Seconds to keep data in active
    T1 = T0 + 30            # Seconds to keep data in quarentine

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
        
        if package != '':
            pool = list(filter(lambda d: d.package == package, pool))

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
        #print('Pop', len(self.POOL_TICKETS), self.Count)

    def popPool(self, pool):
        """ Move data to Quarantine or remove if life time is over of a pool. """
        try:
            for p in pool:
                if time() - p.born > self.T1:
                    self.Count -= 1
                    #print('... Poping')
                    pool.remove(p)
                elif time() - p.born > self.T0:
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
            message = self.Count
        else:
            message = Messages.bad_command_name

        return message
        
    def initialize(self, config):
        self.CONFIG = config
        self.LOGGINGLEVEL = int(self.CONFIG['LOGGING_LEVEL'])
        self.LOGGINGFORMAT = self.CONFIG['LOGGING_FORMAT']
        self.LOGGINGFILE = self.CONFIG['LOGGING_FILE']
        self.T1 = int(self.CONFIG['T1'])
        self.T2 = int(self.CONFIG['T2'])

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
        api.add_resource(ApiAlerts, '/alerts',    methods=['get', 'post', 'put']) 
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


#@singleton
#class EventPool(Resource):
#    """ Class to query events pool """
#    def __init__(self):
#        """ Start class variables """
#        self.Config = Misc.readConfig("./config.yaml")
#        self.URL = self.Config['POOL_PATH']             # URL to start event pool reader
#        self.dp = DataPool()                            # Pool object        
#        
#    """ Class to get events data """
#    def get(self):
#        """ Return all active data """
#        result = list(filter(lambda d: PoolStates.parse(d.state) == PoolStates.ACTIVE, self.dp.pool))
#        resultRECOGNIZERs = list(filter(lambda d: SourceTypes.parse(d.source) == SourceTypes.RECOGNIZER, result))
#        resultControllers = list(filter(lambda d: SourceTypes.parse(d.source) == SourceTypes.CONTROLLER, result))
#        for res in resultRECOGNIZERs:
#            oriData = list(filter(lambda d: d.id == res.id, resultControllers))
#            if len(oriData) > 0:
#                res.controller = oriData[-1].controller
#                res.device = oriData[-1].device                
#
#        parser = reqparse.RequestParser()
#        parser.add_argument('id')
#        parser.add_argument('controller')
#        parser.add_argument('device')
#        parser.add_argument('RECOGNIZER')
#        parser.add_argument('limit')
#        parser.add_argument('lastTime')
#        args = parser.parse_args()
#
#        id = args.id
#        controller = args.controller
#        device = args.device
#        RECOGNIZER = args.RECOGNIZER
#        limit = args.limit
#        lastTime = args.lastTime
#
#        id = '' if id == None else id
#        controller = '' if controller == None else controller
#        device = '' if device == None else device
#        RECOGNIZER = '' if RECOGNIZER == None else RECOGNIZER
#        limit = -1 if limit == None else int(limit)
#        lastTime = 0 if lastTime == None else float(lastTime)
#
#        result = resultRECOGNIZERs
#        if id != '':
#            idRE = re.compile('^' + id + '$')
#            result = list(filter(lambda d: idRE.match(d.id) != None, result))
#        
#        if device != '':
#            deviceRE = re.compile('^' + device + '$')
#            result = list(filter(lambda d: deviceRE.match(d.device) != None, result))
#        
#        if controller != '':
#            controllerRE = re.compile('^' + controller + '$')
#            result = list(filter(lambda d: controllerRE.match(d.controller) != None, result))
#            
#        if RECOGNIZER != '':
#            RECOGNIZERRE = re.compile('^' + RECOGNIZER + '$')
#            result = list(filter(lambda d: RECOGNIZERRE.match(d.RECOGNIZER) != None, result))
#        
#        if lastTime > 0:
#            result = list(filter(lambda d: d.born >= lastTime, result))
#        
#        if limit > -1:
#            result = result[-limit:]
#
#        result = list(map(lambda d: d.getJson(), result))
#        result.insert(0, {'timeQuery' : time()})
#
#        return result
#    
#    def post(self):
#        """ Save events  """
#        try:             
#            parser = reqparse.RequestParser()
#            parser.add_argument('ids')
#            parser.add_argument('analyzer')
#            parser.add_argument('message')
#            args = parser.parse_args()
#
#            ids = self.dp.deserialize(args.ids)
#            analyzer = args.analyzer
#            message = args.message
#
#            result = self.dp.pool
#            #resultRECOGNIZERs = list(filter(lambda d: SourceTypes.parse(d.source) == SourceTypes.RECOGNIZER, result))
#            resultControllers = list(filter(lambda d: SourceTypes.parse(d.source) == SourceTypes.CONTROLLER, result))
#        
#            pathBase = self.Config["SAVE_PATH"] + '{0:%Y%m%d_%H%M}'.format(datetime.now()) + "-" + analyzer
#            Misc.createFolders(pathBase)
#            f = open(pathBase + "/message.txt","a+")
#            f.write(message)
#            f.write('\n')
#            f.close()
#
#            for id in ids:
#                oriData = list(filter(lambda d: d.id == id, resultControllers))
#                if len(oriData) == 0:
#                    continue
#                package = oriData[-1].package
#                oriData = list(filter(lambda d: d.package == package, resultControllers))
#                
#                for o in oriData:
#                    aux = json.loads(o.valueOf('aux'))
#                    Misc.saveByType(o.valueOf('data'), aux['t'], "{}/{}{}.{}".format(pathBase, o.valueOf('device'), o.valueOf('id'), aux['ext']))
#
#            message = 'ok'
#        
#        except:
#            logging.exception('Unexpected saving event data. :: Err: {}.'.format(str(sys.exc_info()[0])))
#            message = 'Unexpected saving event data. :: Err: {}.'.format(str(sys.exc_info()[0]))
#
#        return message
#
#    def getEvents(self, idData='', controller='', device='', RECOGNIZER='', limit=-1, lastTime=0):
#        """ Get data from pool. """
#        g = get(self.URL, params={
#            'id': idData,
#            'controller': controller, 
#            'device': device, 
#            'RECOGNIZER': RECOGNIZER, 
#            'limit': limit,
#            'lastTime': lastTime
#            }).json()
#
#        for i in range(1, len(g)):
#            g[i]['data'] = self.dp.deserialize(g[i]['data'])
#
#        return g    
#
#    def getEventsFormatted(self, Custom='', Tokens=[], idData='', controller='', device='', RECOGNIZER='', limit=-1, lastTime=0):
#        """ Get data from pool.
#            Tokens Availiables:
#                'id',
#                'source',
#                'controller',
#                'device',
#                'RECOGNIZER',
#                'born',
#                'data',
#                'aux'        
#         """        
#        g = self.getEvents(idData, controller, device, RECOGNIZER, limit, lastTime)
#
#        Tokens = Tokens if len(Tokens) > 0 else ['id', 'born', 'RECOGNIZER', 'data', 'device', 'controller']
#        Formater = '{}: At {} the {} detected {} in {} of {}.' if Custom == '' else Custom
#
#        Messages = []
#        for i in range(1, len(g)):
#            res = g[i]
#            Values = []
#            for t in range(len(Tokens)):
#                Values.append(Tokens[t])
#
#            msg = Formater.format(*Values).replace('[','').replace(']','')
#            Messages.append(msg)
#        
#        Messages.insert(0, g[0])
#
#        return Messages
#    
#    def sendDetection(self, analyzer, idsData, message):
#        """ Send detection from analyzer to save data """
#        p = post(self.URL, data={
#            'analyzer' : analyzer, 
#            'message' : message, 
#            'ids': self.dp.serialize(idsData)
#            })
#        return p
#
#@singleton
#class DataPoolold(Resource):
#    """ Class to controlate life time of data """
#    def __init__(self):
#        """ Start class variables """
#        self.URL = ""               # URL to start Pool
#        self.TimeDiff = 0           # Defference between pool server and local time
#
#        self.pool = []              # Store of data
#        self.countData = 0          # Amount of data received
#
#        self.T0 = 30                # Seconds to keep data in active
#        self.T1 = self.T0 + 30      # Seconds to keep data in quarentine
#        
#        self.loggingLevel:int = 0   # logging level to write
#        self.loggingFile = None     # Name of file where write log
#        self.loggingFormat = None   # Format to show the log
##
##    def append(self, data:Data):
#        """ Add new data to the pool """
#        if data.source == SourceTypes.CONTROLLER:
#            data.id += '-' + str(len(self.pool))
#        self.countData += 1
#        self.pool.append(data)
##
##    def pop(self):
#        """ Move data if life time is over """
#        for p in self.pool:
#            if time() - p.born > self.T1:
#                self.pool.remove(p)
#            elif time() - p.born > self.T0:
#                p.state = PoolStates.QUARANTINE
##
##    def get(self):
#        """ Return all active data:
#        Controller and device coulbe Exp Reg.
#        Ex. 'CamController' for single or 'CamController.*?' for all from CamController """
#        parser = reqparse.RequestParser()
#        parser.add_argument('id')
#        parser.add_argument('source')
#        parser.add_argument('package')
#        parser.add_argument('controller')
#        parser.add_argument('device')
#        parser.add_argument('RECOGNIZER')
#        parser.add_argument('limit')
#        parser.add_argument('lastTime')
#        args = parser.parse_args()
#        
#        id = args.id
#        source = args.source
#        package = args.package
#        controller = args.controller
#        device = args.device
#        RECOGNIZER = args.RECOGNIZER
#        limit = args.limit
#        lastTime = args.lastTime
#
#        id = '' if id == None else id
#        package = '' if package == None else package
#        source = '' if source == None else source
#        controller = '' if controller == None else controller
#        device = '' if device == None else device
#        RECOGNIZER = '' if RECOGNIZER == None else RECOGNIZER
#        limit = -1 if limit == None else int(limit)
#        lastTime = 0 if lastTime == None else float(lastTime)
#
#        #result = self.pool[:]
#        result = list(filter(lambda d: PoolStates.parse(d.state) == PoolStates.ACTIVE, self.pool))
#              
#        if id != '':
#            idRE = re.compile('^' + id + '$')
#            result = list(filter(lambda d: idRE.match(d.id) != None, result))
#        
#        if device != '':
#            deviceRE = re.compile('^' + device + '$')
#            result = list(filter(lambda d: deviceRE.match(d.device) != None, result))
#        
#        if controller != '':
#            controllerRE = re.compile('^' + controller + '$')
#            result = list(filter(lambda d: controllerRE.match(d.controller) != None, result))
#            
#        if RECOGNIZER != '':
#            RECOGNIZERRE = re.compile('^' + RECOGNIZER + '$')
#            result = list(filter(lambda d: RECOGNIZERRE.match(d.RECOGNIZER) != None, result))
#        
#        if source != '':
#            result = list(filter(lambda d: SourceTypes.parse(d.source) == SourceTypes.parse(source), result))
#        
#        if package != '':
#            result = list(filter(lambda d: d.package == package, result))
#            
#        if lastTime > 0:
#            result = list(filter(lambda d: d.born >= lastTime, result))
#        
#        if limit > -1:
#            result = result[-limit:]
#        
#        result = list(map(lambda d: d.getJson(), result))
#        result.insert(0, {'timeQuery' : time()})
#
#        return result
##
##    def post(self):
#        """ Load data in pool """
#        try:             
#            parser = reqparse.RequestParser()
#            parser.add_argument('id')
#            parser.add_argument('source')
#            parser.add_argument('package')
#            parser.add_argument('controller')
#            parser.add_argument('device')
#            parser.add_argument('RECOGNIZER')
#            parser.add_argument('data')
#            parser.add_argument('aux')
#            args = parser.parse_args()
#
#            data = Data()
#            
#            if SourceTypes.parse(args.source) == SourceTypes.CONTROLLER:
#                data.id = str(time())
#                data.source = SourceTypes.CONTROLLER
#                data.controller = args.controller
#                data.device = args.device
#                data.package = args.package
#            elif SourceTypes.parse(args.source) == SourceTypes.RECOGNIZER:
#                data.id = args.id
#                data.source = SourceTypes.RECOGNIZER
#                data.RECOGNIZER = args.RECOGNIZER
#                pass
#            
#            data.data = args.data
#            data.aux = args.aux
#            data.born = time()
#            self.append(data)
#            self.pop()
#
#            message = 'ok'
#        
#        except:
#            logging.exception('Unexpected writting data in pool. :: Err: {}.'.format(str(sys.exc_info()[0])))
#            message = 'Unexpected writting data in pool. :: Err: {}.'.format(str(sys.exc_info()[0]))
#
#        return message
##
##    def put(self):
##        """ Exec commands on pool """
##        parser = reqparse.RequestParser()
##        parser.add_argument('command')
##        args = parser.parse_args()
##        message = ''
#        if args.command == 'time':
#            message = time()
#        elif args.command == 'isLive':
#            message = True
#        elif args.command == 'pop':
#            self.pop()
#            message = 'ok'
#        elif args.command == 'count':
#            message = len(self.pool)
#        else:
#            message = 'Bad command name'
#
#        return message
#
#    def start(self):
#        """ Start api for data pool """
#
#        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)
#
#        app = Flask(__name__)
#        log = logging.getLogger('werkzeug')
#        log.setLevel(self.loggingLevel + 10)
#        app.logger = logging.getLogger()
#        api = Api(app)
#        api.add_resource(DataPool, 
#            '/pool',
#            methods=['get', 'post', 'put']) 
#        
#        api.add_resource(EventPool, 
#            '/events',
#            methods=['get', 'post'])
#
#        app.run()
#        logging.info('Pool api stoped.')
#
#    """ Functions to interact with Pool """
#
#    def sendCommand(self, command):
#        """ Function generic to send commands to pool """
#        x = put(self.URL, data={'command': command}).json()
#        return x
#
#    def getTime(self):
#        """ Get system time in pool server """
#        x = self.sendCommand('time')
#        return float(x)
#
#    def getTimeDiff(self):
#        """ Get diference between system time in pool server and local time """
#        t_server = self.getTime()
#        t_local = time()
#        t_diff = t_server - t_local
#        return t_diff
#
#    def isLive(self):
#        """ Shows if pool is living """
#        try:
#            x = self.sendCommand('isLive')
#            return bool(x)
#        except:
#            logging.error(str(sys.exc_info()[0]))
#            return False
#
#    def count(self):
#        """ Returns the size of pool """
#        x = self.sendCommand('count')
#        return int(x)
#
#    def sendData(self, controller, device, data, aux=None, package=''):
#        """ Send data to pool """
#        p = post(self.URL, data={
#            'source': SourceTypes.CONTROLLER,
#            'controller' : controller, 
#            'device': device, 
#            'data': self.serialize(data),
#            'aux':aux,
#            'package':package
#            })
#            
#        return p
#
#    def sendDetection(self, RECOGNIZER, idData, classes, aux=None):
#        """ Send detection data to pool """
#        p = post(self.URL, data={
#            'source': SourceTypes.RECOGNIZER,
#            'RECOGNIZER' : RECOGNIZER, 
#            'id': idData, 
#            'data': self.serialize(classes),
#            'aux':aux
#            })
#        return p
#
#    def getData(self, idData='', source:SourceTypes=None, controller='', device='', RECOGNIZER='', limit=-1, lastTime=0):
#        """ Get data from pool """
#        g = get(self.URL, params={
#            'id': idData, 
#            'source': source, 
#            'controller': controller, 
#            'device': device, 
#            'RECOGNIZER': RECOGNIZER, 
#            'limit': limit,
#            'lastTime': lastTime
#            }).json()
#
#        for i in range(1, len(g)):
#            g[i]['data'] = self.deserialize(g[i]['data'])
#
#        return g
#
#    def serialize(self, data):
#        """ Serialize to transfer estructures and objects """
#        f = pickle.dumps(data, protocol=0) # protocol 0 is printable ASCII
#        return str(f)
#
#    def deserialize(self, data:str):
#        """ Deserialize from transfered estructures and objects """
#        o = pickle.loads(ast.literal_eval(data))
#        return o
#
#