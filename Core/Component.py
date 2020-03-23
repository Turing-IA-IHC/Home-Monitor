"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to represent any extensible component
"""
import sys
from os.path import normpath
from multiprocessing import Process
import hashlib
import Misc
from DataPool import SourceTypes, LogTypes, Messages, Data, Binnacle, CommPool

class Component():
    """ Class to represent any extensible component """
    ME_PATH = ''
    ME_TYPE:SourceTypes = None
    ME_NAME:str = ''
    ME_CHECK = ''
    THREAD = None 
    LOADED = False
    STANDALONE = False
    COMMPOOL = None

    def __init__(self, Me_Path="./", commPool:CommPool=None):
        self.ME_PATH = Me_Path
        self.COMMPOOL = commPool

    def load(self, forceLoad:bool=False):
        self.LOADED = False
        try:
            if not Misc.existsFile("config.yaml", self.ME_PATH):
                raise ValueError(Messages.config_no_file)

            self.CONFIG_PATH = normpath(self.ME_PATH + "/config.yaml")
            self.CONFIG = Misc.readConfig(self.CONFIG_PATH)

            if self.THREAD == None or not self.THREAD.is_alive():
                forceLoad = True

            if not forceLoad:
                if self.ME_CHECK == hashlib.md5(str(self.CONFIG).encode('utf-8')).hexdigest():
                    return

            self.COMMPOOL.logFromCore(Messages.comp_try_start.format(self.ME_PATH), LogTypes.INFO, self.__class__.__name__)
            self.ME_CHECK = hashlib.md5(str(self.CONFIG).encode('utf-8')).hexdigest()
            self.ENABLED = Misc.toBool(Misc.hasKey(self.CONFIG, 'ENABLED', 'False'))
            self.ME_TYPE = SourceTypes.parse(Misc.hasKey(self.CONFIG, 'TYPE', None))
            self.ME_NAME = Misc.hasKey(self.CONFIG, 'NAME', self.ME_PATH)
            
            self.FILE_CLASS = Misc.hasKey(self.CONFIG, 'FILE_CLASS', None)
            if self.FILE_CLASS == None:
                raise ValueError(Messages.error_file_class)
            self.CLASS_NAME = Misc.hasKey(self.CONFIG, 'CLASS_NAME', None)
            if self.CLASS_NAME == None:
                raise ValueError(Messages.error_class_name)

            self.COMMPOOL.logFromCore(Messages.comp_change.format(self.ME_PATH, ('reload' if self.ENABLED else 'stoped')), LogTypes.INFO, self.__class__.__name__)
            
            if self.THREAD != None:
                self.THREAD.terminate()
                self.THREAD = None

            if not self.ENABLED:                
                return
            
            _cls = Misc.importModule(self.ME_PATH, self.FILE_CLASS, self.CLASS_NAME)
            obj = _cls()
            obj.CONFIG = self.CONFIG
            obj.ME_PATH = self.ME_PATH
            obj.ME_TYPE = self.ME_TYPE
            obj.ME_NAME = self.ME_NAME
            obj.COMMPOOL = self.COMMPOOL
            obj.STANDALONE = self.STANDALONE

            DeviceControllerThread = Process(target=obj.start, args=())
            DeviceControllerThread.start()
            self.THREAD = DeviceControllerThread
            
            del _cls, obj
            self.LOADED = True
            self.COMMPOOL.logFromCore(Messages.controller_started.format(self.ME_NAME), LogTypes.INFO, self.__class__.__name__)
        
        except:
            dataE = Data()
            dataE.source_type = self.ME_TYPE
            dataE.source_name = self.ME_NAME
            dataE.source_item = ''
            dataE.data = self.COMMPOOL.errorDetail(Messages.comp_load_error)
            dataE.aux = self.__class__.__name__
            self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)            

    def init_standalone(self, Me_Path="./", config=None, autoload:bool=True):
        Binnacle().loggingSettings(LogTypes.INFO, None, '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ME_PATH = Me_Path      # Path of current component
        self.STANDALONE = True      # If a child start in standalone
        if not Misc.existsFile("config.yaml", self.ME_PATH):
            raise ValueError(Messages.config_no_file)

        self.CONFIG_PATH = normpath(self.ME_PATH + "/config.yaml")
        self.CONFIG = Misc.readConfig(self.CONFIG_PATH) if config == None else config
        self.COMMPOOL = CommPool(self.CONFIG, standAlone=True)
        if(autoload):
            self.load()

    def checkConnection(self):
        """ Verify connection with pool """
        return self.COMMPOOL.isLive()

    def log(self, data, logType):
        """ Allows send message to Binnacle """
        self.COMMPOOL.log_data(data, logType)
