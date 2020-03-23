"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the analyzers that can be loaded.
"""

if __name__ == "__main__":
    print('\n\tAlert!! This class can not start itself. Please start using main.py file.')
    exit(0)

import sys
from os.path import dirname, normpath
from time import sleep
import abc

import Misc
from Component import Component
from DataPool import Data, Messages, LogTypes, SourceTypes, CommPool

class EventAnalyzer(Component):
    """ Generic class that represents all the analyzers that can be loaded. """
    MODEL = None
    DATA_FILTER = Data()
    Limit:int = -1
    LastTime:float = -1
    CLASSES = []
    Channels = {}

    def start(self):
        """ Start module isolated """
        self.DATA_FILTER.source_type = SourceTypes.RECOGNIZER
        self.DATA_FILTER.source_name = Misc.hasKey(self.CONFIG, 'FILTER_NAME', '')
        self.DATA_FILTER.source_item = Misc.hasKey(self.CONFIG, 'FILTER_ITEM', '')
        self.Limit = Misc.hasKey(self.CONFIG, 'FILTER_LIMIT', -1)
        self.CLASSES = Misc.hasKey(self.CONFIG, 'CLASSES', [])

        self.preLoad()
        self.loadModel()
        self.loadChannels()
        self.loaded()
        
        self.running = True
        failedSend = 0

        while self.running:

            gdList = []
            try:
                if Misc.toBool(self.STANDALONE):
                    gdList = self.simulateData(self.DATA_FILTER)
                else:
                    gdList = self.simulateData(self.DATA_FILTER)
                    #gdList = self.bring(self.DATA_FILTER)

                self.LastTime = float(gdList[0]['timeQuery'])                    
            except:
                dataE = Data()
                dataE.source_type = SourceTypes.ANALYZER
                dataE.source_name = self.ME_NAME
                dataE.source_item = ''
                dataE.data = self.COMMPOOL.errorDetail(Messages.analyzer_error_get)
                dataE.aux = ''
                self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)

            for data in gdList[1:]:
                try:
                    package = Misc.randomString()
                    dataAnalizedList = self.analyze(data)
                    for dataAnalized in dataAnalizedList:
                        dataAnalized.package = package
                        if Misc.toBool(self.STANDALONE):
                            self.showData(dataAnalized, data)
                        else:
                            self.notify(dataAnalized)
                        failedSend = 0
                except:
                    dataE = Data()
                    dataE.source_type = SourceTypes.ANALYZER
                    dataE.source_name = self.ME_NAME
                    dataE.source_item = ''
                    dataE.data = self.COMMPOOL.errorDetail(Messages.analyzer_error_send)
                    dataE.aux = ''
                    self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)

                    failedSend += 1

                    if failedSend > 2 and (Misc.toBool(self.STANDALONE) or not self.COMMPOOL.isLive()):
                        dataE = Data()
                        dataE.source_type = SourceTypes.ANALYZER
                        dataE.source_name = self.ME_NAME
                        dataE.source_item = ''
                        dataE.data = Messages.analyzer_error_stop
                        dataE.aux = ''
                        self.COMMPOOL.logFromComponent(dataE, LogTypes.WARNING)
                        self.stop()
                        break

    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        pass

    @abc.abstractmethod
    def loadModel(self):
        """ Loads model """
        pass

    def loadChannels(self):
        """ Loads available channels """
        pass

    @abc.abstractmethod
    def loaded(self):
        """  Implement me! :: Just after load the model """
        pass
    
    def bring(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Returns a list objects type Data from pool """
        return []

    @abc.abstractmethod
    def analyze(self, data:Data):
        """ Implement me! :: Exec prediction to recognize an activity """
        pass

    def notify(self, data:Data):
        """ Send data to pool """
        for chl in self.Channels:
            # TODO Invocar listado de notificadores
            pass

    def stop(self):
        """ Stop module and getting data """
        self.running = False

    @abc.abstractmethod
    def showData(self, dataAnalized:Data, dataSource:Data):
        """  Implement me! :: To show data if this module start standalone """
        pass

    @abc.abstractmethod
    def simulateData(self, device):
        """  Implement me! :: Allows to simulate data if this module start standalone """
        pass

    
#    def __init__(self, cfg=None):
#        self.ep = EventPool()       # Object to get information
#        self.dp = DataPool()        # Object to get information
#        self.URL = ""               # Pool URL
#        self.Me_Path = "./"         # Path of current component
#        self.Standalone = False     # If a child start in standalone
#        self.lastTime = time()      # Time of last petition to the pool
#        
#        self.Config = cfg           # Object with all config params
#        self.NET = None             # Neural Network to predict
#
#        self.Controller = ''        # Controller to filter data
#        self.Device = ''            # Device name to filter data
#        self.Limit = -1             # Amount of data to filter data
#
#        self.loggingLevel = None    # logging level to write
#        self.loggingFile = None     # Name of file where write log
#        self.loggingFormat = None   # Format to show the log
#
#    """ Abstract methods """
#    @abc.abstractmethod
#    def preLoad(self):
#        """ Implement me! :: Load knowledge for pre processing """
#        pass
#  
#    @abc.abstractmethod
#    def predict(self, data):
#        """ Implement me! :: Do prediction and return class found """
#        pass
#
#    @abc.abstractmethod
#    def showData(self, data, classes, aux):
#        """ Implement me! :: To show data if this module start standalone.
#        set self.Standalone = True before start. """
#        pass
#
#    @abc.abstractmethod
#    def testData(self):
#        """ Implement me! :: Data t test if this module start standalone. 
#            You must return an array as expected if you query the data pool.
#        set self.Standalone = True before start. """
#        pass
#
#    """ Real methods """
#    def start(self):
#        """ Start module and predicting """
#        self.activateLog()
#        self.ep.URL = self.URL
#        self.dp.URL = self.URL
#
#        self.preLoad()
#
#        self.running = True
#
#        logging.debug('Start detection of {} in {}.'.format(self.Config["CLASSES"], 
#                        self.__class__.__name__))
#        failedSend = 0
#        while self.running:
#            gdList = []
#            _classes = None
#            _idData = 0
#
#            try:
#                if not self.Standalone:
#                    gdList = self.bring(controller=self.Controller, device=self.Device, 
#                                        limit=self.Limit, lastTime=self.lastTime)
#                    self.lastTime = gdList[0]['timeQuery']
#                else:
#                    gdList = self.testData()
#                failedSend = 0        
#            except:
#                failedSend += 1
#                logging.exception(
#                    'Unexpected error getting data from pool: {}. Controller: {}, Device: {}, Limit: {}.'.format(
#                        self.URL, self.Controller, self.Device, self.Limit))
#                if failedSend > 2 and not self.dp.isLive():
#                    logging.error('Pool no found {} will shutdown.'.format(self.__class__.__name__))
#                    self.stop()
#                    break
#                continue
#
#            for gd in  gdList[1:]:
#                _idsEvents = []
#                try:
#                    _idsEvents, _aux = self.predict(gd)
#                    _idData = gd['id']
#                except:
#                    logging.exception(
#                        'Unexpected error in prediction from classifier: {} ({}).'.format(
#                            self.__class__.__name__, self.Config["MACHINE_NAME"]))
#                try:
#                    #TODO: Change for a notifier
#                    if not self.Standalone and len(_idsEvents) > 0:
#                        self.sendDetection(_idsEvents, _aux)
#                    else:
#                        self.showData(gd, _idsEvents, _aux)
#                    failedSend = 0        
#                except:
#                    failedSend += 1
#                    logging.exception(
#                        'Unexpected error sending data from classifier: {} ({}).'.format(
#                            self.__class__.__name__, self.Config["MACHINE_NAME"]))
#
#                    if failedSend > 2 and not self.dp.isLive():
#                        logging.error('Pool no found {} will shutdown.'.format(self.__class__.__name__))
#                        self.stop()
#                        break            
#
#    def stop(self):
#        """ Stop module and predicting """
#        self.running = False
#
#    def sendDetection(self, idsData, message):
#        """ Send detection data to pool """
#        self.ep.sendDetection(analyzer=self.Config["MACHINE_NAME"], 
#                            idsData=idsData, message=message)
#
#    def bring(self, controller='', device='', classifier='', limit=-1, lastTime=0):
#        """ Bring data from Pool """
#        return self.ep.getEvents(controller=controller, device=device, limit=limit, lastTime=lastTime)
#        
#    def activateLog(self):
#        """ Activate logging """
#        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)
#