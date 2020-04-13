"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Template to analyze classes of recognizers.
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
from ActivityAnalyzer import ActivityAnalyzer
from DataPool import LogTypes, SourceTypes, Messages, Data

class AnomalousEventAnalyzer(ActivityAnalyzer):
    """ Template to analyze classes of recognizers. """

    Simulating = False

    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        # TODO: Put here, everything you need to load before you start processing
        pass
    
    def loadModel(self):
        """ Loads model """
        from textblob.classifiers import NaiveBayesClassifier
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        import pickle
        ModelPath = normpath(self.ME_PATH + "/" + self.CONFIG['MODEL'])
        with open(ModelPath, 'rb') as file:
            self.MODEL = pickle.load(file)

    def loaded(self):
        """ Implement me! :: Just after load the model and channels """
        # TODO: This method is called just after load model
        pass

    def analyze(self, data):
        """ Exec analysis of activity """
        Phrase = "At {} the {} detect {} in {} of {}"
        auxSource = data.strToJSon(data.aux)
        Phrase = Phrase.format(Misc.timeToString(data.born), data.source_name, data.data, \
            Misc.hasKey(auxSource,'source_item',''), Misc.hasKey(auxSource,'source_name','') )

        dataReturn = []
        auxData = '"phrase":"{}"'
        
        typeDetected:str = self.MODEL.classify(Phrase)
        if typeDetected.lower() != 'none': 
            dataInf = Data()
            dataInf.source_type = self.ME_TYPE
            dataInf.source_name = self.ME_NAME
            dataInf.source_item = ''
            dataInf.data = typeDetected
            dataInf.aux = "{" + auxData.format(Phrase) + "}"
            dataReturn.append(dataInf)

        return dataReturn

    def showData(self, dataanalyzeed:Data, dataSource:Data):
        """ Implement me! :: To show data if this module start standalone """
        # TODO: Put code if you want test this module in standalone form.
        """ Exmple:
        print('Classes detected: {}. Aux: {}.'.format(dataanalyzeed.data, dataanalyzeed.aux))
        """
        pass
    
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Allows to simulate data if this module start standalone """
        Phrase = "At {} the {} detect {} in {} of {}"
        dataReturn = []
        try:
            if self.Simulating == None or self.Simulating == False:
                self.Simulating = True
                self.Counter = 0
                self.file = open("RGBInfarctRecignizer_OutPut.txt", 'r').readlines()
                self.file_length = len(self.file)

            if self.Counter < self.file_length:            
                limit = limit if limit > -1 else self.file_length - self.Counter
                for _ in range(limit):
                    if self.file[self.Counter] != '' and len(self.file[self.Counter]) > 10:
                        #"At {} the {InfarctSkeleton} detect {``Infarct''} in {livingRoom1} of {CamController}.".format()

                        dataSimulated = Data()
                        dataSimulated = dataSimulated.parse(self.file[self.Counter], True, True)
                        dataNarrator = Data()
                        dataAux = dataNarrator.strToJSon(dataSimulated.aux)
                        source_item = Misc.hasKey(dataAux, 'source_item', '')
                        source_name = Misc.hasKey(dataAux, 'source_name', '')
                        dataNarrator.data = Phrase.format(dataSimulated.born, 
                            dataSimulated.source_name, dataSimulated.data, source_item, source_name)
                        print(dataNarrator.data)
                        dataReturn.append(dataSimulated)
                    self.Counter += 1
            else:
                self.Started = False
        except:
            self.COMMPOOL.errorDetail('Error simulateData: ')
            self.Started = False

        dataReturn.insert(0, {'timeQuery':time()})
        sleep(300/1000)
        return dataReturn
    
# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = AnomalousEventAnalyzer()
    comp.init_standalone(Me_Path=dirname(__file__))
