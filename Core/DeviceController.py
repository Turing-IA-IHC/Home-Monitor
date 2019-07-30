"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the components that can be coupled.
"""

import abc
from DataPool import DataPool

class DeviceController(abc.ABC):
    """ Generic class that represents all the components that can be coupled. """

    URL = ""
    sampling = 0
    
    def __init__(self, cfg):
        self.Config = cfg
        self.dp = DataPool()

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
    def send(self, controller, device, data):
        """ Send data to pool """        
        self.dp.URL = self.URL
        #print('Sending data to {}. controller: {}. device: {}.'.format(self.URL, controller, device))
        self.dp.sendData(controller, device, data)