"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to control all Channels to load in system.
"""

import sys
from os.path import normpath
import logging
from time import sleep
from multiprocessing import Process
import hashlib

import Misc
from DataPool import DataPool

class LoaderChannel:
    """ Class to control all Channels to load in system. """
    
    def __init__(self):
        """ Initialize all variables """
        self.URL = ''               # URL of pool server
        self.channels = []         # List of channels
        self.loggingLevel:int = 0   # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log
    
    def loadChannels(self):
        """ Load all channels in './Channels' folder. 
            Each channel have to be a sub folder and must to have a 'config.yaml' file.
        """
        logging.debug('Searching for new channels...')
        channelsFolders =  Misc.lsFolders("./Channels")
        for cf in channelsFolders:
            if Misc.existsFile("config.yaml", cf):
                try:
                    _pathFile = normpath(cf + "/config.yaml")
                    _config = Misc.readConfig(_pathFile)
                    _enabled = Misc.toBool(str(_config['ENABLED']))
                    _check = hashlib.md5(str(_config).encode('utf-8')).hexdigest()

                    _moduleName = Misc.hasKey(_config, 'MACHINE_NAME', 'No MACHINE_NAME')
                    _className = Misc.hasKey(_config, 'CLASS_NAME', 'No CLASS_NAME')
                    
                    _found = False

                    for cc in range(len(self.channels)):
                        # Check file changes
                        _ctrl = self.channels[cc]
                        if _ctrl["configFile"] == _pathFile:
                            _found = True
                            if _ctrl["check"] != _check:
                                logging.info('Something changed in {}. It will be {}.'.format(_pathFile,
                                    ('reload' if _enabled else 'stoped')))

                                if "thread" in _ctrl and _ctrl["thread"].is_alive():
                                    _ctrl["thread"].terminate()
                                    del _ctrl["thread"]

                                self.channels[cc] = {
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
                        logging.info('There is a new module in {}. {}.'.format(_pathFile,
                            ('It will be Load' if _enabled else 'But is disabled')))
                        self.channels.append({
                                "check": _check,
                                "configFile": _pathFile,
                                "path": cf,
                                "moduleName": _moduleName,
                                "className": _className,
                                "enabled": _enabled,
                                "config" : _config,
                            })
                except:
                    logging.exception('Unexpected error loading channel in folder {} :: {}.'.format(cf, str(sys.exc_info()[0])))

    def send(self):
        """ Start load of all Channels """

        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)
        self.loadChannels()
        for cc in range(len(self.channels)):
            _ctrl = self.channels[cc]
            _cls = None
            if _ctrl["enabled"] and not "thread" in _ctrl:
                """ Load componente and class using config file information """
                logging.info('Starting Channel {}.'.format(_ctrl['moduleName']))
                _cls = Misc.importModule(_ctrl["path"], _ctrl['moduleName'], _ctrl['className'])
                _cls = _cls(_ctrl["config"])
                _cls.URL = self.URL
                _cls.Me_Path = _ctrl["path"]
                _cls.loggingLevel = self.loggingLevel
                _cls.loggingFile = self.loggingFile
                _cls.loggingFormat = self.loggingFormat

                ChannelHARThread = Process(target=_cls.send, args=())
                ChannelHARThread.start()
                del _cls
                logging.info('Channel {} sending message.'.format(_ctrl['moduleName']))                

        logging.info('Sending messages finished.')
