"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to analyze anomalous events.
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
from EventAnayzer import EventAnalyzer

class AnomalousEventAnalyzer(EventAnalyzer):
    """ Class to analyze anomalous events. """

    def preLoad(self):
        """ Load knowledge for prediction """
        """ Load keras + tensorflow model """
        ## TODO: Put here, everything you need to load before you start event analysis
        
        """ Example:
        ModelPath = normpath(dirname(__file__) + "/" + self.Config['MODEL'])
        logging.debug('Loadding model for {} from {} ...'.format(self.__class__.__name__, ModelPath))       
        self.NET = load_model(ModelPath)
        self.NET._make_predict_function()
        if logging.getLogger().level < logging.INFO: # Only shows in Debug
            self.NET.summary()
        """
        self.Controller = Misc.hasKey(self.Config, 'CONTROLLER', '')    # Controller to filter data
        self.Device = Misc.hasKey(self.Config, 'DEVICE', '')            # Device name to filter data
        self.Limit = -1                                                 # Amount of data to filter data

    def predict(self, data):
        """ Do prediction and return class found """
        # TODO: Make predictions and return like an array of classes and the auxiliar information.
        # Avoid returning class None or background.
        return np.array([ self.Classes[1], ]), 'Aux'
  
    def showData(self, data, classes, aux):
        """ To show data if this module start standalone.
        set self.Standalone = True before start. """
        # TODO: Put code if you want test this module in standalone form.
        print('Classes detected: {}. Aux: {}.'.format(classes, aux))

    def testData(self):
        """ Data t test if this module start standalone. 
            You must return an array as expected if you query the data pool.
        set self.Standalone = True before start. """
        # TODO: Put code if you want test this module in standalone form.
        auxData = '{' + '"W":{}, "H":{}'.format(1, 1) + '}'
        return [{'timeQuery':0}, {'id':0, 'data':[], 'aux':auxData}]
    
# =========== Start standalone =========== #
if __name__ == "__main__":
    config = Misc.readConfig(dirname(__file__) + "/config.yaml")
    Alz = AnomalousEventAnalyzer(config)
    Alz.Me_Path = dirname(__file__)
    Alz.Standalone = True
    Alz.start()
