"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the classifiers that can be loaded.
"""

import abc
from os.path import dirname, abspath, exists, split, normpath
import logging
from time import time

from DataPool import DataPool
import Misc

class ClassifierHAR(abc.ABC):
    """ Generic class that represents all the classifiers that can be loaded. """
    
    def __init__(self, cfg=None):
        self.dp = DataPool()        # Object to send information
        self.URL = ""               # Pool URL
        self.lastTime = time()      # Time of last petition to the pool
        
        self.Config = cfg           # Object with all config params
        self.Classes = self.Config['CLASSES']   # Classes able to detect
        #print(' -- ', self.Classes, len(self.Classes))

        self.loggingLevel = None    # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log

    """ Abstract methods """
    @abc.abstractmethod
    def start(self):
        """ Implement me! :: Start module and predicting """
        pass

    @abc.abstractmethod
    def stop(self):
        """ Implement me! :: Stop module and predicting """
        pass

    @abc.abstractmethod
    def predict(self, idDevice):
        """ Implement me! :: Do prediction and return class found """
        pass

    """ Real methods """
    def sendDetection(self, idData, classes):
        """ Send detection data to pool """
        self.dp.URL = self.URL
        print('Sending data to {}. idData: {}. classes: {}.'.format(self.URL, idData, classes))
        self.dp.sendDetection(idData, classes)

    def bring(self, controller = '', device = '', limit = -1, lastTime = 0):
        """ Bring data from Pool """
        self.dp.URL = self.URL
        #print('Bringing data from {}. controller: {}. device: {}. limit: {}. lastTime: {}.'.format(
        #    self.URL, controller, device, limit, lastTime))
        return self.dp.getData(controller, device, limit, lastTime)

    def activateLog(self):
        """ Activate logging """
        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)

    def loadModel(self, ModelPath=None, BasePath="./"):
        """ Load and returns keras + tensorflow model """
        from tensorflow.keras import backend as K
        from tensorflow.keras.models import Sequential, load_model

        if ModelPath == None:
            ModelPath = self.Config['MODEL']

        ModelPath = normpath(BasePath + "/" + ModelPath)
        logging.info('Loadding model ' + ModelPath + ' ...') #TODO: Change to Debug

        NET = load_model(ModelPath)
        if logging.getLogger().level <= logging.INFO: # Debug
            NET.summary()

