"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly recognizersmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Main class to start whole system
"""

__version__ = "1.0.0"

import sys
import logging
from multiprocessing import Process, Value
from time import time, sleep, gmtime
from os.path import dirname, abspath, exists, split, normpath

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from DataPool import SourceTypes, LogTypes, Messages, PoolStates, Data, Binnacle, DataPool, CommPool

from LoaderController import LoaderController
from LoaderRecognizer import LoaderRecognizer
from LoaderAnalyzer import LoaderAnalyzer

class main():
    """ Main class to start whole system """
    def __init__(self, components:int, vars=[]):
        """ 
            Start whole system and all sub systems.
            components is a number between 1 and 15.
            components represents a binary of 4 positions being:
                components[0] => DataPool   : Example 1
                components[1] => Controllers: Example 2
                components[2] => Recognizers: Exmaple 4
                components[3] => Analyzers  : Exmaple 8
            To load all sub system set 15 to 'components' parameter.
            It is possible to combine the starting of some subsystems, for example, 
            to load DataPool and recognizer only set 5 to 'components' parameter.
            Vars: Set any config var using form VAR=VALUE
        """
        print('\n')
        print('=========================='.center(50, "="))
        print(' Wellcome to Home-Monitor '.center(50, "=") )
        print(' Version: {} '.format(__version__).center(50, " "))
        print('=========================='.center(50, "="))
        print('')

        # Verify components to load param
        if components < 1 or components > 15:
            Binnacle().logFromCore(Messages.nothing_to_load, LogTypes.WARNING, self.__class__.__name__)
            return
        
        # Loading configuration file
        self.CONFIG_FILE = normpath(abspath('.') + "/config.yaml")
        if not exists(self.CONFIG_FILE):
            Binnacle().loggingSettings(LogTypes.ERROR, '', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            Binnacle().logFromCore(Messages.config_no_file + self.CONFIG_FILE, LogTypes.ERROR, self.__class__.__name__)
            return
        self.CONFIG = Misc.readConfig(self.CONFIG_FILE)

        
        # Replacing config vars
        for v in vars:
            vParam = str(v).split('=')
            if len(vParam) > 0:
                t = type(Misc.hasKey(self.CONFIG, vParam[0], ''))
                self.CONFIG[vParam[0]] = t(vParam[1])
        Misc.showConfig(self.CONFIG)

        # Logging Configuration
        tm = gmtime()
        if Misc.toBool(Misc.hasKey(self.CONFIG, 'LOGGING_TO_FILE', 'False')):
            loggingFile = '{}.log'.format(str(tm.tm_year) + '%02d' % tm.tm_mon + '%02d' % tm.tm_mday) 
            loggingFile = normpath(Misc.hasKey(self.CONFIG,'LOGGING_PATH' + "/", "./") + loggingFile)
            self.CONFIG['LOGGING_FILE'] = loggingFile
        Binnacle().loggingConf(self.CONFIG)

        #if components > 1:
        self.commPool = CommPool(self.CONFIG)

        # Define which component should be started
        toStart = "%04d"% int(str(bin(components)).replace("0b",""))
        print('')
        Binnacle().logFromCore(Messages.system_start, LogTypes.INFO, self.__class__.__name__)
        Binnacle().logFromCore(Messages.system_start_components + toStart, LogTypes.INFO, self.__class__.__name__)
        print('')

        self.must_start_pool = toStart[3] == '1'
        self.must_start_controllers = toStart[2] == '1'
        self.must_start_recognizers = toStart[1] == '1'
        self.must_start_analyzers = toStart[0] == '1'

        if self.must_start_pool:
            self.start_pool()
        if self.must_start_controllers:
            self.start_controllers()        
        if self.must_start_recognizers:
            self.start_recognizers()
        if self.must_start_analyzers:
            self.start_analyzers()

        self.heart_beat()

    def heart_beat(self):
        """ Keep system running """
        Binnacle().logFromCore(Messages.system_start_heart_beat, LogTypes.INFO, self.__class__.__name__)
        while True:
            try:
                """ Section to control the execution of the pool """
                if self.must_start_pool and not self.poolThread.is_alive():
                    Binnacle().logFromCore(Messages.system_pool_restart, LogTypes.INFO, self.__class__.__name__)
                    self.start_pool()
                
                if self.must_start_pool:
                    self.commPool.sendCommand('pop')
                    print(' \t {} data received.'.format(self.commPool.count()))

            except:
                message = Binnacle().errorDetail(Messages.system_pool_error)
                Binnacle().logFromCore(message, LogTypes.ERROR, self.__class__.__name__) 
            
            try:
                """ Section to control the execution of the input data """
                if self.must_start_controllers and not self.inputDataThread.is_alive():
                    self.commPool.logFromCore(Messages.system_controllers_restart, LogTypes.INFO, self.__class__.__name__)
                    self.start_controllers()
            except:
                message = Binnacle().errorDetail(Messages.system_controllers_error)
                self.commPool.logFromCore(message, LogTypes.ERROR, self.__class__.__name__)
                  
            try:
                """ Section to control the execution of the recognizers """
                if self.must_start_recognizers and not self.loaderRecognizersThread.is_alive():
                    self.commPool.logFromCore(Messages.system_recognizers_restart, LogTypes.INFO, self.__class__.__name__)
                    self.start_recognizers()
            except:
                message = Binnacle().errorDetail(Messages.system_recognizers_error)
                self.commPool.logFromCore(message, LogTypes.ERROR, self.__class__.__name__)
                  
            try:
                """ Section to control the execution of the lanalyzers """
                if self.must_start_analyzers and not self.loaderAnalyzersThread.is_alive():
                    self.commPool.logFromCore(Messages.system_analyzers_restart, LogTypes.INFO, self.__class__.__name__)
                    self.start_recognizers()
            except:
                message = Binnacle().errorDetail(Messages.system_analyzers_error)
                self.commPool.logFromCore(message, LogTypes.ERROR, self.__class__.__name__)

            sleep(Misc.hasKey(self.CONFIG, 'CHECKING_TIME', 30))

    def start_pool(self):
        """ Start data pool """
        Binnacle().logFromCore(Messages.system_pool_start + self.CONFIG['URL_BASE'], LogTypes.INFO, self.__class__.__name__)
        pool = DataPool()
        pool.initialize(self.CONFIG)
        self.poolThread = Process(target=pool.start, args=())
        self.poolThread.daemon = True
        self.poolThread.start()
        del pool
        sleep(2)
        Binnacle().logFromCore(Messages.system_pool_started + self.CONFIG['URL_BASE'], LogTypes.INFO, self.__class__.__name__)

    def start_controllers(self):
        """ Start input data controller and all device controllers """
        self.commPool.logFromCore(Messages.system_controllers_start + self.CONFIG['URL_BASE'], LogTypes.INFO, self.__class__.__name__)
        loaderController = LoaderController(self.CONFIG)
        self.inputDataThread = Process(target=loaderController.start, args=())
        self.inputDataThread.start()
        del loaderController
        sleep(2)
        self.commPool.logFromCore(Messages.system_controllers_started + self.CONFIG['URL_BASE'], LogTypes.INFO, self.__class__.__name__)
                
    def start_recognizers(self):
        """ Start loader of Recognizers and all recognizers """
        self.commPool.logFromCore(Messages.system_recognizers_start + self.CONFIG['URL_BASE'], LogTypes.INFO, self.__class__.__name__)
        loaderRecognizer = LoaderRecognizer(self.CONFIG)
        self.loaderRecognizersThread = Process(target=loaderRecognizer.start, args=())
        self.loaderRecognizersThread.start()
        del loaderRecognizer
        sleep(2)
        self.commPool.logFromCore(Messages.system_recognizers_started + self.CONFIG['URL_BASE'], LogTypes.INFO, self.__class__.__name__)
        
    def start_analyzers(self):
        """ Start loader of Analyzers and all all analyzers """
        self.commPool.logFromCore(Messages.system_analyzers_start + self.CONFIG['URL_BASE'], LogTypes.INFO, self.__class__.__name__)
        loaderAnalyzer = LoaderAnalyzer(self.CONFIG)
        self.loaderAnalyzersThread = Process(target=loaderAnalyzer.start, args=())
        self.loaderAnalyzersThread.start()
        del loaderAnalyzer
        sleep(2)
        self.commPool.logFromCore(Messages.system_analyzers_started + self.CONFIG['URL_BASE'], LogTypes.INFO, self.__class__.__name__)
        
if __name__ == "__main__":
    components = 0   # Message no one component
    components = 1   # Only pool
    components = 2   # Only load controller
    components = 3   # Pool + load controller
    #components = 4  # Only Recognizers
    components = 5  # Pool + Recognizers
    #components = 6  # Load controller + Recognizers
    #components = 7  # Pool + Load controller + Recognizers
    #components = 8  # Only Adnormal events
    #components = 15 # All components

    components = 4
    m = main(components)
    
    