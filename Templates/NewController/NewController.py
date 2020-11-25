"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019 (Change)
    Copyright (c) 2019 G0 S.A.S. (Change)
    See LICENSE file for details

Class information:
    Template to get data from a device type NewController.
"""

import sys
from os.path import dirname, normpath

import math
import logging
import numpy as np
from time import sleep, time

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from DeviceController import DeviceController
from DataPool import Data, LogTypes

class NewController(DeviceController):
    """ Template to get data from a device type New. """
    
    def preLoad(self):
        """ Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start capturing data
        pass
  
    def initializeDevice(self, device):
        """ Initialize device """
        # TODO: Load a physical device and put in 'capture' var
        capture = None
        return capture

    def getData(self, device):
        """ Returns a list of tuples like {controller, device, data} with data elements """

        dev = self.Devices[device["id"]]['objOfCapture']
        # TODO: Read and return a list of tuples like {controller, device, data} with data elements
        dataReturn = []

        """ Example:
        _, frame = dev.read()

        if frame is None:
            return []

        height = np.size(frame, 0)
        width = np.size(frame, 1)
        deviceName = Misc.hasKey(device, 'name', device["id"])

        auxData = '{' + '"W":{}, "H":{}'.format(width, height) + '}'
        
        dataRgb = Data()
        dataRgb.source_type = self.ME_TYPE
        dataRgb.source_name = self.ME_NAME
        dataRgb.source_item = deviceName
        dataRgb.data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        dataRgb.aux = auxData
        dataReturn.append(dataRgb)
        
        dataReturn.append({
                'controller': 'CamController/Gray',
                'device': deviceName,
                'data': self.preProc_Gray(frame),
                'aux': auxData,
            })
        """
        return dataReturn
      
    def showData(self, data:Data):
        """ To show data if this module start standalone """
        # TODO: Put code if you want test this module in standalone form.
        pass

    def simulateData(self, dataFilter:Data):
        """ Allows simulate input data """
        # TODO: Put code if you want test this module in standalone form.
        dataReturn = []        
        return dataReturn

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = NewController()
    comp.setLoggingSettings(LogTypes.DEBUG)
    comp.init_standalone(path=dirname(__file__))
    sleep(600)