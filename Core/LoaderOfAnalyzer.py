"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to control all Analyzer components to load in system.
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
from FactAnalyzer import FactAnalyzer

class LoaderOfAnalyzer:
    """ Class to control all Analyzer components to load in system. """
    def __init__(self, config):
        """ Initialize all variables """
        self.CONFIG = config
        self.CHECKING_TIME = int(Misc.hasKey(self.CONFIG, 'CHECKING_TIME', 10)) # Time in seconds to check service availability
        self.URL_POOL = self.CONFIG['URL_BASE']  # URL of pool server
        self.Analyzers = {}                 # List of analyzers
    
    def start(self):
        """ Start load of all device analyzers """
        cp = CommPool(self.CONFIG, preferred_url=CommPool.URL_EVENTS)
        cp.logFromCore(Messages.system_analyzers_connect.format(cp.URL_BASE), LogTypes.INFO, self.__class__.__name__)

        while True:
            cp.logFromCore(Messages.analyzer_searching, LogTypes.INFO, self.__class__.__name__)
            analyzersFolders =  Misc.lsFolders("./Analyzers")
            for cf in analyzersFolders:
                if Misc.hasKey(self.Analyzers, cf, None) == None:
                    comp = Component(cf, cp)
                    self.Analyzers[cf] = comp

            for c in self.Analyzers:
                comp = self.Analyzers[c]
                comp.load()
            
            sleep(self.CHECKING_TIME)

        cp.logFromCore(Messages.analyzer_stop, LogTypes.INFO, self.__class__.__name__)
    