"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to represent any extensible component
"""
import sys
from os.path import normpath
from multiprocessing import Process
import abc
import hashlib
import Misc
from DataPool import SourceTypes, LogTypes, Messages, Data, Binnacle, CommPool

class Component():
    """ Class to represent any extensible component """

    ME_NAME:str = None
    ME_TYPE:SourceTypes = None
    ME_PATH:str = None
    ME_CONFIG = None
    ME_CONFIG_PATH:str = None
    ME_FILE_CLASS:str = None
    ME_CLASS_NAME:str = None
    ME_ENABLED:bool = False 
    ME_LOADED:bool = False 
    ME_STANDALONE:bool = False 
    CP:CommPool = None
    BC:Binnacle = Binnacle()
    
    Check:str = ''              # Hash of config file
    Thread:Process = None       # Thread of compoment executing
    Running:bool = False        # Shows if component is executing
    Simulating:bool = False     # Flag to control if data is simulated from a file
    SimulatingPath:str = None   # Path to simulating file
    loggingLevel:LogTypes = LogTypes.INFO # Level of logging

    def __init__(self, path="./", cp:CommPool=None):
        """ Build a new component un memory """
        self.ME_PATH = path
        self.CP = cp

    def init_standalone(self, path="./", config=None):
        """ Start the component isolated of system """
        self.ME_PATH = path         # Path of current component
        self.ME_STANDALONE = True   
        if not Misc.existsFile("config.yaml", self.ME_PATH):
            raise ValueError(Messages.config_no_file)

        self.ME_CONFIG_PATH = normpath(self.ME_PATH + "/config.yaml")
        self.ME_CONFIG = Misc.readConfig(self.ME_CONFIG_PATH) if config == None else config
        self.CP = CommPool(self.ME_CONFIG, standAlone=True)

        self.load()

    def load(self, forceLoad:bool=False):
        """ Loads the component """
        self.ME_LOADED = False
        try:            
            if not Misc.existsFile("config.yaml", self.ME_PATH):
                raise ValueError(Messages.config_no_file)
            self.ME_CONFIG_PATH = normpath(self.ME_PATH + "/config.yaml")
            self.ME_CONFIG = Misc.readConfig(self.ME_CONFIG_PATH)
            new_check = hashlib.md5(str(self.ME_CONFIG).encode('utf-8')).hexdigest()

            if new_check == self.Check:
                return

            self.Check = new_check
            
            self.log(Messages.comp_try_start.format(self.ME_PATH), LogTypes.INFO)
            self.ME_NAME = Misc.hasKey(self.ME_CONFIG, 'NAME', self.ME_PATH)
            self.ME_TYPE = SourceTypes.parse(Misc.hasKey(self.ME_CONFIG, 'TYPE', None))
            self.ME_ENABLED = Misc.toBool(Misc.hasKey(self.ME_CONFIG, 'ENABLED', 'False')) 
            
            if self.Thread != None:
                self.Thread.terminate()
                self.Thread = None

            self.log(Messages.comp_change.format(self.ME_PATH, ('reload' if self.ME_ENABLED else 'stoped')), LogTypes.INFO)
            if not self.ME_ENABLED:
                return
            
            self.ME_FILE_CLASS = Misc.hasKey(self.ME_CONFIG, 'FILE_CLASS', None)
            if self.ME_FILE_CLASS == None:
                raise ValueError(Messages.error_file_class)
            self.ME_CLASS_NAME = Misc.hasKey(self.ME_CONFIG, 'CLASS_NAME', None)
            if self.ME_CLASS_NAME == None:
                raise ValueError(Messages.error_class_name)

            self.Simulating = Misc.toBool(Misc.hasKey(self.ME_CONFIG, 'SIMULATING', 'False'))
            self.SimulatingPath = Misc.hasKey(self.ME_CONFIG, 'SIMULATING_PATH', '')
            if self.Simulating:
                self.setSimulatedMode(self.Simulating, self.SimulatingPath)
            
            
            _cls = Misc.importModule(self.ME_PATH, self.ME_FILE_CLASS, self.ME_CLASS_NAME)
            obj = _cls()
            obj.ME_NAME = self.ME_NAME
            obj.ME_TYPE = self.ME_TYPE
            obj.ME_PATH = self.ME_PATH
            obj.ME_CONFIG = self.ME_CONFIG
            obj.ME_CONFIG_PATH = self.ME_CONFIG_PATH
            obj.ME_FILE_CLASS = self.ME_FILE_CLASS
            obj.ME_CLASS_NAME = self.ME_CLASS_NAME
            obj.ME_ENABLED = self.ME_ENABLED
            obj.ME_LOADED = True
            obj.ME_STANDALONE = self.ME_STANDALONE
            obj.CP = self.CP
            obj.BC = self.BC
            obj.Check = self.Check
            obj.Running = self.Running
            obj.Simulating = self.Simulating
            obj.SimulatingPath = self.SimulatingPath
            obj.loggingLevel = self.loggingLevel

            DeviceControllerThread = Process(target=obj.start, args=())
            DeviceControllerThread.start()
            self.Thread = DeviceControllerThread
            
            del _cls, obj
            self.ME_LOADED = True
            self.log(Messages.comp_started.format(self.ME_NAME), LogTypes.INFO)
            print(self.ME_NAME, 'loaded.')
        
        except:
            self.log(Messages.comp_load_error, LogTypes.ERROR)         

    def checkConnection(self):
        """ Verify connection with pool """
        return self.CP.isLive()
    
    def log(self, msg:str, logType:LogTypes, item:str=''): 
        """ Allows send message to Binnacle """
        dataLog = Data()
        dataLog.source_type = self.ME_TYPE
        dataLog.source_name = self.ME_NAME
        dataLog.source_item = item
        dataLog.data =  '{}'.format(msg)
        dataLog.aux = self.__class__.__name__
        if logType.value > LogTypes.WARNING.value:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            dataLog.data +=  ' == {} :: {} :: {} :: {}'.format(exc_obj, exc_type, fname, exc_tb.tb_lineno)
        
        self.BC.logFromComponent(dataLog, logType)
        if not self.ME_STANDALONE:
            self.CP.logFromComponent(dataLog, logType)

    def setLoggingSettings(self, loggingLevel:LogTypes=LogTypes.INFO, loggingFile=None, loggingFormat=None):
        """ set logging configurations """
        self.loggingLevel = loggingLevel
        self.BC.loggingSettings(loggingLevel, loggingFile, loggingFormat)

    def setSimulatedMode(self, simulate:bool, path:str):
        """ Set if the capturing is simulated """
        self.Simulating = simulate
        self.SimulatingPath = path
        self.log(Messages.comp_setSimulateMode.format(self.ME_NAME, str(simulate)), LogTypes.INFO)
        
    @abc.abstractmethod
    def start(self):
        """ Implement me! :: Do anything necessary for start a component. """
        raise ValueError('Implement me! :: Do anything necessary for start a component.')        
    
    def stop(self):
        """ Stop module and getting data """
        self.Running = False
        self.log(Messages.comp_stop.format(self.ME_NAME), LogTypes.WARNING)
    
    def send(self, data:Data):
        """ Send data to pool """
        self.CP.send(data)
    
    def receive(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Returns a list objects type Data from pool """
        if self.Simulating:
            return self.simulateData(dataFilter, limit, lastTime)
        else:
            return self.CP.receive(dataFilter, limit=limit, lastTime=lastTime)

    @abc.abstractmethod
    def showData(self, data:Data):
        """  Implement me! :: To show data if this module start standalone.
        Call init_standalone before start. """
        raise ValueError('Implement me! :: To show data if this module start standalone. Call init_standalone before start.')
    @abc.abstractmethod
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """  Implement me! :: Allows to simulate data if this module start standalone.
        Call init_standalone before start. """
        raise ValueError('Implement me! :: Allows to simulate data if this module start standalone. Call init_standalone before start.')
    
