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

import logging
from multiprocessing import Process, Value
from time import time, sleep, gmtime
from os.path import dirname, abspath, exists, split, normpath
import sys

import Misc
from DataPool import DataPool
from InputDataController import InputDataController
from LoaderHAR import LoaderHAR

class main():
    """ Main class to start whole system """
    def __init__(self, components):
        print('\n')
        print('=========================='.center(50, "="))
        print(' Wellcome to Home-Monitor '.center(50, "=") )
        print(' Version: {}      '.format(__version__).center(50, " "))
        print('=========================='.center(50, "="))
        print('')

        toStart = "%04d"% int(str(bin(components)).replace("0b",""))

        self.CONFIG_FILE = normpath(abspath('.') + "/config.yaml")
        if not exists(self.CONFIG_FILE):
            logging.exception('Config file does not exits: ' + self.CONFIG_FILE)
            return

        self.CONFIG = Misc.readConfig(self.CONFIG_FILE)
        Misc.showConfig(self.CONFIG)

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
        self.must_start_devices = toStart[2] == '1'
        self.must_start_har = toStart[1] == '1'
        self.must_start_events = toStart[0] == '1'

        if self.must_start_pool:
            self.pool:DataPool = None
            self.start_pool()

        if self.must_start_devices:
            self.inputData:InputDataController = None
            self.start_devices()

        if self.must_start_har:
            self.loaderHAR:LoaderHAR = None
            self.start_classifiers()

        print('')
        self.heart_beat()
        
    def heart_beat(self):
        logging.info('All sub systems will keep alive ...')

        while True:
            try:
                """ Section to control the execution of the pool """
                if self.must_start_pool:
                    if self.pool == None or not self.poolThread.is_alive():
                        logging.warning('Pool service is death. System auto start it.')
                        self.start_pool()
                    #logging.info('Pool service is living. Has ' + str(self.pool.count()) + ' data')
            except:
                logging.exception("Unexpected error checking pool: " + str(sys.exc_info()[0]))

            try:
                """ Section to control the execution of the input data """
                if self.must_start_devices:
                    if self.inputData == None or not self.inputDataThread.is_alive():
                        logging.warning('Input data service is death. System auto start it.')
                        self.start_devices()
                    #else:
                    #    print('\t ++ inputData: Running')
                    #logging.debug('Controllers loaded: ' + str(len(self.inputData.controllers)))
            except:
                logging.exception("Unexpected error checking input data controller: " + str(sys.exc_info()[0]))

            try:
                """ Section to control the execution of the HAR Loader """
                if self.must_start_har:
                    if self.loaderHAR == None or not self.loaderHARThread.is_alive():
                        logging.warning('HAR Loader service is death. System auto start it.')
                        self.start_classifiers()
                    #logging.debug('Classifiers loaded: ' + str(len(self.loaderHAR.controllers)))
            except:
                logging.exception("Unexpected error checking HAR Loader: " + str(sys.exc_info()[0]))

            #try:
            #    dp = DataPool()
            #    dp.URL = self.CONFIG['POOL_PATH']
            #    #CamController/Gray
            #    g = dp.getData(controller = 'CamController/Gray', device = 'Trasera', limit = 1)
            #    if len(g) > 1 :
            #        from cv2 import cv2
            #        cv2.imwrite('imagen.png', g[-1]['data'])
            #        #print('id: "{}", Controller: "{}", Device: "{}"'.format(g[-1]['id'], g[-1]['controller'], g[-1]['device']))

            #except:
            #    logging.exception("Unexpected readding data from pool: " + str(sys.exc_info()[0]))
            #
            sleep(3)

    def start_pool(self):
        """ Start data pool """

        if self.pool == None:
            self.pool = DataPool()
        
        self.pool.URL = self.CONFIG['POOL_PATH']
        self.pool.loggingLevel = self.CONFIG['LOGGING_LEVEL']
        self.pool.loggingFormat = self.CONFIG['LOGGING_FORMAT']
        self.pool.loggingFile = self.loggingFile

        logging.info('Starting pool in ' + self.pool.URL)
        self.poolThread = Process(target=self.pool.start, args=())
        self.poolThread.daemon = True
        self.poolThread.start()
        sleep(2)
        logging.info('Pool started.')

    def start_devices(self):
        """ Start input data controller and all device controllers """

        if self.inputData == None:
            self.inputData = InputDataController()
        
        self.inputData.URL = self.CONFIG['POOL_PATH']
        self.inputData.loggingLevel = self.CONFIG['LOGGING_LEVEL']
        self.inputData.loggingFormat = self.CONFIG['LOGGING_FORMAT']
        self.inputData.loggingFile = self.loggingFile

        logging.info('Starting input data controllers with pool in ' + self.inputData.URL)
        self.inputDataThread = Process(target=self.inputData.start, args=())
        #self.inputDataThread.daemon = True
        self.inputDataThread.start()
        sleep(2)
        logging.info('Input data controller started.')

    def start_classifiers(self):
        """ Start loader HAR and all classifiers HAR """

        if self.loaderHAR == None:
            self.loaderHAR = LoaderHAR()
        
        self.loaderHAR.URL = self.CONFIG['POOL_PATH']
        self.loaderHAR.loggingLevel = self.CONFIG['LOGGING_LEVEL']
        self.loaderHAR.loggingFormat = self.CONFIG['LOGGING_FORMAT']
        self.loaderHAR.loggingFile = self.loggingFile

        logging.info('Starting Loader HAR with pool in ' + self.loaderHAR.URL)
        self.loaderHARThread = Process(target=self.loaderHAR.start, args=())
        #self.loaderHARThread.daemon = True
        self.loaderHARThread.start()
        sleep(2)
        logging.info('Loader HAR started.')

if __name__ == "__main__":
    components = 0   # Message no one component
    components = 1   # Only pool
    components = 2   # Only input data controller
    components = 3   # Pool + input data controller
    #components = 4  # Only classifiers HAR
    #components = 5  # Pool + Classifiers HAR
    #components = 6  # Input data controller + Classifiers HAR
    components = 7  # Pool + input data controller + classifiers HAR
    #components = 8  # Only Adnormal events
    #components = 15 # All components

    m = main(components)