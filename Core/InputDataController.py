"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to control all data received from device drivers.
"""
import sys
import numpy as np
from time import time, sleep
from DataPool import DataPool, Data
import Misc
from Component import Component

class InputDataController:
    """ Class to control all data received from device drivers. """
    
    def __init__(self):
        """ Initialize all variables """
        self.URL = ''
        self.controllers = []

    def loadControllers(self):
        """ Load all devices controllers in './Controllers' folder. 
            Each controller have to be a sub folder and must have a 'Config.yaml' file.
        """
        controllersFolders =  Misc.lsFolders("./Controllers")
        for cf in controllersFolders:
            if Misc.existsFile('Config.yaml', cf):
                ctl = Component()
                ctl.createFromConfigFile(cf)
                self.controllers.append(ctl)
    
    def start(self):
        print('Url pool api in ' + self.URL)
        print('Starting controllers')
        for ctl in self.controllers:            
            #TODO: Obtener el ID asignado
            some_object = ctl.cls(ctl.Config, None)
            some_object.imprime()
            



    def newData(self):
        print('adding data to the pool..')
        dp = DataPool()
        dp.URL = self.URL
        dp.sendData('Artificial', '000111000111')

    def simulate(self):
        for _ in range(1000):
            self.newData()
            sleep(2)

    def imprime(self):
        print('xxx')