"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the communication channles that can be loaded.
"""

import abc
from os.path import dirname, abspath, exists, split, normpath
import logging
from time import time

from DataPool import DataPool
import Misc

class CommChannel(abc.ABC):
    """ Generic class that represents all the communication channles that can be loaded. """
    
    def __init__(self, cfg=None):
        self.dp = DataPool()        # Object to send information
        self.URL = ""               # Pool URL
        self.Me_Path = "./"         # Path of current component
        self.Standalone = False     # If a child start in standalone
        
        self.Config = cfg           # Object with all config params

        self.loggingLevel = None    # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log

    """ Abstract methods """
    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Load configurations for to send message """
        pass
  
    @abc.abstractmethod
    def send(self, Data, Subject, Message, To, CC='', BCC=''):
        """ Implement me! :: Sen message.
            Data: contains details of event like {id:1000}.
         """
        pass
    """ Real methods """
    def bring(self, controller='', device='', limit=-1, lastTime=0):
        """ Bring data from Pool """
        # TODO: Ver como se van consultar y retornar los datos de la detección por ejemplo id o package
        self.dp.URL = self.URL
        return self.dp.getData(controller=controller, device=device, limit=limit, lastTime=lastTime)
        
    def activateLog(self):
        """ Activate logging """
        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)