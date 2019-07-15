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

from multiprocessing import Process, Value
from time import time, sleep

from InputDataController import InputDataController
from DataPool import DataPool

class main():
    """ Main class to start whole system """
    def __init__(self):
        print('=========================='.center(50, "="))
        print(' Wellcome to Home-Monitor '.center(50, "=") )
        print(' Version: {}      '.format(__version__).center(50, " "))
        print('=========================='.center(50, "="))
        print('\n\n')
        
        print('Starting pool ...')
        self.pool = DataPool()
        self.pool.URL = "http://127.0.0.1:5000/pool"
        self.poolRunning = False

        print('Starting device controllers ...')
        self.inputData = InputDataController()
        self.inputData.URL = "http://127.0.0.1:5000/pool"
        self.controllerRunning = False
        self.inputData.loadControllers()
        self.inputData.start()

        print('Starting event controllers ...')

        print('Starting the magic ...')
        self.heart_beat()
        
    def heart_beat(self):
        
        try:
            """ Section to control the execution of the input data """
            inputDataThread = Process(target=self.inputData.simulate, args=())
            inputDataThread.daemon = True
            inputDataThread.start()
        except:
            pass

        while True:
            try:                
                """ Section to control the execution of the pool """
                if not self.poolRunning:
                    inputDataThread = Process(target=self.pool.start, args=())
                    inputDataThread.daemon = True
                    print('Starting pool service...') # TODO: Change log class
                    inputDataThread.start()
                    self.poolRunning = True

                    #poolBeat = Value('d', time())
                    #poolThread = Process(target=self.pool.pop, args=(poolBeat,))           
                elif not self.pool.isLive():
                    self.poolRunning = False
                    print('Pool service is death. System auto start it.') # TODO: Change log class
                else:
                    print('Pool service is living. Has', self.pool.count(), 'data') # TODO: Change log class

                sleep(3)
            except:
                pass

if __name__ == "__main__":
    m = main()