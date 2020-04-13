"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

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

class ColorInfarctRecognizer(EventRecognizer):
    """ Template to predict classes of New Recognizer. """

    Simulating = False

    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start processing
        pass
    
    def loadModel(self):
        """ Loads model """
        ModelPath = normpath(self.ME_PATH + "/" + self.CONFIG['MODEL'])
        dataC = Data()
        dataC.source_type = SourceTypes.RECOGNIZER
        dataC.source_name = self.ME_NAME
        dataC.source_item = ''
        dataC.data = Messages.controller_loading_model.format(ModelPath)
        dataC.aux = ''
        self.COMMPOOL.logFromComponent(dataC, LogTypes.INFO)
        self.MODEL = load_model(ModelPath)
        self.MODEL._make_predict_function()
        if self.STANDALONE:
            self.MODEL.summary() 

    def loaded(self):
        """ Implement me! :: Just after load the model """
        # TODO: This method is called just after load model
        pass

    def predict(self, data):
        """ Exec prediction to recognize an activity """
        x = cv2.cvtColor(data.data, cv2.COLOR_BGR2RGB)
        x = cv2.resize(x, (256, 256), interpolation = cv2.INTER_AREA)
        x = np.expand_dims(x, axis=0)

        array = self.MODEL.predict(x)
        result = array[0]
        answer = np.argmax(result)

        dataReturn = []
        auxData = ''
        
        dataInf = Data()
        dataInf.source_type = self.ME_TYPE
        dataInf.source_name = self.ME_NAME
        dataInf.source_item = ''
        dataInf.data = self.CLASSES[answer]
        dataInf.aux = auxData
        dataReturn.append(dataInf)

        return dataReturn

    def showData(self, dataPredicted:Data, dataSource:Data):
        """ To show data if this module start standalone """
        #print('Classes detected: {}. Aux: {}.'.format(dataPredicted.data, dataPredicted.aux))
        cv2.imshow(dataSource.source_name + '-' + dataSource.source_item, dataSource.data)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
            cv2.destroyAllWindows()

        with open("RGBInfarctRecignizer_OutPut.txt",'a+') as file:
            file.write('\n' + dataPredicted.toString(True, True))
    
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Allows to simulate data if this module start standalone """
        dataReturn = []
        try:
            if self.Simulating == None or self.Simulating == False:
                self.Simulating = True
                self.Counter = 0
                self.file = open("CamController_OutPut.txt", 'r').readlines()
                self.file_length = len(self.file)

            if self.Counter < self.file_length:            
                limit = limit if limit > -1 else self.file_length - self.Counter
                for _ in range(limit):
                    if self.file[self.Counter] != '' and len(self.file[self.Counter]) > 10:
                        dataSimulated = Data()
                        dataSimulated = dataSimulated.parse(self.file[self.Counter], False, True)
                        dataReturn.append(dataSimulated)
                    self.Counter += 1
            else:
                self.Started = False
        except:
            print(self.COMMPOOL.errorDetail('Error simulateData: '))
            self.Started = False

        dataReturn.insert(0, {'timeQuery':time()})
        #sleep(30/1000)
        return dataReturn
    
# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = ColorInfarctRecognizer()
    comp.init_standalone(Me_Path=dirname(__file__))
