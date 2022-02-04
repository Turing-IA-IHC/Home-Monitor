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
import logging
import json
import math

from cv2 import cv2
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.models import load_model

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from ActivityRecognizer import ActivityRecognizer
from DataPool import Data

class NewRecognizer(ActivityRecognizer):
    """ Template to predict classes of New Recognizer. """

    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start processing
        pass
    
    def loadModel(self):
        """ Loads model """
        # TODO: Use if you need an special way of loading knowledge
        """ Example:
        ModelPath = normpath(dirname(__file__) + "/" + self.Config['MODEL'])
        logging.debug('Loadding model for {} from {} ...'.format(self.__class__.__name__, ModelPath))       
        self.NET = load_model(ModelPath)
        self.NET._make_predict_function()
        if logging.getLogger().level < logging.INFO: # Only shows in Debug
            self.NET.summary()
        """
        pass

    def loaded(self):
        """  Implement me! :: Just after load the model """
        # TODO: This method is called just after load model
        pass

    def predict(self, data):
        """ Implement me! :: Exec prediction to recognize an activity """
        # TODO: This method must return a list oh classes detected in Input Data and the auxiliar information.
        # Avoid returning class None or background.
        """ Example:
        return np.array([ self.Classes[1], ]), 'Aux'
        """
        pass

    def showData(self, data:Data):
        """  Implement me! :: To show data if this module start standalone """
        # TODO: Put code if you want test this module in standalone form.
        """ Exmple:
        print('Classes detected: {}. Aux: {}.'.format(classes, aux))
        """
        pass
    
    def simulateData(self, device):
        """  Implement me! :: Allows to simulate data if this module start standalone """
        # TODO: Put code if you want test this module in standalone form.
        """ Example:
        auxData = '{' + '"W":{}, "H":{}'.format(1, 1) + '}'
        return [{'timeQuery':0}, {'id':0, 'data':[], 'aux':auxData}]
        """
        pass
    
""" =========== Start standalone =========== """
if __name__ == "__main__":
    comp = NewRecognizer()
    comp.init_standalone(Me_Path=dirname(__file__))