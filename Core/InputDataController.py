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
from os.path import dirname, abspath, exists, split, normpath
import numpy as np
from time import time, sleep
import logging
from multiprocessing import Process, Value
import hashlib
from DataPool import DataPool, Data
import Misc

class InputDataController:
    """ Class to control all data received from device drivers. """
    
    def __init__(self):
        """ Initialize all variables """
        self.URL = ''
        self.controllers = []
        
    def loadControllers(self):
        """ Load all devices controllers in './Controllers' folder. 
            Each controller have to be a sub folder and must to have a 'Config.yaml' file.
        """
        logging.debug('Searching for new device controllers...')
        controllersFolders =  Misc.lsFolders("./Controllers")
        for cf in controllersFolders:
            if Misc.existsFile("Config.yaml", cf):
                _pathFile = normpath(cf + "/Config.yaml")
                _config = Misc.readConfig(_pathFile)
                _check = hashlib.md5(str(_config).encode('utf-8')).hexdigest()
                _found = False

                for cc in range(len(self.controllers)):
                    # Check file changes
                    _ctrl = self.controllers[cc]
                    if _ctrl["configFile"] == _pathFile:
                        _found = True
                        if _ctrl["check"] != _check:
                            logging.info('Something changed in ' + _pathFile + '. It will be reload.')
                            del _ctrl.cls
                            _ctrl = {
                            "check": _check,
                            "configFile": _pathFile,
                            "path": cf,
                            "moduleName": _config['MACHINE_NAME'],
                            "className": _config['CLASS_NAME'],
                            "cls": None,
                            "enabled": bool(_config['MACHINE_NAME']),
                            "sampling": _config['SAMPLING'],
                            "config" : _config,
                        }
                        break

                if not _found:
                    logging.info('There is a new module in ' + _pathFile + '. It will be Load.')
                    self.controllers.append({
                            "check": _check,
                            "configFile": _pathFile,
                            "path": cf,
                            "moduleName": _config['MACHINE_NAME'],
                            "className": _config['CLASS_NAME'],
                            "cls": None,
                            "enabled": bool(_config['MACHINE_NAME']),
                            "sampling": _config['SAMPLING'],
                            "config" : _config,
                        })

    def start(self):

        logging.basicConfig(
            level=logging.INFO,
            #filename='{}.log'.format(str(tm.tm_year) + '%02d' % tm.tm_mon + '%02d' % tm.tm_mday), 
            #filemode='w', 
            format='%(name)s - %(levelname)s - %(message)s')

        while True:
            self.loadControllers()
            for cc in range(len(self.controllers)):
                _ctrl = self.controllers[cc]
                _cls = None
                if _ctrl["enabled"] and _ctrl["cls"] == None: # Ver si el hilo sigue activo
                    """ Load componente and class using config file information
                        path: Path where is the config file
                        configFile: Name of config file. If none load 'config.yaml'.
                    """
                    logging.info('Starting device controller ' + _ctrl['moduleName'] + '.')
                    _cls = Misc.importModule(_ctrl["path"], _ctrl['moduleName'], _ctrl['className'])
                    _ctrl["cls"] = _cls(_ctrl["config"])
                    _ctrl["cls"].sampling = _ctrl["sampling"]
                    _ctrl["cls"].URL = self.URL
                    DeviceControlerThread = Process(target=_ctrl["cls"].start, args=())
                    #DeviceControlerThread.daemon = True
                    DeviceControlerThread.start()
                    logging.info('Device controller '  + _ctrl['moduleName'] + ' started.')
                    
            sleep(30)

        logging.info('Input data controller stoped')

    def newData(self):
        logging.debug('adding data to the pool..')
        dp = DataPool()
        dp.URL = self.URL
        dp.sendData('Artificial', 'Sala', '000111000111')

    def simulate(self):
        for _ in range(1000):
            self.newData()
            sleep(2)

    def imprime(self):
        print('xxx')