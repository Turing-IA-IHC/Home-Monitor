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

class NewRecognizer(EventRecognizer):
    """ Template to predict classes of New Recognizer. """

    Simulating = False

    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start processing
        pass
    
    def loadModel(self):
        """ Loads model """
        # TODO: Use if you need an special way of loading knowledge
        """ Example:
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
        """
        pass

    def loaded(self):
        """ Implement me! :: Just after load the model """
        # TODO: This method is called just after load model
        pass

    def predict(self, data):
        """ Implement me! :: Exec prediction to recognize an activity """
        # TODO: This method must return a list of classes detected in Input Data and the auxiliar information.
        # Avoid returning class None or background.
        """ Example:
        x = cv2.cvtColor(data.data, cv2.COLOR_BGR2RGB)
        x = cv2.resize(x, (256, 256), interpolation = cv2.INTER_AREA)
        x = np.expand_dims(x, axis=0)

        array = self.MODEL.predict(x)
        result = array[0]
        answer = np.argmax(result)

        dataReturn = []
        auxData = '"t":"json", "idSource":"{}"'

        dataInf = Data()
        dataInf.source_type = self.ME_TYPE
        dataInf.source_name = self.ME_NAME
        dataInf.source_item = ''
        dataInf.data = self.CLASSES[answer]
        dataInf.aux = '{' + auxData.format(data.id) + '}'
        dataReturn.append(dataInf)

        return dataReturn
        """
        pass

    def showData(self, dataPredicted:Data, dataSource:Data):
        """ Implement me! :: To show data if this module start standalone """
        # TODO: Put code if you want test this module in standalone form.
        """ Exmple:
        print('Classes detected: {}. Aux: {}.'.format(dataPredicted.data, dataPredicted.aux))
        """
        pass
    
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Implement me! :: Allows to simulate data if this module start standalone """
        if self.Simulating == None or self.Simulating == False:
            self.Simulating = True
        # TODO: Put code if you want test this module in standalone form.
        """ Example:
        dataReturn = []
        dataReturn.insert(0, {'timeQuery':time()})
        return dataReturn
        """
        pass
    
# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = NewRecognizer()
    comp.init_standalone(Me_Path=dirname(__file__))
