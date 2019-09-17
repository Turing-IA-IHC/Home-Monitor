"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the devices that can be loaded.
"""

if __name__ == "__main__":
    print('\n\tAlert!! This class can not start itself. Please start using main.py file.')
    exit(0)

from os.path import dirname, normpath
from time import sleep
import threading
import logging
import abc

import Misc
from DataPool import DataPool

class DeviceController(abc.ABC):
    """ Generic class that represents all the devices that can be loaded. """
    
    def __init__(self, cfg):
        self.dp = DataPool()        # Object to send information
        self.URL = ""               # Pool URL
        self.Me_Path = "./"         # Path of current component
        self.Standalone = False     # If a child start in standalone
        
        self.Config = cfg           # Object with all config params
        self.Devices = []           # List of devices loaded
        self.InactiveDevices = []   # List of devices unpluged
        self.Sampling = self.Config['SAMPLING'] # Sampling rate
        
        self.loggingLevel:int = 0   # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log

    """ Abstract methods """
    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Load knowledge o whatever need for pre processing """
        pass

    @abc.abstractmethod
    def initializeDevice(self, device):
        """  Implement me! :: Initialize device """
        pass

    @abc.abstractmethod
    def getData(self, device):
        """ Implement me! :: Returns a list of tuples like {controller, device, data} with data elements """
        pass

    @abc.abstractmethod
    def showData(self, gd):
        """  Implement me! :: To show data if this module start standalone.
        set self.Standalone = True before start. """
        pass

    """ Real methods """
    def start(self):
        """ Start module and getting data """
        self.activateLog()
        self.preLoad()
            
        self.running = True
        self.Devices = self.getDeviceList()

        for device in self.Devices:
            device['capture'] = self.initializeDevice(device)

        logging.debug('Reading data from devices type {}.'.format(self.__class__.__name__))
        failedSend = 0
        while self.running:

            for device in self.Devices:
                if device in self.InactiveDevices:
                    continue

                gdList = []
                try:
                    gdList = self.getData(device)
                except:
                    logging.exception(
                        'Unexpected error readding data from device: {}:{} ({})'.format(
                            device['id'], device['name'], str(device['capture']))
                        )
                    self.InactiveDevices.append(device)
                    import threading
                    x = threading.Thread(target=self.checkDevice, args=(device,))
                    x.start()
            
                package = Misc.randomString()
                for gd in gdList:
                    try:
                        if not self.Standalone:
                            self.send(gd['controller'], gd['device'], gd['data'], gd['aux'], package=package)
                        else:
                            self.showData(gd)
                        failedSend = 0
                    except:
                        failedSend += 1
                        logging.exception(
                            'Unexpected error sending data from device: {}:{} ({})'.format(
                                device['id'], device['name'], str(device['capture']))
                            )

                        if failedSend > 2 and not self.dp.isLive():
                            logging.error('Pool no found {} will shutdown.'.format(self.__class__.__name__))
                            self.stop()
                            break

            sleep(self.Sampling)

    def stop(self):
        """ Stop module and getting data """
        self.running = False
    
    def getDeviceList(self):
        """ Returns a list of devices able to read """
        devices = Misc.readConfig(normpath(self.Me_Path) + "/devices.yaml")
        devices = devices['DEVICES']
        result = list(filter(lambda d: Misc.toBool(d['enabled']), devices))
        return result

    def checkDevice(self, device):
        """ Check if a device is on line again """
        for _ in range(30):
            try:
                thrs = threading.enumerate()
                if thrs[0]._is_stopped: # MainThread
                    break
                device['capture'] = self.initializeDevice(device)
                self.getData(device)
                self.InactiveDevices.remove(device)
                break
            except:
                pass

            sleep(int(self.Config["CHECK_TIME"]))

    def send(self, controller, device, data, aux=None, package=''):
        """ Send data to pool """
        self.dp.URL = self.URL
        #print('Sending data to {}. controller: {}. device: {}.'.format(self.URL, controller, device))
        self.dp.sendData(controller, device, data, aux, package)

    def activateLog(self):
        """ Activate logging """
        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)
