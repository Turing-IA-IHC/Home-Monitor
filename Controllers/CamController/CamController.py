"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019 (Change)
    Copyright (c) 2019 G0 S.A.S. (Change)
    See LICENSE file for details

Class information:
    Template to get data from a device type CamController.
"""

import sys
import os
from os.path import dirname, normpath

import math
import numpy as np
from time import sleep, time

from cv2 import cv2 #pip install opencv-python
from scipy.ndimage.filters import gaussian_filter
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.models import load_model

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from DeviceController import DeviceController
from DataPool import Data, LogTypes

class CamController(DeviceController):
    """ Class to get RGB data from cams. """

    simulationStep = 0
    # visualize
    colors = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], [170, 255, 0], [85, 255, 0],
          [0, 255, 0], \
          [0, 255, 85], [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], [0, 0, 255],
          [85, 0, 255], \
          [170, 0, 255], [255, 0, 255], [255, 0, 170], [255, 0, 85]]
    
    def preLoad(self):
        """ Load knowledge for pre processing """
        self.getRGB = 'RGB' in self.ME_CONFIG['FORMATS']
        self.getGray = 'Gray' in self.ME_CONFIG['FORMATS']
        self.getObject = 'Object' in self.ME_CONFIG['FORMATS']
        self.getSkeleton = 'Skeleton' in self.ME_CONFIG['FORMATS']
        
        if self.getObject:
            sys.path.insert(0, self.ME_PATH)
            from mrcnn.CamControllerExtractor import CamControllerExtractor
            cocoH5 = Misc.hasKey(self.ME_CONFIG, 'MODEL_MSK', 'model/objectsModel.h5')
            self.cce = CamControllerExtractor(Me_Component_Path=self.ME_PATH, coco_model_path=cocoH5)
            self.cce.CLASSES_TO_DETECT = [x.lower() for x in self.ME_CONFIG['OBJECTS']]
        if self.getSkeleton:
            ModelPath = Misc.hasKey(self.ME_CONFIG, 'MODEL_SKl', 'model/poseModel.h5')
            ModelPath = os.path.normpath(os.path.join(self.ME_PATH, ModelPath))
            self.log('Loadding model from {} ...'.format(ModelPath), LogTypes.DEBUG)
            self.joinsBodyNET = load_model(ModelPath)
            self.joinsBodyNET._make_predict_function()
  
    def initializeDevice(self, device):
        """ Initialize device """
        capture = cv2.VideoCapture(device['id'])
        _width = Misc.hasKey(device, 'width', self.ME_CONFIG['FRAME_WIDTH'])
        _height = Misc.hasKey(device, 'height', self.ME_CONFIG['FRAME_HEIGHT'])
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, _width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, _height)
        return capture

    def getData(self, device, frame=None):
        """ Returns a list of Data objects """

        cam = self.Devices[device["id"]]['objOfCapture']
        if frame is None:
            _, frame = cam.read()

        if frame is None:
            return []

        height = np.size(frame, 0)
        width = np.size(frame, 1)
        deviceName = Misc.hasKey(device, 'name', device["id"])

        dataReturn = []
        auxData = '"t":"{}", "ext":"{}", "W":"{}", "H":"{}"'
        
        if self.getRGB:
            dataRgb = Data()
            dataRgb.source_type = self.ME_TYPE
            dataRgb.source_name = self.ME_NAME
            dataRgb.source_item = deviceName
            #dataRgb.data = frame
            dataRgb.data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            dataRgb.aux = '{' + auxData.format('image', 'png', width, height) + '}'
            dataReturn.append(dataRgb)
        
        if self.getGray:
            dataGray = Data()
            dataGray.source_type = self.ME_TYPE
            dataGray.source_name = self.ME_NAME + '/Gray'
            dataGray.source_item = deviceName
            dataGray.data = self.preProcGray(frame)
            dataGray.aux = '{' + auxData.format('image', 'png', width, height) + '}'
            dataReturn.append(dataGray)

        if self.getObject:
            auxPer = auxData.format('image', 'png', width, height)
            auxPer += ',"ClassName":"{}", "backColor":{}, "Y1":{}, "X1":{}, "Y2":{}, "X2":{}'
            objs = self.preProcObject(frame)
            for obj in objs:
                dataPerson = Data()
                dataPerson.source_type = self.ME_TYPE
                dataPerson.source_name = self.ME_NAME + '/Person'
                dataPerson.source_item = deviceName
                dataPerson.data = obj.Mask
                dataPerson.aux = '{' + auxPer.format(obj.ClassName, obj.backColor, obj.Y1, obj.X1, obj.Y2, obj.X2) + '}'
                dataReturn.append(dataPerson)

        if self.getSkeleton and not self.joinsBodyNET is None:
            dataSkeleton = Data()
            dataSkeleton.source_type = self.ME_TYPE
            dataSkeleton.source_name = self.ME_NAME + '/Skeleton'
            dataSkeleton.source_item = deviceName            
            dataSkeleton.data = self.preProcSkeleton(frame)
            dataSkeleton.aux = '{' + auxData.format('csv', 'csv', width, height) + '}'
            dataReturn.append(dataSkeleton)
        
        return dataReturn
  
    def showData(self, data:Data):
        """ To show data if this module start standalone """
        
        if data.source_name == self.ME_NAME + '/Skeleton':
            people = data.data #Points of skeleton
            aux = data.strToJSon(data.aux)
            h = int(Misc.hasKey(aux, 'H',self.ME_CONFIG['FRAME_HEIGHT']))
            w = int(Misc.hasKey(aux, 'W',self.ME_CONFIG['FRAME_WIDTH']))
            rgbImage = np.zeros((h, w, 3), np.uint8)            
            for person in people:
                for idj, join in enumerate(person):
                    if join[0] != None:
                        cv2.circle(rgbImage, (join[0], join[1]), 5, self.colors[idj], thickness=-1)
        elif data.source_name == self.ME_NAME + '/Person':
            rgbImage = np.zeros( (data.data.shape[0], data.data.shape[1], 3), dtype=np.uint8)
            rgbImage[:,:,0] = np.where(data.data[:,:] == 1, 255, 0 )
            rgbImage[:,:,1] = np.where(data.data[:,:] == 1, 255, 0 )
            rgbImage[:,:,2] = np.where(data.data[:,:] == 1, 255, 0 )            
        else:
            rgbImage = data.data # For capture the image in RGB color space
        
        # Display the resulting frame
        cv2.imshow(data.source_name + '-' + data.source_item, cv2.cvtColor(rgbImage, cv2.COLOR_BGR2RGB))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
            cv2.destroyAllWindows()

        #with open("M:/tmp/HM-SimulatingData/CamController_OutPut.txt",'a+') as file:
        #    file.write('\n' + data.toString(False, True))

    def simulateData(self, dataFilter:Data):
        """ Allows simulate input data """        
        if self.simulationStep == 0:
            self.capture = cv2.VideoCapture(self.SimulatingPath)
            self.video_length = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            
        if self.capture.isOpened() and self.simulationStep < self.video_length:
            _, frame = self.capture.read()
            self.simulationStep += 1
            sleep(1)
            if frame is None:
                return []
            return self.getData(dataFilter.source_item, frame=frame)
        else:
            self.simulationStep = 0
            return self.simulateData(dataFilter.source_item)

    # =========== Auxiliar methods =========== #

    def preProcGray(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def preProcObject(self, frame):
        return self.cce.locatePeople(frame)
        #Detections = self.cce.locatePeople(frame)
        #for d in Detections:
        #    img =  np.zeros((d.Frame.shape[0], d.Frame.shape[1]), dtype=int)
        #    img[:,:] = np.where(d.Frame[:,:,0] == d.backColor[0], 1 , 0)
        #    img[:,:] += np.where(d.Frame[:,:,1] == d.backColor[1], 1 , 0)
        #    img[:,:] += np.where(d.Frame[:,:,2] == d.backColor[2], 1 , 0)
        #    img[:,:] = np.where(img[:,:] == 3, 0 , 1)
        #    d.Frame = d.Mask
        #return Detections      

    def preProcSkeleton(self, frame):

        oriImg = frame  # B,G,R order
        scale_search = [0.22, .5] #,0.25,.5, 1, 1.5, 2]
        multiplier = [x * 368 / oriImg.shape[0] for x in scale_search]

        heatmap_avg = np.zeros((oriImg.shape[0], oriImg.shape[1], 19))
        paf_avg = np.zeros((oriImg.shape[0], oriImg.shape[1], 38))
        stride = 8
        thre2 = 0.05

        for m in range(len(multiplier)):
            scale = multiplier[m]
    
            imageToTest = cv2.resize(oriImg, (0, 0), 
                fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

            imageToTest_padded, pad = self.padRightDownCorner(imageToTest)
            input_img = np.transpose(np.float32(imageToTest_padded[:,:,:,np.newaxis]), (3,0,1,2)) # required shape (1, width, height, channels)
            output_blobs = self.joinsBodyNET.predict(input_img)
      
            # extract outputs, resize, and remove padding
            heatmap = np.squeeze(output_blobs[1])  # output 1 is heatmaps
            heatmap = cv2.resize(heatmap, (0, 0), fx=stride, fy=stride,
                                interpolation=cv2.INTER_CUBIC)
            heatmap = heatmap[:imageToTest_padded.shape[0] - pad[2], :imageToTest_padded.shape[1] - pad[3],:]
            heatmap = cv2.resize(heatmap, (oriImg.shape[1], oriImg.shape[0]), interpolation=cv2.INTER_CUBIC)

            paf = np.squeeze(output_blobs[0])  # output 0 is PAFs
            paf = cv2.resize(paf, (0, 0), fx=stride, fy=stride,
                            interpolation=cv2.INTER_CUBIC)
            paf = paf[:imageToTest_padded.shape[0] - pad[2], :imageToTest_padded.shape[1] - pad[3], :]
            paf = cv2.resize(paf, (oriImg.shape[1], oriImg.shape[0]), interpolation=cv2.INTER_CUBIC)

            heatmap_avg = heatmap_avg + heatmap / len(multiplier)
            paf_avg = paf_avg + paf / len(multiplier)

        all_peaks = []
        peak_counter = 0
    
        for part in range(18):
            map_ori = heatmap_avg[:, :, part]
            map = gaussian_filter(map_ori, sigma=3)
            thre1 = 0.7
            
            map_left = np.zeros(map.shape)
            map_left[1:, :] = map[:-1, :]
            map_right = np.zeros(map.shape)
            map_right[:-1, :] = map[1:, :]
            map_up = np.zeros(map.shape)
            map_up[:, 1:] = map[:, :-1]
            map_down = np.zeros(map.shape)
            map_down[:, :-1] = map[:, 1:]
    
            peaks_binary = np.logical_and.reduce(
                (map >= map_left, map >= map_right, map >= map_up, map >= map_down, map > thre1))
            
            #peaks_binary = np.logical_and.reduce((map > thre1, map > thre1))
            
            peaks = list(zip(np.nonzero(peaks_binary)[1], np.nonzero(peaks_binary)[0]))  # note reverse
            peaks_with_score = [x + (map_ori[x[1], x[0]],) for x in peaks]
            id = range(peak_counter, peak_counter + len(peaks))
            peaks_with_score_and_id = [peaks_with_score[i] + (id[i],) for i in range(len(id))]
    
            all_peaks.append(peaks_with_score_and_id)
            peak_counter += len(peaks)

        connection_all = []
        special_k = []
        mid_num = 10

        # find connection in the specified sequence, center 29 is in the position 15
        limbSeq = [[2, 3], [2, 6], [3, 4], [4, 5], [6, 7], [7, 8], [2, 9], [9, 10], \
                [10, 11], [2, 12], [12, 13], [13, 14], [2, 1], [1, 15], [15, 17], \
                [1, 16], [16, 18], [3, 17], [6, 18]]

        # the middle joints heatmap correpondence
        mapIdx = [[31, 32], [39, 40], [33, 34], [35, 36], [41, 42], [43, 44], [19, 20], [21, 22], \
            [23, 24], [25, 26], [27, 28], [29, 30], [47, 48], [49, 50], [53, 54], [51, 52], \
            [55, 56], [37, 38], [45, 46]]

        for k in range(len(mapIdx)):
            score_mid = paf_avg[:, :, [x - 19 for x in mapIdx[k]]]
            candA = all_peaks[limbSeq[k][0] - 1]
            candB = all_peaks[limbSeq[k][1] - 1]
            nA = len(candA)
            nB = len(candB)
            indexA, indexB = limbSeq[k]
            if (nA != 0 and nB != 0):
                connection_candidate = []
                for i in range(nA):
                    for j in range(nB):
                        vec = np.subtract(candB[j][:2], candA[i][:2])
                        norm = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
                        # failure case when 2 body parts overlaps
                        if norm == 0:
                            continue
                        vec = np.divide(vec, norm)

                        startend = list(zip(np.linspace(candA[i][0], candB[j][0], num=mid_num), \
                                    np.linspace(candA[i][1], candB[j][1], num=mid_num)))

                        vec_x = np.array(
                            [score_mid[int(round(startend[I][1])), int(round(startend[I][0])), 0] \
                            for I in range(len(startend))])
                        vec_y = np.array(
                            [score_mid[int(round(startend[I][1])), int(round(startend[I][0])), 1] \
                            for I in range(len(startend))])

                        score_midpts = np.multiply(vec_x, vec[0]) + np.multiply(vec_y, vec[1])
                        score_with_dist_prior = sum(score_midpts) / len(score_midpts) + min(
                            0.5 * oriImg.shape[0] / norm - 1, 0)
                        criterion1 = len(np.nonzero(score_midpts > thre2)[0]) > 0.8 * len(
                            score_midpts)
                        criterion2 = score_with_dist_prior > 0
                        if criterion1 and criterion2:
                            connection_candidate.append([i, j, score_with_dist_prior,
                                                        score_with_dist_prior + candA[i][2] + candB[j][2]])

                connection_candidate = sorted(connection_candidate, key=lambda x: x[2], reverse=True)
                connection = np.zeros((0, 5))
                for c in range(len(connection_candidate)):
                    i, j, s = connection_candidate[c][0:3]
                    if (i not in connection[:, 3] and j not in connection[:, 4]):
                        connection = np.vstack([connection, [candA[i][3], candB[j][3], s, i, j]])
                        if (len(connection) >= min(nA, nB)):
                            break

                connection_all.append(connection)
            else:
                special_k.append(k)
                connection_all.append([])

        # last number in each row is the total parts number of that person
        # the second last number in each row is the score of the overall configuration
        subset = -1 * np.ones((0, 20))
        candidate = np.array([item for sublist in all_peaks for item in sublist])

        for k in range(len(mapIdx)):
            if k not in special_k:
                partAs = connection_all[k][:, 0]
                partBs = connection_all[k][:, 1]
                indexA, indexB = np.array(limbSeq[k]) - 1

                for i in range(len(connection_all[k])):  # = 1:size(temp,1)
                    found = 0
                    subset_idx = [-1, -1]
                    for j in range(len(subset)):  # 1:size(subset,1):
                        if subset[j][indexA] == partAs[i] or subset[j][indexB] == partBs[i]:
                            subset_idx[found] = j
                            found += 1

                    if found == 1:
                        j = subset_idx[0]
                        if (subset[j][indexB] != partBs[i]):
                            subset[j][indexB] = partBs[i]
                            subset[j][-1] += 1
                            subset[j][-2] += candidate[partBs[i].astype(int), 2] + connection_all[k][i][2]
                    elif found == 2:  # if found 2 and disjoint, merge them
                        j1, j2 = subset_idx
                        membership = ((subset[j1] >= 0).astype(int) + (subset[j2] >= 0).astype(int))[:-2]
                        if len(np.nonzero(membership == 2)[0]) == 0:  # merge
                            subset[j1][:-2] += (subset[j2][:-2] + 1)
                            subset[j1][-2:] += subset[j2][-2:]
                            subset[j1][-2] += connection_all[k][i][2]
                            subset = np.delete(subset, j2, 0)
                        else:  # as like found == 1
                            subset[j1][indexB] = partBs[i]
                            subset[j1][-1] += 1
                            subset[j1][-2] += candidate[partBs[i].astype(int), 2] + connection_all[k][i][2]

                    # if find no partA in the subset, create a new subset
                    elif not found and k < 17:
                        row = -1 * np.ones(20)
                        row[indexA] = partAs[i]
                        row[indexB] = partBs[i]
                        row[-1] = 2
                        row[-2] = sum(candidate[connection_all[k][i, :2].astype(int), 2]) + \
                                connection_all[k][i][2]
                        subset = np.vstack([subset, row])

        # delete some rows of subset which has few parts occur
        deleteIdx = []
        for i in range(len(subset)):
            if subset[i][-1] < 4 or subset[i][-2] / subset[i][-1] < 0.4:
                deleteIdx.append(i)
        subset = np.delete(subset, deleteIdx, axis=0)

        # Construct each person
        people = []
        for i in range(len(subset)):
            #if subset[i][1] == -1: # No neck
            #    continue
            #if subset[i][0] == -1: # No nose
            #    continue
            #if subset[i][2] == -1 and subset[i][5] == -1 : #No shoulders
            #    continue
            #if subset[i][4] == -1 and subset[i][7] == -1 : #No hands/Wrist
            #    continue
            person = []
            for j in range(18): # 18 connections
                    
                #'Nose','Neck','RShoulder','RElbow','RWrist','LShoulder','LElbow','LWrist',
                #'RHip','RKnee','RAnkle','LHip','LKnee','LAnkle','REye','LEye','REar','LEar'

                if subset[i][j] > -1:
                    point = list(filter(lambda x: x[3:4] == subset[i][j], all_peaks[j]))                
                else:
                    point = [(None, None)] # If points are not detected
                    
                x, y = point[0][0:2]
                person.append((x, y))
            
            people.append(person)

        people = np.array(people)

        return people

    def padRightDownCorner(self, img, stride=8, padValue=128):
        h = img.shape[0]
        w = img.shape[1]
    
        pad = 4 * [None]
        pad[0] = 0 # up
        pad[1] = 0 # left
        pad[2] = 0 if (h%stride==0) else stride - (h % stride) # down
        pad[3] = 0 if (w%stride==0) else stride - (w % stride) # right
    
        img_padded = img
        pad_up = np.tile(img_padded[0:1,:,:]*0 + padValue, (pad[0], 1, 1))
        img_padded = np.concatenate((pad_up, img_padded), axis=0)
        pad_left = np.tile(img_padded[:,0:1,:]*0 + padValue, (1, pad[1], 1))
        img_padded = np.concatenate((pad_left, img_padded), axis=1)
        pad_down = np.tile(img_padded[-2:-1,:,:]*0 + padValue, (pad[2], 1, 1))
        img_padded = np.concatenate((img_padded, pad_down), axis=0)
        pad_right = np.tile(img_padded[:,-2:-1,:]*0 + padValue, (1, pad[3], 1))
        img_padded = np.concatenate((img_padded, pad_right), axis=1)
    
        return img_padded, pad

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = CamController()
    comp.setLoggingSettings(LogTypes.DEBUG)
    comp.init_standalone(path=dirname(__file__))
    sleep(600)
