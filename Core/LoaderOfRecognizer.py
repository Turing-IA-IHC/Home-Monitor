"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to load all activity recognizers.
"""

import sys
from os.path import normpath
import logging
from time import sleep
from multiprocessing import Process
import hashlib

import Misc
from Component import Component
from DataPool import LogTypes, Messages, CommPool
from DeviceController import DeviceController

class LoaderOfRecognizer:
    """ Class to load all activity recognizers. """

    def __init__(self, config):
        """ Initialize all variables """
        self.CONFIG = config
        self.CHECKING_TIME = int(Misc.hasKey(self.CONFIG, 'CHECKING_TIME', 10)) # Time in seconds to check service availability
        self.URL = self.CONFIG['URL_BASE']  # URL of pool server # TODO cambiar nombre a URL_POOL
        self.Recognizers = {}               # List of Recognizers
    
    def start(self):
        """ Start load of all device recognizers """
        cp = CommPool(self.CONFIG, preferred_url=CommPool.URL_TICKETS)
        cp.logFromCore(Messages.system_recognizers_connect.format(cp.URL_BASE), LogTypes.INFO, self.__class__.__name__)

        while True:
            cp.logFromCore(Messages.recognizer_searching, LogTypes.INFO, self.__class__.__name__)
            recognizersFolders =  Misc.lsFolders("./Recognizers")
            for cf in recognizersFolders:
                if Misc.hasKey(self.Recognizers, cf, None) == None:
                    comp = Component(cf, cp)
                    self.Recognizers[cf] = comp

            for c in self.Recognizers:
                comp = self.Recognizers[c]
                comp.load()
            
            sleep(self.CHECKING_TIME)

        cp.logFromCore(Messages.recognizer_stop, LogTypes.INFO, self.__class__.__name__)
        