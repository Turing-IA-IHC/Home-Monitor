"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

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
from DataPool import DataPool, SourceType
from LoaderController import LoaderController
from LoaderHAR import LoaderHAR
from LoaderAnalyzer import LoaderAnalyzer

class main():
    """ Main class to start whole system """
    def __init__(self, components):
        print('\n')
        print('=========================='.center(50, "="))
        print(' Wellcome to Home-Monitor '.center(50, "=") )
        print(' Version: {}      '.format(__version__).center(50, " "))
        print('=========================='.center(50, "="))
        print('')

        # Define which component should be started
        toStart = "%04d"% int(str(bin(components)).replace("0b",""))
        
        # Loading configuration file
        self.CONFIG_FILE = normpath(abspath('.') + "/config.yaml")
        if not exists(self.CONFIG_FILE):
            logging.exception('Config file does not exits: ' + self.CONFIG_FILE)
            return
        self.CONFIG = Misc.readConfig(self.CONFIG_FILE)
        Misc.showConfig(self.CONFIG)

        # Logging Configuration
        tm = gmtime()
        self.loggingFile = ""
        if Misc.toBool(str(self.CONFIG['LOGGING_TO_FILE'])):
            self.loggingFile = '{}.log'.format(str(tm.tm_year) + '%02d' % tm.tm_mon + '%02d' % tm.tm_mday) 
            self.loggingFile = normpath(self.CONFIG['LOGGING_TO_FILE'] + "/" + self.loggingFile)
            print('Log File:', self.loggingFile)
        Misc.loggingConf(self.CONFIG['LOGGING_LEVEL'], self.loggingFile, self.CONFIG['LOGGING_FORMAT'])

        print('')
        logging.info('Starting the magic ...')
        logging.info('Starting components with comand: ' + toStart)
        print('')

        self.must_start_pool = toStart[3] == '1'
        self.must_start_controllers = toStart[2] == '1'
        self.must_start_har = toStart[1] == '1'
        self.must_start_analyzers = toStart[0] == '1'

        if self.must_start_pool:
            self.start_pool()

        if self.must_start_controllers:
            self.start_controllers()

        if self.must_start_har:
            self.start_classifiers()

        if self.must_start_analyzers:
            self.start_analyzers()

        print('')
        self.heart_beat()
        
    def heart_beat(self):
        logging.info('All sub systems will keep alive ...')

        while True:
            try:
                """ Section to control the execution of the pool """
                if self.must_start_pool:
                    if not self.poolThread.is_alive():
                        logging.warning('Pool service is death. System auto start it.')
                        self.start_pool()
                    #pool = DataPool()
                    #pool.URL = self.CONFIG['POOL_PATH']
                    #logging.info('Pool service is living. Has ' + str(pool.count()) + ' data')
            except:
                logging.exception('Unexpected error checking pool: {}.'.format(str(sys.exc_info()[0])))

            try:
                """ Section to control the execution of the input data """
                if self.must_start_controllers:
                    if not self.inputDataThread.is_alive():
                        logging.warning('Controllers loader service is death. System auto start it.')
                        self.start_controllers()
            except:
                logging.exception('Unexpected error checking loader of controllers: {}.'.format(str(sys.exc_info()[0])))

            try:
                """ Section to control the execution of the HAR Loader """
                if self.must_start_har:
                    if not self.loaderHARThread.is_alive():
                        logging.warning('HAR loader service is death. System auto start it.')
                        self.start_classifiers()
            except:
                logging.exception('Unexpected error checking loader of HAR: {}'.format(str(sys.exc_info()[0])))

            try:
                """ Section to control the execution of the HAR Loader """
                if self.must_start_analyzers:
                    if not self.loaderAnalyzerThread.is_alive():
                        logging.warning('Analyzer loader service is death. System auto start it.')
                        self.start_analyzers()
            except:
                logging.exception('Unexpected error checking loader of Analyzers: {}'.format(str(sys.exc_info()[0])))

            """ # Borrar solo para ver las imágenes capturadas
            try:
                dp = DataPool()
                dp.URL = self.CONFIG['POOL_PATH']
                #CamController/Gray
                #, device = 'Trasera'
                g = dp.getData(controller = 'CamController/Gray', limit = 1)
                if len(g) > 1 :
                    from cv2 import cv2
                    cv2.imwrite('imagen.png', g[-1]['data'])
                    #print('id: "{}", Controller: "{}", Device: "{}"'.format(g[-1]['id'], g[-1]['controller'], g[-1]['device']))
            except:
                logging.exception('Unexpected readding data from pool. :: Error: {}.'.format(str(sys.exc_info()[0])))
            """
            """ # Borrar solo para ver clases capturadas
            try:
                dp = DataPool()
                dp.URL = self.CONFIG['POOL_PATH']
                g = dp.getData(source=SourceType.CLASSIFIER, limit=-1)
                if len(g) > 1 :
                    print('id: "{}", frase: "{}"'.format(g[-1]['id'], g[-1]['data']))
            except:
                logging.exception('Unexpected readding data from pool. :: Error: {}.'.format(str(sys.exc_info()[0])))
            """

            sleep(3)

    def start_pool(self):
        """ Start data pool """

        pool = DataPool()
        pool.URL = self.CONFIG['POOL_PATH']
        pool.loggingLevel = int(self.CONFIG['LOGGING_LEVEL'])
        pool.loggingFormat = self.CONFIG['LOGGING_FORMAT']
        pool.loggingFile = self.loggingFile

        logging.info('Starting pool in ' + pool.URL)
        self.poolThread = Process(target=pool.start, args=())
        self.poolThread.daemon = True
        self.poolThread.start()
        del pool
        sleep(2)
        logging.info('Pool started.')

    def start_controllers(self):
        """ Start input data controller and all device controllers """

        loaderController = LoaderController()        
        loaderController.URL = self.CONFIG['POOL_PATH']
        loaderController.loggingLevel = int(self.CONFIG['LOGGING_LEVEL'])
        loaderController.loggingFormat = self.CONFIG['LOGGING_FORMAT']
        loaderController.loggingFile = self.loggingFile

        logging.info('Starting loader of controllers with pool in ' + loaderController.URL)
        self.inputDataThread = Process(target=loaderController.start, args=())
        self.inputDataThread.start()
        del loaderController
        sleep(2)
        logging.info('Loader of controllers started.')

    def start_classifiers(self):
        """ Start loader of HAR and all classifiers HAR """

        loaderHAR = LoaderHAR()        
        loaderHAR.URL = self.CONFIG['POOL_PATH']
        loaderHAR.loggingLevel = self.CONFIG['LOGGING_LEVEL']
        loaderHAR.loggingFormat = self.CONFIG['LOGGING_FORMAT']
        loaderHAR.loggingFile = self.loggingFile

        logging.info('Starting Loader HAR with pool in ' + loaderHAR.URL)
        self.loaderHARThread = Process(target=loaderHAR.start, args=())
        self.loaderHARThread.start()
        del loaderHAR
        sleep(2)
        logging.info('Loader HAR started.')

    def start_analyzers(self):
        """ Start loader of Analyzers """

        loaderAnalyzer = LoaderAnalyzer()        
        loaderAnalyzer.URL = self.CONFIG['EVENT_PATH']
        loaderAnalyzer.loggingLevel = self.CONFIG['LOGGING_LEVEL']
        loaderAnalyzer.loggingFormat = self.CONFIG['LOGGING_FORMAT']
        loaderAnalyzer.loggingFile = self.loggingFile

        logging.info('Starting Loader Analyzer with pool in ' + loaderAnalyzer.URL)
        self.loaderAnalyzerThread = Process(target=loaderAnalyzer.start, args=())
        self.loaderAnalyzerThread.start()
        del loaderAnalyzer
        sleep(2)
        logging.info('Loader Analyzer started.')

if __name__ == "__main__":
    components = 0   # Message no one component
    components = 1   # Only pool
    components = 2   # Only load controller
    components = 3   # Pool + load controller
    #components = 4  # Only classifiers HAR
    #components = 5  # Pool + Classifiers HAR
    #components = 6  # Load controller + Classifiers HAR
    components = 7   # Pool + Load controller + classifiers HAR
    #components = 8  # Only Adnormal events
    components = 15 # All components

    m = main(components)
    
    