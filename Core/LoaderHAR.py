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
from time import time, sleep, ctime
import logging
from multiprocessing import Process, Value
import hashlib
from DataPool import DataPool, Data
import Misc

class LoaderHAR:
    """ Class to control all HAR components to load in system. """
    
    def __init__(self):
        """ Initialize all variables """
        self.URL = ''               # URL of pool server
        self.classifiers = []       # List of classifiers
        self.loggingLevel = None    # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log
    
    def loadClassifiers(self):
        """ Load all classifiers in './HAR' folder. 
            Each classifier have to be a sub folder and must to have a 'config.yaml' file.
        """
        logging.debug('Searching for new device classifiers...')
        classifiersFolders =  Misc.lsFolders("./HAR")
        for cf in classifiersFolders:
            if Misc.existsFile("config.yaml", cf):
                try:
                    _pathFile = normpath(cf + "/config.yaml")
                    _config = Misc.readConfig(_pathFile)
                    _enabled = Misc.toBool(str(_config['ENABLED']))
                    _moduleName = _config['MACHINE_NAME'] if _enabled else Misc.hasKey(_config, 'MACHINE_NAME')
                    _className = _config['CLASS_NAME'] if _enabled else Misc.hasKey(_config, 'CLASS_NAME')
                    
                    _check = hashlib.md5(str(_config).encode('utf-8')).hexdigest()
                    _found = False

                    for cc in range(len(self.classifiers)):
                        # Check file changes
                        _ctrl = self.classifiers[cc]
                        if _ctrl["configFile"] == _pathFile:
                            _found = True
                            if _ctrl["check"] != _check:
                                logging.info('Something changed in ' + _pathFile +
                                    ('. It will be reload.' if _enabled else '. It will be stoped.'))

                                if "thread" in _ctrl and _ctrl["thread"].is_alive():
                                    _ctrl["thread"].terminate()
                                    del _ctrl["thread"]

                                self.classifiers[cc] = {
                                "check": _check,
                                "configFile": _pathFile,
                                "path": cf,
                                "moduleName": _moduleName,
                                "className": _className,
                                "enabled": _enabled,
                                "config" : _config,
                            }
                            break

                    if not _found:
                        logging.info('There is a new module in ' + _pathFile + 
                            ('. It will be Load.' if _enabled else '. But is disabled.'))
                        self.classifiers.append({
                                "check": _check,
                                "configFile": _pathFile,
                                "path": cf,
                                "moduleName": _moduleName,
                                "className": _className,
                                "enabled": _enabled,
                                "config" : _config,
                            })

                except:
                    logging.exception("Unexpected error loading HAR classifier in folder " + cf + " : " + str(sys.exc_info()[0]))

    def start(self):
        """ Start load of all HAR Classifiers """

        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)

        dp = DataPool()
        dp.URL = self.URL

        TimeDiff = 999999
        logging.info('Trying to connect to Pool from HAR Loader ...')
        err = ''
        for _ in range(10):
            try:
                TimeDiff = dp.getTimeDiff()
                logging.info('Time in pool server: ' + ctime(time() + TimeDiff) + ' Diference: ' + str(TimeDiff))
                break
            except:
                err = str(sys.exc_info()[0])
                sleep(1)

        if TimeDiff == 999999:
            logging.error('Failed to connect to ' + dp.URL + ' :: Err: ' + err)
            logging.error('Press control + c to terminate.')
            return

        while True:
            self.loadClassifiers()
            for cc in range(len(self.classifiers)):
                _ctrl = self.classifiers[cc]
                #_cls = None
                #if _ctrl["enabled"] and not "thread" in _ctrl:
                #    """ Load componente and class using config file information """
                #    logging.info('Starting HAR classifiers ' + _ctrl['moduleName'] + '.')
                #    _cls = Misc.importModule(_ctrl["path"], _ctrl['moduleName'], _ctrl['className'])
                #    _cls = _cls(_ctrl["config"])
                #    _cls.URL = self.URL
                #    ClassifierHARThread = Process(target=_cls.start, args=())
                #    #ClassifierHARThread.daemon = True
                #    ClassifierHARThread.start()
                #    _ctrl["thread"] = ClassifierHARThread
                #    del _cls
                #    logging.info('HAR classifier '  + _ctrl['moduleName'] + ' started.')
                    
            sleep(30)

        logging.info('Loader HAR stoped')
