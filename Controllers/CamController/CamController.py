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
#import cv2  #pip install opencv-python
from cv2 import cv2
import numpy as np
from time import time, sleep
import logging


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
        logging.basicConfig(
            level=logging.INFO,
            #filename='{}.log'.format(str(tm.tm_year) + '%02d' % tm.tm_mon + '%02d' % tm.tm_mday), 
            #filemode='w', 
            format='%(name)s - %(levelname)s - %(message)s')
            
        self.running = True
        self.Devices = self.getDeviceList()

        for c in range(len(self.Devices)):
            capture = cv2.VideoCapture(self.Devices[c]['id'])
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
            self.Devices[c]['cam'] = capture

        logging.debug('Reading cams')
        while self.running:
            for d in self.Devices:
                try:
                    gdList = self.getData(d['id'])
                except:
                    logging.exception("Unexpected Readding data fom device: " + str(self.Devices[d['id']]['cam']))
                    self.Devices.remove(self.Devices[d])
                    break
            
                for gd in gdList:
                    self.send(gd['controller'], gd['device'], gd['data'])

            sleep(self.sampling)

    def stop(self):
        """ Stop module and getting data """
        #cv2.stop()
        self.running = False

    def getDeviceList(self):
        """ Returns a list of devices able to read """
        cams = []
        cams.append({
            'id':0,
            'cam':None
        })
        
        cams.append({
            'id':1,
            'cam':None
        })
        
        return cams

    def getData(self, idDevice):
        """ Returns a list of tuples like {controller, device, data} with data elements """

        cam = self.Devices[idDevice]['cam']
        ret, frame = cam.read()

        deviceName = 'Trasera' if idDevice == 1 else 'Delantera'

        dataReturn = []

        dataReturn.append({
            'controller': 'CamController',
            'device': deviceName,
            'data': self.dp.serialize(frame),
        })
        
        dataReturn.append({
            'controller': 'CamController/Gray',
            'device': deviceName,
            'data': self.dp.serialize(self.preProcc_Gray(frame)),
        })
        
        dataReturn.append({
            'controller': 'CamController/Person',
            'device': deviceName,
            'data': self.dp.serialize(self.preProcc_Person(frame)),
        })

        dataReturn.append({
            'controller': 'CamController/Skeleton',
            'device': deviceName,
            'data': self.dp.serialize(self.preProcc_Skeleton(frame)),
        })
        

        return dataReturn


    def preProcc_Gray(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray

    def preProcc_Person(self, frame):
        sleep(1)
        return frame

    def preProcc_Skeleton(self, frame):
        sleep(1)
        return frame

if __name__ == "__main__":
    capture = cv2.VideoCapture(1)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
    while(True):
        # Capture frame-by-frame
        ret, frame = capture.read()
        #serialized = pickle.dumps(frame, protocol=0) # protocol 0 is printable ASCII
        #frame = pickle.loads(serialized)
        
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #For capture image in monochrome
        rgbImage = frame #For capture the image in RGB color space
        # Display the resulting frame
        cv2.imshow('Webcam',rgbImage)        
        #Wait to press 'q' key for capturing
        if cv2.waitKey(1) & 0xFF == ord('q'):
            #cv2.imwrite('img.png',frame)
            break
	
    # When everything done, release the capture
    print(capture)
    capture.release()
    print(capture)
    cv2.destroyAllWindows()