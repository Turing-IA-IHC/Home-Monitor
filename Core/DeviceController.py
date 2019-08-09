"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the components that can be loaded.
"""

import abc
from DataPool import DataPool
import Misc

class DeviceController(abc.ABC):
    """ Generic class that represents all the components that can be loaded. """
    
    def __init__(self, cfg):
        self.dp = DataPool()        # Object to send information
        self.URL = ""               # Pool URL
        
        self.Config = cfg           # Object with all config params
        self.Devices = []           # List of devices loaded
        self.InactiveDevices = []   # List of devices unpluged
        self.Sampling = self.Config['SAMPLING'] # Sampling rate
        
        self.loggingLevel = None    # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log

    """ Abstract methods """
    @abc.abstractmethod
    def start(self):
        """ Implement me! :: Start module and getting data """
        pass

    @abc.abstractmethod
    def stop(self):
        """ Implement me! :: Stop module and getting data """
        pass

    @abc.abstractmethod
    def getDeviceList(self):
        """ Implement me! :: Returns a list of devices able to read """
        pass

    @abc.abstractmethod
    def getData(self, idDevice):
        """ Implement me! :: Returns a list of tuples like {controller, device, data} with data elements """
        pass

    """ Real methods """
    def send(self, controller, device, data, aux=None):
        """ Send data to pool """
        self.dp.URL = self.URL
        #print('Sending data to {}. controller: {}. device: {}.'.format(self.URL, controller, device))
        self.dp.sendData(controller, device, data, aux)

    def activateLog(self):
        """ Activate logging """
        Misc.loggingConf(self.loggingLevel, self.loggingFile, self.loggingFormat)
