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

sys.path.insert(0, './Core/')
from InputDataController import InputDataController


class CamController(InputDataController):
    """ Class to get RGB data from cams """
    NOMBRE = '' #TODO: ver standar de manejo de nombre y versión 
    VERSION = ''

    def __init__(self, cfg, device_id):
        """ Inicializa la clase cargando las variables de configuración """
        self.id = device_id
        self.running = False
        self.capture = cv2.VideoCapture(self.id)
        # these 2 lines can be removed if you dont have a 1080p camera.
        #self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        #self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def getDeviceList(self):
        """ Método que retorna el listado de dispositivos disponibles """
        return [0]

    def getData(self):
        """ Método que retorna la información capturada y en estructura conocida """
        ret, frame = self.capture.read()
        return ret, frame

    def start(self, func):
        """ Función que invocara el sistema para que el módulo inicie """
        self.running = True
        while self.running:
            func(self.getData())

        
    def stop(self):
        """ Función que invocara el sistema para detener cualquier funcionamiento del módulo y descargar la memoria ocupada """


    def imprime(self):
        print('yyy')

if __name__ == "__main__":
    c = CamController(None, None)
    c.imprime()
    #c.super().imprime()