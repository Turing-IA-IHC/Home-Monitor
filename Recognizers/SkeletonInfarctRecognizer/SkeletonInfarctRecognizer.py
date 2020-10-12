"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to detect a posible person in infarcting.
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
    """ Class to detect a posible person in infarcting. """

    simulationStep = 0

    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        #pass
        import os
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    
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

        per = data.data
        if per[0].any() == None or per[1].any() == None or per[2].any() == None or per[5].any() == None:   
            return []

        skeletonResult = self.predict_skeleton(person=per)
        
        img = self.extract_face(frame=rgbData.data, person=per)
        faceResult = self.predict_face(frame=img)

        array = self.predict_full(skeletonResult, faceResult)
        result = array[0]
        answer = np.argmax(result)

        if result[answer] < 0.65:
            return []
        #print(result[answer], skeletonResult, faceResult)

        if answer > 0:
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

        #with open("M:/tmp/HM-SimulatingData/SkeletonInfarctRecognizer_OutPut.txt",'a+') as file:
        #    file.write('\n' + dataPredicted.toString(False, True))
    
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

    def furthest_shouder(self, person):
        """ Returns the distance to the shoulder furthest from the neck """
        neck = person[1]
        if person[2][0] is not None:
            length_RShoulder = math.pow(person[2][0] - neck[0], 2) + math.pow(person[2][1] - neck[1], 2)
        else:
            length_RShoulder = 0
        if person[5][0] is not None:        
            length_LShoulder = math.pow(person[5][0] - neck[0], 2) + math.pow(person[5][1] - neck[1], 2)
        else:
            length_LShoulder = 0

        if length_RShoulder > length_LShoulder:
            Shoulder = 2 # Right
            H = math.sqrt(length_RShoulder)
        else:
            Shoulder = 5 # Left
            H = math.sqrt(length_LShoulder)
            
        CosA = (person[Shoulder][0] - neck[0]) / H
        SinA = (neck[1] - person[Shoulder][1]) / H

        return H, CosA, SinA

    def complete_body(self, person):
        
        nose = person[0]
        neck = person[1]
        h = math.sqrt(math.pow(neck[0] - nose[0],2) + math.pow(neck[1] - nose[1], 2))
        h = int(h)

        if person[2][0] is None: # if not RShoulder mirror LShoulder
            auxX = neck[0] - person[5][0]
            auxY = person[5][1]
            person[2] = (neck[0] + auxX, auxY)
        
        if person[5][0] is None: # if not LShoulder mirror RShoulder
            auxX = neck[0] - person[2][0]
            auxY = person[2][1]
            person[5] = (neck[0] + auxX, auxY)

        #if person[8][0] is None: # No RHip calculate it
        #    person[8] = (person[2][0], neck[1] + int(2 * h))

        #if person[9][0] is None: # No LHip calculate it
        #    person[9] = (person[5][0], neck[1] + int(2 * h))

        if person[3][0] is None: # Not RElbow
            if not person[6][0] is None: # LElbow
                auxX = neck[0] - person[6][0]
                auxY = person[6][1]
                person[3] = (neck[0] + auxX, auxY)
            else:
                person[3] = (person[2][0], person[2][1] + 2*h)

        if person[6][0] is None: # Not LElbow
            if not person[3][0] is None: # RElbow
                auxX = neck[0] - person[3][0]
                auxY = person[3][1]
                person[6] = (neck[0] + auxX, auxY)
            else:
                person[6] = (person[5][0], person[5][1] + 2*h)

        if person[4][0] is None: # Not RWrist
            if not person[7][0] is None: # LWrist
                auxX = neck[0] - person[7][0]
                auxY = person[7][1]
                person[4] = (neck[0] + auxX, auxY)
            else:
                person[4] = (person[3][0], person[3][1] + 2*h)

        if person[7][0] is None: # Not LWrist
            if not person[4][0] is None: # RWrist
                auxX = neck[0] - person[4][0]
                auxY = person[4][1]
                person[7] = (neck[0] + auxX, auxY)
            else:
                person[7] = (person[6][0], person[6][1] + 2*h)

        return person

    def rotate_point(self,cX, cY, cosA, sinA, X, Y):
        X1 = X - cX
        Y1 = cY - Y
        X2 = (X1 * -cosA) - (Y1 * sinA)
        Y2 = (X1 * sinA) + (Y1 * -cosA)
        resX = (-1 if cosA > 0.0 else 1) * X2 + cX
        resY = (1 if cosA > 0.0 else -1) * Y2 + cY
        return int(resX), int(resY)

    def rotate_person(self, person):
        """ Rotate joints arround neck """
        neck = person[1]
        _, CosA, SinA = self.furthest_shouder(person)

        for p in range(len(person)):
            point = person[p]
            if not point[0] is None:
                x, y = self.rotate_point(neck[0], neck[1], CosA, SinA, point[0], point[1])
                #x, y = point[0], point[1]
                person[p] = (x, y)

        return person

    def norm_person(self, person):
        """ Normalize the distances between joints """
        H, _, _ = self.furthest_shouder(person)
        neck = person[1]
        nPerson = []
        for p in range(len(person)):
            point = person[p]
            if point[0] is None:
                x = None
                y = None
            else:
                x = (point[0] - neck[0]) / H
                y = (neck[1] - point[1]) / H
            nPerson.append((x, y))

        return nPerson   

    def predict_skeleton(self, person):
        """ Make skeleton prediction """
        self.rotate_person(person)
        self.complete_body(person)
        nPerson = self.norm_person(person)
        nPerson = np.expand_dims(nPerson, axis=0)
        return self.MODEL.predict(nPerson[:,0:8])
        
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
