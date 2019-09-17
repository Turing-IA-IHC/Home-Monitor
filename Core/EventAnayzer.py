"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the analyzers that can be loaded.
"""

import abc
from os.path import dirname, abspath, exists, split, normpath
import logging
from time import time

from DataPool import DataPool, EventPool
import Misc

class EventAnalyzer(abc.ABC):
    """ Generic class that represents all the analyzers that can be loaded. """
    
    def __init__(self, cfg=None):
        self.ep = EventPool()       # Object to get information
        self.dp = DataPool()        # Object to get information
        self.URL = ""               # Pool URL
        self.Me_Path = "./"         # Path of current component
        self.Standalone = False     # If a child start in standalone
        self.lastTime = time()      # Time of last petition to the pool
        
        self.Config = cfg           # Object with all config params
        self.NET = None             # Neural Network to predict

        self.Controller = ''        # Controller to filter data
        self.Device = ''            # Device name to filter data
        self.Limit = -1             # Amount of data to filter data

        self.loggingLevel = None    # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log

    """ Abstract methods """
    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Load knowledge for pre processing """
        pass
  
    @abc.abstractmethod
    def predict(self, data):
        """ Implement me! :: Do prediction and return class found """
        pass

    @abc.abstractmethod
    def showData(self, data, classes, aux):
        """ Implement me! :: To show data if this module start standalone.
        set self.Standalone = True before start. """
        pass

    @abc.abstractmethod
    def testData(self):
        """ Implement me! :: Data t test if this module start standalone. 
            You must return an array as expected if you query the data pool.
        set self.Standalone = True before start. """
        pass

    """ Real methods """
    def start(self):
        """ Start module and predicting """
        self.activateLog()
        self.ep.URL = self.URL
        self.dp.URL = self.URL

        self.preLoad()

        self.running = True

        logging.debug('Start detection of {} in {}.'.format(self.Config["CLASSES"], 
                        self.__class__.__name__))
        failedSend = 0
        while self.running:
            gdList = []
            _classes = None
            _idData = 0

            try:
                if not self.Standalone:
                    gdList = self.bring(controller=self.Controller, device=self.Device, 
                                        limit=self.Limit, lastTime=self.lastTime)
                    self.lastTime = gdList[0]['timeQuery']
                else:
                    gdList = self.testData()
                failedSend = 0        
            except:
                failedSend += 1
                logging.exception(
                    'Unexpected error getting data from pool: {}. Controller: {}, Device: {}, Limit: {}.'.format(
                        self.URL, self.Controller, self.Device, self.Limit))
                if failedSend > 2 and not self.dp.isLive():
                    logging.error('Pool no found {} will shutdown.'.format(self.__class__.__name__))
                    self.stop()
                    break
                continue

            for gd in  gdList[1:]:
                _idsEvents = []
                try:
                    _idsEvents, _aux = self.predict(gd)
                    _idData = gd['id']
                except:
                    logging.exception(
                        'Unexpected error in prediction from classifier: {} ({}).'.format(
                            self.__class__.__name__, self.Config["MACHINE_NAME"]))
                try:
                    #TODO: Change for a notifier
                    if not self.Standalone and len(_idsEvents) > 0:
                        self.sendDetection(_idsEvents, _aux)
                    else:
                        self.showData(gd, _idsEvents, _aux)
                    failedSend = 0        
                except:
                    failedSend += 1
                    logging.exception(
                        'Unexpected error sending data from classifier: {} ({}).'.format(
                            self.__class__.__name__, self.Config["MACHINE_NAME"]))

                    if failedSend > 2 and not self.dp.isLive():
                        logging.error('Pool no found {} will shutdown.'.format(self.__class__.__name__))
                        self.stop()
                        break            

    def stop(self):
        """ Stop module and predicting """
        self.running = False

    def sendDetection(self, idsData, message):
        """ Send detection data to pool """
        self.ep.sendDetection(analyzer=self.Config["MACHINE_NAME"], 
                            idsData=idsData, message=message)

    def bring(self, controller='', device='', classifier='', limit=-1, lastTime=0):
        """ Bring data from Pool """
        return self.ep.getEvents(controller=controller, device=device, limit=limit, lastTime=lastTime)
        
    def activateLog(self):
        """ Activate logging """
        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)
