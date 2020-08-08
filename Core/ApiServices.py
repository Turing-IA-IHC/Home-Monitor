"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to controlate input data throw api rest
"""
from flask import Flask, request
from flask_restful import Resource, reqparse
from requests import get, post, put
from time import time
import Misc
from DataPool import SourceTypes, LogTypes, Messages, PoolStates, Data, Binnacle, DataPool

class ApiBase():

    def get(self, parser, sourceType:SourceTypes, origin:str):
        """ Returns all active data. 
                Params: Data
            
            Retrive a object Data with structure:
                {
                    'id'            : self.id,
                    'born'          : self.born,
                    'source_type'   : str(self.source_type),
                    'source_name'   : self.source_name,
                    'source_item'   : self.source_item,
                    'package'       : self.package,
                    'data'          : self.serialize(self.data),
                    'aux'           : self.serialize(self.aux),
                    'state'         : str(self.state),
                },
                limit,
                lastTime,
                all
            
            Controller and device could be an Exp Reg.
            Ex. 'CamController' for single or 'CamController.*?' for all from CamController
        """
        try:
            #TODO: Si en lugar de data se reciben las variables id, package, source_name y source_item
            # como se registra en la documentación. Además el tipo lo debe sacar de la url que se usa
            parser = reqparse.RequestParser()
            parser.add_argument('data')
            parser.add_argument('limit')
            parser.add_argument('lastTime')
            parser.add_argument('onlyActive')
            args = parser.parse_args()

            dataIn = args.data
            dataIn = '' if dataIn == None else dataIn
            data = Data()
            data.id = '-1'
            if dataIn != '':
                data = data.parse(dataIn)

            limit = args.limit
            lastTime = args.lastTime
            onlyActive = True if args.onlyActive == '' else Misc.toBool(args.onlyActive)
            
            result = DataPool().getPool(data=data, limit=limit, lastTime=lastTime, onlyActive=onlyActive)
            
            result = list(map(lambda d: d.getJson(), result))
            result.insert(0, {'msg':'ok', 'queryTime' : time()})        
        except:
            message = Binnacle().errorDetail(Messages.error_pool_reading)
            Binnacle().logFromCore(message, LogTypes.ERROR, origin)
            result = [{'msg': message}]
        return result

    def post(self, parser, sourceType:SourceTypes, origin:str):
        """ Load data in pool. Params:
                data: Data
            
            Retrive a object Data with structure:
                {
                    'id'            : self.id,
                    'born'          : self.born,
                    'source_type'   : str(self.source_type),
                    'source_name'   : self.source_name,
                    'source_item'   : self.source_item,
                    'package'       : self.package,
                    'data'          : self.serialize(self.data),
                    'aux'           : self.serialize(self.aux),
                    'state'         : str(self.state),
                }
        """
        try:
            #TODO: Validar tipo de dato y si no coiside emitir error
            #TODO: E ltipo de dato esperado lo debe sacar de la clase en su instanciación
            parser = reqparse.RequestParser()
            parser.add_argument('data')
            args = parser.parse_args()

            dataIn = args.data
            dataIn = '' if dataIn == None else dataIn
            data = Data()
            data.id = -1
            if dataIn != '':
                data = data.parse(dataIn)
                if sourceType != SourceTypes.parse(data.source_type):
                    raise ValueError(Messages.bad_source_type_deteiled.format(sourceType, SourceTypes.parse(data.source_type)))
                DataPool().append(data)
                DataPool().pop()

            result = [{'msg': 'ok', 'id': data.id}]        
        except:
            message = Binnacle().errorDetail(Messages.error_pool_writing)
            Binnacle().logFromCore(message, LogTypes.ERROR, origin)
            result = [{'msg': message}]
        return result

    def put(self, parser, origin:str):
        """ Exec commands on pool """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('command')
            args = parser.parse_args()
            result = [{'msg': 'ok', 'res': DataPool().command(args.command)}]            
        except:
            message = Binnacle().errorDetail(Messages.error_pool_command)
            Binnacle().logFromCore(message, LogTypes.ERROR, origin)
            result = [{'msg': message}]
        return result

class ApiAlerts(Resource):
    """ Class to receive and return all alerts detected by analyzers """
    apiBase = ApiBase()

    def get(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.get(parser, SourceTypes.ANALYZER, self.__class__.__name__)
        return result

    def post(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.post(parser, SourceTypes.ANALYZER, self.__class__.__name__)
        return result

    def put(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.put(parser, self.__class__.__name__)
        return result

class ApiEvents(Resource):
    """ Class to receive and return all events detected by recognizers """
    apiBase = ApiBase()

    def get(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.get(parser, SourceTypes.RECOGNIZER, self.__class__.__name__)
        return result

    def post(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.post(parser, SourceTypes.RECOGNIZER, self.__class__.__name__)
        return result

    def put(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.put(parser, self.__class__.__name__)
        return result

class ApiTickets(Resource):
    """ Class to receive and return all tickets captured by controllers """
    apiBase = ApiBase()

    def get(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.get(parser, SourceTypes.CONTROLLER, self.__class__.__name__)
        return result

    def post(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.post(parser, SourceTypes.CONTROLLER, self.__class__.__name__)
        return result

    def put(self):
        parser = reqparse.RequestParser()
        result = self.apiBase.put(parser, self.__class__.__name__)
        return result

class ApiLogs(Resource):
    """ Class to receive messages generated by the components """

    def __init__(self):
        self.CONFIG = Misc.readConfig('./config.yaml')
        Binnacle().loggingConf(self.CONFIG)

    def post(self):
        """ Register message in Binnacle """
        parser = reqparse.RequestParser()        
        parser.add_argument('data')
        #parser.add_argument('data.data')
        #parser.add_argument('data.aux')
        parser.add_argument('logType')
        parser.add_argument('isCore')
        args = parser.parse_args()
        dataIn = args.data
        dataIn = '' if dataIn == None else dataIn
        data = Data()
        data.id = -1
        if dataIn != '':
            data = data.parse(dataIn, dataPlain=True, auxPlain=True)
            if Misc.toBool(args.isCore):
                Binnacle().logFromCore(data.data, LogTypes.parse(args.logType), data.aux)
            else:
                Binnacle().logFromComponent(data, LogTypes.parse(args.logType))
