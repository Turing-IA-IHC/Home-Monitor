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
from DataPool import DataPool
import Misc

class ClassifierHAR(abc.ABC):
    """ Generic class that represents all the classifiers that can be loaded. """
    
    def __init__(self, cfg=None):
        self.dp = DataPool()        # Object to send information
        self.URL = ""               # Pool URL
        
        self.Config = cfg           # Object with all config params
        self.Classifiers = []       # List of classifiers loaded
        self.Classes = [ 'None' ]   # Classes able to detect

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
    def Predict(self, idDevice):
        """ Implement me! :: Do prediction and return class found """
        pass

    """ Real methods """
    def sendDetection(self, idData, classes):
        """ Send detection data to pool """
        self.dp.URL = self.URL
        #print('Sending data to {}. controller: {}. device: {}.'.format(self.URL, controller, device))
        self.dp.sendData(controller, device, data)

    def bring(self, controller = '', device = '', limit = -1, lastTime = 0):
        """ Bring data from Pool """
        self.dp.URL = self.URL
        #print('Bringing data from {}. controller: {}. device: {}.'.format(self.URL, controller, device))
        self.dp.getData(controller, device, limit, lastTime)

    def activateLog(self):
        """ Activate logging """
        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)
