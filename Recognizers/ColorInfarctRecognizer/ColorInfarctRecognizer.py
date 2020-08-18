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

class ColorInfarctRecognizer(EventRecognizer):
    """ Template to predict classes of New Recognizer. """

    simulationStep = 0

    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start processing
        pass
    
    def loadModel(self):
        """ Loads model """
        ModelPath = normpath(self.ME_PATH + "/" + self.ME_CONFIG['MODEL'])
        self.log(Messages.controller_loading_model.format(ModelPath), LogTypes.DEBUG)
        self.MODEL = load_model(ModelPath)
        self.MODEL._make_predict_function()
        if self.ME_STANDALONE:
            self.MODEL.summary() 

    def loaded(self):
        """ Implement me! :: Just after load the model """
        # TODO: This method is called just after load model
        pass

    def predict(self, data:Data):
        """ Exec prediction to recognize an activity """

        rgbFilter = Data()
        rgbFilter.id = None
        rgbFilter.package = data.package
        rgbFilter.source_name = 'CamController'
        rgbFilter.source_type = SourceTypes.CONTROLLER
        rgbData = self.receive(dataFilter=rgbFilter, limit=1, lastTime=0)
        
        if len(rgbData) < 2:
            return []

        rgbData = rgbData[1]
        img = self.fuzzySilhouetteAndRGB(rgb=rgbData.data, mask=data.data)
        #x = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        x = cv2.resize(img, (256, 256), interpolation = cv2.INTER_AREA)
        x = np.expand_dims(x, axis=0)
        data.data = img

        array = self.MODEL.predict(x)
        result = array[0]
        answer = np.argmax(result)

        if result[answer] < 0.7:
            return []

        dataReturn = []
        
        dataInf = Data()
        dataInf.source_item = self.CLASSES[answer]
        dataInf.data = { 'class':self.CLASSES[answer], 'acc':result[answer] }
        dataReturn.append(dataInf)

        return dataReturn

    def showData(self, dataPredicted:Data, dataSource:Data):
        """ To show data if this module start standalone """
        self.log('Class detected:' + dataPredicted.data['class'] + \
            ' with acc:' + str(dataPredicted.data['acc']), LogTypes.INFO)

        #cv2.imshow(dataSource.source_name + '-' + dataSource.source_item, dataSource.data)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    self.stop()
        #    cv2.destroyAllWindows()

        #with open("M:/tmp/HM-SimulatingData/ColorInfarctRecognizer_OutPut.txt",'a+') as file:
        #    file.write('\n' + dataPredicted.toString(False, True))
    
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Allows to simulate data if this module start standalone """

        if self.simulationStep == 0:
            self.file = open(self.SimulatingPath, 'r').readlines()
            self.file_length = len(self.file)

        dataReturn = []

        if dataFilter.package != '':
            for target_list in self.file:
                if len(target_list) < 10:
                    continue
                dataSimulated = Data()
                dataSimulated = dataSimulated.parse(target_list, False, True)
                if dataSimulated.package == dataFilter.package and dataSimulated.source_name == dataFilter.source_name:
                    dataReturn.append(dataSimulated)
                    dataReturn.insert(0, {'queryTime':time()})
                    return dataReturn

        if self.simulationStep < self.file_length:
            if len(self.file[self.simulationStep]) < 10:
                dataReturn.insert(0, {'queryTime':time()})
                self.simulationStep += 1
                return dataReturn

            dataSimulated = Data()
            dataSimulated = dataSimulated.parse(self.file[self.simulationStep], False, True)

            if dataSimulated.source_name != dataFilter.source_name:
                dataReturn.insert(0, {'queryTime':time()})
                self.simulationStep += 1
                return dataReturn

            self.simulationStep += 1
            dataReturn.append(dataSimulated)
            dataReturn.insert(0, {'queryTime':time()})
        else:
            self.simulationStep = 0
            dataReturn = self.simulateData(dataFilter)

        return dataReturn

    # =========== Auxiliar methods =========== #
    
    def fuzzySilhouetteAndRGB(self, rgb, mask):
        """ Using mask generate a new RGB image extracting the backgroud """
        newImg = np.copy(rgb)
        newMask = np.expand_dims(np.copy(mask), axis=2)
        newImg[:,:,0] = np.where(newMask[:,:,0] == False, 255, newImg[:,:,0])
        newImg[:,:,1] = np.where(newMask[:,:,0] == False, 0, newImg[:,:,1])
        newImg[:,:,2] = np.where(newMask[:,:,0] == False, 255, newImg[:,:,2])
        return newImg

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = ColorInfarctRecognizer()
    comp.setLoggingSettings(LogTypes.INFO)
    comp.init_standalone(path=dirname(__file__))
    sleep(600)
