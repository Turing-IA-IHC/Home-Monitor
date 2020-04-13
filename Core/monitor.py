"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly recognizersmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to monitor the health of the entire system
"""

__version__ = "1.0.0"

import sys
import platform
from time import time, sleep
from os.path import dirname, abspath, exists, split, normpath

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from DataPool import SourceTypes, LogTypes, Messages, PoolStates, Data, Binnacle, DataPool, CommPool

class monitor:
    """ Class to monitor the health of the entire system """

    def __init__(self, vars=[]):
        """ Start the sub system to monitor the health of the entire system
            Vars: Set any config var using form VAR=VALUE
        """
        print('\n')
        print('=========================='.center(50, "="))
        print(' Wellcome to Home-Monitor '.center(50, "=") )
        print(' Version: {} '.format(__version__).center(50, " "))
        print('=========================='.center(50, "="))
        print(' Health Monitor System '.center(50, "=") )
        print('=========================='.center(50, "="))
        print('')
        
        self.CONFIG_FILE = normpath(abspath('.') + "/config.yaml")
        self.CONFIG = Misc.readConfig(self.CONFIG_FILE)

        # Replacing config vars
        Misc.replaceConfigVars(self.CONFIG, vars)
        Misc.showConfig(self.CONFIG)

        self.commPool = CommPool(self.CONFIG)

        current_os = platform.system()
        if current_os == 'Windows':
            print(' Press esc or x to exit '.center(50, "=") )
            import msvcrt

        chk_time = Misc.hasKey(self.CONFIG, 'CHECKING_TIME', 30)
        while True:
            if current_os == 'Windows':
                if msvcrt.kbhit():
                    keyPressed = ord(msvcrt.getch())
                    if keyPressed in [27, 120]:
                        break
            
            pool_msg = self.commPool.count()
                        
            for i in range(chk_time):
                msg = '{} - Refreshing time: {} Seg.'.format(pool_msg, (chk_time - i))
                if Misc.toBool(Misc.hasKey(self.CONFIG, 'RUN_IN_COLLAB', 'N')):
                    sys.stdout.write('\r' + msg)
                else:
                    print(msg, end='\r', flush=True)
            
                sleep(1)

if __name__ == "__main__":
    #hms = monitor(['URL_BASE=http://9f9e80a7.ngrok.io',])
    hms = monitor()
