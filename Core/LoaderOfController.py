"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to load all device controllers.
"""

import sys
from os.path import normpath
from time import sleep
from multiprocessing import Process
import hashlib

import Misc
from Component import Component
from DataPool import LogTypes, Messages, CommPool
from DeviceController import DeviceController

class LoaderOfController:
    """ Class to load all device controllers. """

    def __init__(self, config):
        """ Initialize all variables """
        self.CONFIG = config
        self.CHECKING_TIME = int(Misc.hasKey(self.CONFIG, 'CHECKING_TIME', 10)) # Time in seconds to check service availability
        self.URL = self.CONFIG['URL_BASE']  # URL of pool server TODO: URL_POOL
        self.controllers = {}               # List of controllers TODO: Controllers Variables en nuscula primera mayus
    
    def start(self):
        """ Start load of all device controllers """
        cp = CommPool(self.CONFIG, preferred_url=CommPool.URL_TICKETS)
        cp.logFromCore(Messages.system_controllers_connect.format(cp.URL_BASE), LogTypes.INFO, self.__class__.__name__)

        while True:
            #cp.logFromCore(Messages.controller_searching, LogTypes.DEBUG, self.__class__.__name__)
            controllersFolders =  Misc.lsFolders("./Controllers")
            for cf in controllersFolders:
                if Misc.hasKey(self.controllers, cf, None) == None:
                    comp = Component(cf, cp)
                    self.controllers[cf] = comp

            for c in self.controllers:
                comp = self.controllers[c]
                comp.load()
            
            sleep(self.CHECKING_TIME)

        cp.logFromCore(Messages.controller_stop, LogTypes.INFO, self.__class__.__name__)
        