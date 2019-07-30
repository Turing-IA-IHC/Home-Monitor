"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to get RGB data from cams
"""

import sys
import cv2  #pip install opencv-python
import numpy as np
from time import time, sleep

sys.path.insert(0, './Core/')
from DeviceController import DeviceController

class CamController(DeviceController):
    """ Class to get RGB data from cams """
    NOMBRE = '' #TODO: ver standar de manejo de nombre y versión 
    VERSION = ''
    Devices = []

    #def __init__(self, cfg, device_id):
    #    """ Inicializa la clase cargando las variables de configuración """
    #    self.id = device_id
    #    self.running = False
    #    #self.capture = cv2.VideoCapture(self.id)
    #    # these 2 lines can be removed if you dont have a 1080p camera.
    #    #self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    #    #self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    def start(self):
        """ Start module and getting data """
        self.running = True
        self.Devices = self.getDeviceList()
        print('Leyendo de dispositivos....')
        #while self.running:
        #    for d in self.Devices:
        #        gdList = self.getData()
        #        for _controller, _device, _data in gdList:
        #            self.send(_controller, _device, _data)
        #    sleep(self.sampling)

    def stop(self):
        """ Stop module and getting data """
        #cv2.stop()
        self.running = False

    def getDeviceList(self):
        """ Returns a list of devices able to read """
        return [0]

    def getData(self):
        """ Implement me! :: Returns a list of tuples like {controller, device, data} with data elements """
        ret, frame = self.capture.read()

        dataReturn = []

        dataReturn.append({
            'controller': 'CamController',
            'device': '0',
            'data': frame,
        })

        dataReturn.append({
            'controller': 'CamController/BW',
            'device': '0',
            'data': self.prePross_BW(frame),
        })

        return dataReturn


    def prePross_BW(self, frame):
        return frame

    def prePross_Person(self, frame):
        return frame

    def prePross_Skeleton(self, frame):
        return frame