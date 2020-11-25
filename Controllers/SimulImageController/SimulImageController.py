"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019 (Change)
    Copyright (c) 2019 G0 S.A.S. (Change)
    See LICENSE file for details

Class information:
    Template to get data from a device type SimulImageController.
"""

import sys
from os.path import dirname, normpath

import math
import logging
import numpy as np
from time import sleep, time

from cv2 import cv2 #pip install opencv-python

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from DeviceController import DeviceController
from DataPool import Data, LogTypes

class SimulImageController(DeviceController):
    """ Class to get data from simulated data. """
    simulationStep = 0
    
    def preLoad(self):
        """ Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start capturing data
        pass
  
    def initializeDevice(self, device):
        """ Initialize device """
        # TODO: Load a physical device and put in 'capture' var
        capture = None
        return capture

    def getData(self, device, frame=None, time_event=0, event=''):
        """ Returns a list of tuples like {controller, device, data} with data elements """

        dev = self.Devices[device["id"]]['objOfCapture']
        dataReturn = []
        
        if frame is None:
            return []

        height = np.size(frame, 0)
        width = np.size(frame, 1)
        deviceName = Misc.hasKey(device, 'name', device["id"])

        auxData = '{' + '"t":"{}", "ext":"{}", "W":{}, "H":{}, "time":"{}", "event":"{}"'.format('image_rgb', 
            'png', width, height, time_event, event) + '}'
        
        dataRgb = Data()
        dataRgb.source_type = self.ME_TYPE
        dataRgb.source_name = self.ME_NAME
        dataRgb.source_item = deviceName
        dataRgb.data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        dataRgb.aux = auxData
        dataReturn.append(dataRgb)
        
        #print(auxData, end='\r')
        
        # Display the resulting frame
        cv2.imshow(dataRgb.source_name + '-' + dataRgb.source_item, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
            cv2.destroyAllWindows()

        return dataReturn
      
    def showData(self, data:Data):
        """ To show data if this module start standalone """
        # Display the resulting frame
        rgbImage = cv2.cvtColor(data.data, cv2.COLOR_BGR2RGB)
        cv2.imshow(data.source_name + '-' + data.source_item, rgbImage)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
            cv2.destroyAllWindows()

    def simulateData(self, dataFilter:Data):
        """ Allows simulate input data """
        if self.simulationStep == 0:
            self.file = np.loadtxt(self.SimulatingPath, dtype=np.object, delimiter=',')
            self.file_length = len(self.file)

        if self.simulationStep < self.file_length:
            if len(self.file[self.simulationStep, 2]) < 3:
                self.simulationStep += 1
                #print(' -- no -- ')
                return []

            #print(' -- si -- ')
            self.simulationStep += 3
            frame = cv2.imread(self.file[self.simulationStep, 1])
            time_event = self.file[self.simulationStep, 3]
            event = self.file[self.simulationStep, 2]
            return self.getData(dataFilter.source_item, frame=frame, time_event=time_event, event=event)
        else:
            self.simulationStep = 0
            return self.simulateData(dataFilter)


# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = SimulImageController()
    comp.setLoggingSettings(LogTypes.DEBUG)
    comp.init_standalone(path=dirname(__file__))
    sleep(600)