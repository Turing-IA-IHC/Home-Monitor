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
    NOMBRE = ''     #   TODO: ver standar de manejo de nombre y versión 
    VERSION = ''
        
    def start(self):
        """ Start module and getting data """
        self.activateLog()
            
        self.running = True
        self.Devices = self.getDeviceList()

        for c in range(len(self.Devices)):
            capture = self.initializeDevice(self.Devices[c])
            self.Devices[c]['cam'] = capture

        logging.debug('Reading cams')
        while self.running:
            for d in self.Devices:
                if d in self.InactiveDevices:
                    continue

                gdList = []
                try:
                    gdList = self.getData(d['id'])
                except:
                    logging.exception("Unexpected Readding data from device: " + str(self.Devices[d['id']]['cam']))
                    self.InactiveDevices.append(d)
                    import threading
                    x = threading.Thread(target=self.checkDevice, args=(d,))
                    x.start()
            
                for gd in gdList: # TODO: Try Catch
                    self.send(gd['controller'], gd['device'], gd['data'])

            sleep(self.Sampling)

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

    def initializeDevice(self, device):
        """ Initialize device """
        capture = cv2.VideoCapture(device['id'])
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.Config['FRAME_WIDTH'])
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.Config['FRAME_HEIGHT'])
        return capture

    def checkDevice(self, Device):
        """ Check if a device is online again """
        for _ in range(30):
            try:
                capture = self.initializeDevice(Device)
                Device['cam'] = capture
                self.getData(Device['id'])
                self.InactiveDevices.remove(Device)
                break
            except:
                pass

            sleep(30)

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