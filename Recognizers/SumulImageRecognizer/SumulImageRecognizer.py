"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Template to predict classes of New Rercognizer.
"""

import sys
import numpy as np
from os.path import dirname, normpath
import json
import math
from time import time, sleep

from cv2 import cv2
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.models import load_model

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from EventRecognizer import EventRecognizer
from DataPool import LogTypes, SourceTypes, Messages, Data

class SumulImageRecognizer(EventRecognizer):
    """ Template to predict classes of New Recognizer. """

    simulationStep = 0

    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start processing
        pass
    
    def loadModel(self):
        """ Loads model """
        # TODO: Use if you need an special way of loading knowledge
        """ Example:
        ModelPath = normpath(self.ME_PATH + "/" + self.ME_CONFIG['MODEL'])
        self.log(Messages.controller_loading_model.format(ModelPath), LogTypes.DEBUG)
        self.MODEL = load_model(ModelPath)
        self.MODEL._make_predict_function()
        if self.ME_STANDALONE:
            self.MODEL.summary()
        """
        pass

    def loaded(self):
        """ Implement me! :: Just after load the model """
        # TODO: This method is called just after load model
        pass

    def predict(self, data:Data):
        """ Exec prediction to recognize an activity """
        
        dataReturn = []

        d = data.strToJSon(data.aux)

        if Misc.hasKey(d, 'time', '') == '' or Misc.hasKey(d, 'event', '') == '':
            return dataReturn
        
        time_event = d['time']
        event = d['event']
        auxData = '{' + '"time":"{}", "event":"{}"'.format(time_event, event) + '}'

        dataSimulated = Data()
        dataSimulated.source_name = self.ME_NAME
        dataSimulated.source_type = SourceTypes.RECOGNIZER
        dataSimulated.source_item = event
        dataSimulated.data = { 'class':event, 'acc':1.0 }
        dataSimulated.aux = auxData
        dataReturn.append(dataSimulated)
        return dataReturn

    def showData(self, dataPredicted:Data, dataSource:Data):
        """ To show data if this module start standalone """
        self.log('Class detected:' + dataPredicted.data['class'] + \
            ' with acc:' + str(dataPredicted.data['acc']), LogTypes.INFO)
        #print('Class detected:' + dataPredicted.data['class'] + \
        #    ' with acc:' + str(dataPredicted.data['acc']), end='\r')

        # Display the resulting frame
        rgbImage = dataSource.data
        cv2.imshow(dataSource.source_name + '-' + dataSource.source_item, rgbImage)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
            cv2.destroyAllWindows()
    
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Allows simulate input data """
        if self.simulationStep == 0:
            self.file = np.loadtxt(self.SimulatingPath, dtype=np.object, delimiter=',')
            self.file_length = len(self.file)

        dataReturn = []

        if self.simulationStep < self.file_length:
            if len(self.file[self.simulationStep, 2]) < 3:
                dataReturn.insert(0, {'queryTime':time()})
                self.simulationStep += 1
                print(' -- no -- ')
                return dataReturn
            
            frame = cv2.imread(self.file[self.simulationStep, 1])
            height = np.size(frame, 0)
            width = np.size(frame, 1)
            time_event = self.file[self.simulationStep, 3]
            event = self.file[self.simulationStep, 2]
            auxData = '{' + '"t":"{}", "ext":"{}", "W":{}, "H":{}, "time":"{}", "event":"{}"'.format('image_rgb', 
            'png', width, height, time_event, event) + '}'
            
            dataSimulated = Data()
            dataSimulated.source_name = 'SimulImageController'
            dataSimulated.source_type = SourceTypes.CONTROLLER
            dataSimulated.source_item = ''
            dataSimulated.data = frame
            dataSimulated.aux = auxData

            self.simulationStep += 1
            dataReturn.append(dataSimulated)
            dataReturn.insert(0, {'queryTime':time()})
        else:
            self.simulationStep = 0
            dataReturn = self.simulateData(dataFilter)

        return dataReturn
    
# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = SumulImageRecognizer()
    comp.setLoggingSettings(LogTypes.WARNING)
    comp.init_standalone(path=dirname(__file__))
    sleep(600)
