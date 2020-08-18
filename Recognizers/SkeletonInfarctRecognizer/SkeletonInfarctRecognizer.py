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

class SkeletonInfarctRecognizer(EventRecognizer):
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
        ModelPath = normpath(self.ME_PATH + "/" + self.ME_CONFIG['MODEL_FACE'])
        self.log(Messages.controller_loading_model.format(ModelPath), LogTypes.DEBUG)
        self.MODEL_FACE = load_model(ModelPath)
        self.MODEL_FACE._make_predict_function()
        if self.ME_STANDALONE:
            self.MODEL_FACE.summary()

    def loaded(self):
        """ Implement me! :: Just after load the model """
        # TODO: This method is called just after load model
        pass

    def predict(self, data:Data):
        """ Exec prediction to recognize an activity """

        rgbFilter = Data()
        rgbFilter.id = None
        rgbFilter.package  = data.package
        rgbFilter.source_name = 'CamController'
        rgbFilter.source_type = SourceTypes.CONTROLLER
        rgbData = self.receive(dataFilter=rgbFilter, limit=1, lastTime=0)
        
        if len(rgbData) < 2:
            return []
        rgbData = rgbData[1]

        dataReturn = []

        for per in data.data:
            if per[0].any() == None or per[1].any() == None or per[2].any() == None or per[5].any() == None:
                continue   

            img = self.extract_face(frame=rgbData.data, person=per)
            
            skeletonResult = self.predict_skeleton(person=per)
            faceResult = self.predict_face(frame=img)

            array = self.predict_full(skeletonResult, faceResult)
            result = array[0]
            answer = np.argmax(result)

            if result[answer] < 0.7:
                continue

            dataInf = Data()
            dataInf.source_item = self.CLASSES[answer]
            dataInf.data = { 'class':self.CLASSES[answer], 'acc':result[answer] }
            dataReturn.append(dataInf)

        return dataReturn

    def showData(self, dataPredicted:Data, dataSource:Data):
        """ Implement me! :: To show data if this module start standalone """
        self.log('Class detected:' + dataPredicted.data['class'] + \
            ' with acc:' + str(dataPredicted.data['acc']), LogTypes.INFO)
        
        #cv2.imshow(dataSource.source_name + '-' + dataSource.source_item, dataSource.data)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    self.stop()
        #    cv2.destroyAllWindows()

        with open("M:/tmp/HM-SimulatingData/SkeletonInfarctRecognizer_OutPut.txt",'a+') as file:
            file.write('\n' + dataPredicted.toString(False, True))
    
    def simulateData(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Implement me! :: Allows to simulate data if this module start standalone """

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

    def extract_face(self, frame, person):
        """ Cut and return image of face base in neck and nose points """
        Nose = person[0]
        Neck = person[1]
        RShoulder = person[2]
        LShoulder = person[5]
        Radio1 = math.sqrt(math.pow(Neck[1] - Nose[1], 2) + math.pow(Neck[0] - Nose[0], 2))
        Radio2 = math.sqrt(math.pow(Neck[1] - RShoulder[1], 2) + math.pow(Neck[0] - RShoulder[0], 2))
        Radio3 = math.sqrt(math.pow(Neck[1] - LShoulder[1], 2) + math.pow(Neck[0] - LShoulder[0], 2))
        Radio = max(Radio1, Radio2, Radio3)
        Radio = int(Radio)
        x = max(Nose[0] - Radio, 0)
        y = max(Nose[1] - Radio, 0)
        
        Face = frame[y:Nose[1] + Radio, x:Nose[0] + Radio]
        Face = cv2.resize(Face, (64, 64))
        return Face

    def predict_skeleton(self, person):
        """ Make skeleton prediction """
        person = np.expand_dims(person, axis=0)
        return self.MODEL.predict(person[:,0:8])
        
    def predict_face(self, frame):
        """ Make face prediction """
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.expand_dims(frame, axis=0)
        return self.MODEL_FACE.predict(frame)
        
    def predict_full(self, skeletonResult, faceResult):
        """ Combine skeleton and face results """
        result = skeletonResult + faceResult
        result /= 2
        return result

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = SkeletonInfarctRecognizer()
    comp.setLoggingSettings(LogTypes.DEBUG)
    comp.init_standalone(path=dirname(__file__))
    sleep(600)
