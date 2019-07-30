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
from InputDataController import InputDataController
from DataPool import DataPool

class main():
    """ Main class to start whole system """
    def __init__(self, components):
        print('\n')
        print('=========================='.center(50, "="))
        print(' Wellcome to Home-Monitor '.center(50, "=") )
        print(' Version: {}      '.format(__version__).center(50, " "))
        print('=========================='.center(50, "="))
        print('\n')

        toStart = "%04d"% int(str(bin(components)).replace("0b",""))
        logging.info('Starting components with comand: ' + toStart)

        self.CONFIG_FILE = normpath(abspath('.') + "/Config.yaml")
        if not exists(self.CONFIG_FILE):
            logging.exception('Config file does not exits: ' + self.CONFIG_FILE)
            return

        self.CONFIG = Misc.readConfig(self.CONFIG_FILE)
        Misc.showConfig(self.CONFIG)
        print('')

        self.must_start_pool = toStart[2] == '1'
        self.must_start_devices = toStart[1] == '1'

        if toStart[3] == '1':
            print('Starting event controllers ...')

        if self.must_start_pool:
            self.pool:DataPool = None
            self.start_pool()

        if self.must_start_devices:
            self.inputData:InputDataController = None
            self.start_devices()

        if toStart[0] == '1':
            print('Starting har controllers ...')

        print('')
        self.heart_beat()
        
    def heart_beat(self):
        logging.info('Starting the magic ...')

        while True:
            try:
                """ Section to control the execution of the pool """
                if self.must_start_pool:
                    if not self.pool.isLive():
                        logging.warning('Pool service is death. System auto start it.')
                        self.start_pool()
                    logging.debug('Pool service is living. Has ' + str(self.pool.count()) + ' data')
            except:
                logging.exception("Unexpected error checking pool: " + str(sys.exc_info()[0]))

            try:
                """ Section to control the execution of the input data """
                if self.must_start_devices:
                    if self.inputData == None:
                        logging.warning('input data service is death. System auto start it.')
                        self.start_devices()
                    logging.debug('Controllers loaded: ' + str(len(self.inputData.controllers)))
            except:
                logging.exception("Unexpected error checking input data controller: " + str(sys.exc_info()[0]))

            sleep(3)

    def start_pool(self):
        """ Start data pool """

        if self.pool == None:
            self.pool = DataPool()
        
        self.pool.URL = self.CONFIG['POOL_PATH']

        logging.info('Starting pool in ' + self.pool.URL)
        inputDataThread = Process(target=self.pool.start, args=())
        inputDataThread.daemon = True
        inputDataThread.start()
        logging.info('Pool started.')

    def start_devices(self):
        """ Start input data controller and all device controllers """

        if self.inputData == None:
            self.inputData = InputDataController()
        
        self.inputData.URL = self.CONFIG['POOL_PATH']

        logging.info('Starting input data controllers with pool in ' + self.inputData.URL)
        inputDataThread = Process(target=self.inputData.start, args=())
        #inputDataThread.daemon = True
        inputDataThread.start()
        logging.info('Input data controller started.')

if __name__ == "__main__":
    components = 0 # Message no one controller
    components = 1 # Only events controller
    components = 2 # Only pool
    #components = 3 # events controller + pool
    components = 4 # Only input data controller
    #components = 5 # events controller + input data controller
    components = 6 # pool + input data controller
    #components = 7 # events controller + pool + input data controller
    #components = 8 # Only har controller
    #components = 15 # All controllers

    tm = gmtime()
    logging.basicConfig(
        level=logging.INFO,
        #filename='{}.log'.format(str(tm.tm_year) + '%02d' % tm.tm_mon + '%02d' % tm.tm_mday), 
        #filemode='w', 
        format='%(name)s - %(levelname)s - %(message)s')

    m = main(components)