"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Generic class that represents all the classifiers that can be loaded.
"""

import abc
from os.path import dirname, abspath, exists, split, normpath
import logging
from time import time

from DataPool import DataPool
import Misc

#TODO: Parece wque esta clase ya no va
class ClassifierHAR(abc.ABC):
    """ Generic class that represents all the classifiers that can be loaded. """
    
    def __init__(self, cfg=None):
        self.dp = DataPool()        # Object to send information
        self.URL = ""               # Pool URL
        self.Me_Path = "./"         # Path of current component
        self.Standalone = False     # If a child start in standalone
        self.lastTime = time()      # Time of last petition to the pool
        
        self.Config = cfg           # Object with all config params
        self.Classes = self.Config['CLASSES']   # Classes able to detect
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
        """ Implement me! :: Load everything need to proccess """
        pass
  
    @abc.abstractmethod
    def loadModel(self):
        """ Implement me! :: Load knowledge for prediction """
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
        """ Start module and prediction """
        self.activateLog()
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
                _classes = []
                try:
                    _classes, _aux = self.predict(gd)
                    _idData = gd['id']
                except:
                    logging.exception(
                        'Unexpected error in prediction from classifier: {} ({}).'.format(
                            self.__class__.__name__, self.Config["MACHINE_NAME"]))
                
                try:
                    if not self.Standalone and len(_classes) > 0:
                        self.sendDetection(_idData, _classes, _aux)
                    else:
                        self.showData(gd, _classes, _aux)
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

    def sendDetection(self, idData, classes, aux=None):
        """ Send detection data to pool """
        self.dp.URL = self.URL
        self.dp.sendDetection(classifier=self.Config["MACHINE_NAME"], 
                            idData=idData, classes=classes, aux=aux)

    def bring(self, controller='', device='', limit=-1, lastTime=0):
        """ Bring data from Pool """
        self.dp.URL = self.URL
        return self.dp.getData(controller=controller, device=device, limit=limit, lastTime=lastTime)
    
    def activateLog(self):
        """ Activate logging """
        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)
