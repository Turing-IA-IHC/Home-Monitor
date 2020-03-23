"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the devices that can be loaded.
"""

if __name__ == "__main__":
    print('\n\tAlert!! This class can not start itself. Please start using main.py file.')
    exit(0)

import sys
from os.path import dirname, normpath
from time import sleep
import threading
import logging
import abc

import Misc
from Component import Component
from DataPool import Data, Messages, LogTypes, SourceTypes, CommPool

class DeviceController(Component):
    """ Generic class that represents all the devices that can be loaded. """ 
    Devices = []           # List of devices loaded
    InactiveDevices = []   # List of devices unpluged

    def start(self):
        """ Start module isolated """
        self.preLoad()
        self.Devices = self.getDeviceList()
        
        for device in self.Devices:
            device['objOfCapture'] = self.initializeDevice(device)
        
        self.running = True
        Sampling = Misc.hasKey(self.CONFIG, 'SAMPLING', 1) # Sampling rate
        failedSend = 0

        while self.running:

            for device in self.Devices:
                if device in self.InactiveDevices:
                    continue

                gdList = []
                try:
                        if Misc.toBool(self.STANDALONE):
                            gdList = self.simulateData(device)
                        else:
                            gdList = self.simulateData(device)
                            #gdList = self.getData(device)
                except:
                    dataE = Data()
                    dataE.source_type = SourceTypes.CONTROLLER
                    dataE.source_name = self.ME_NAME
                    dataE.source_item = Misc.hasKey(device, 'name', device['id'])
                    dataE.data = self.COMMPOOL.errorDetail(Messages.controller_error_get)
                    dataE.aux = '{}'.format(str(device['objOfCapture']))
                    self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)
                    self.InactiveDevices.append(device)
                    import threading
                    x = threading.Thread(target=self.checkDevice, args=(device,))
                    x.start()
            
                package = Misc.randomString()
                for data in gdList:
                    try:
                        data.package = package
                        if Misc.toBool(self.STANDALONE):
                            self.showData(data)
                        else:
                            self.send(data)
                        failedSend = 0
                    except:
                        dataE = Data()
                        dataE.source_type = SourceTypes.CONTROLLER
                        dataE.source_name = self.ME_NAME
                        dataE.source_item = Misc.hasKey(device, 'name', device['id'])
                        dataE.data = self.COMMPOOL.errorDetail(Messages.controller_error_send)
                        dataE.aux = '{}'.format(str(device['objOfCapture']))
                        self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)

                        failedSend += 1

                        if failedSend > 2 and (Misc.toBool(self.STANDALONE) or not self.COMMPOOL.isLive()):
                            dataE = Data()
                            dataE.source_type = SourceTypes.CONTROLLER
                            dataE.source_name = self.ME_NAME
                            dataE.source_item = Misc.hasKey(device, 'name', device['id'])
                            dataE.data = Messages.controller_error_stop
                            dataE.aux = '{}'.format(str(device['objOfCapture']))
                            self.COMMPOOL.logFromComponent(dataE, LogTypes.WARNING)
                            self.stop()
                            break

            sleep(Sampling)

    """ Abstract methods """
    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Load knowledge o whatever need for pre processing """
        pass

    @abc.abstractmethod
    def getDeviceList(self):
        """ Returns a list of devices able to read """
        devices = Misc.readConfig(normpath(self.ME_PATH) + "/devices.yaml")
        devices = devices['DEVICES']
        result = list(filter(lambda d: Misc.toBool(d['enabled']), devices))
        return result

    @abc.abstractmethod
    def initializeDevice(self, device):
        """  Implement me! :: Initialize device """
        pass
    
    @abc.abstractmethod
    def getData(self, device):
        """ Implement me! :: Returns a list of tuples like {controller, device, data} with data elements """
        pass

    def send(self, data:Data):
        """ Send data to pool """
        self.COMMPOOL.send(data)
    
    def checkDevice(self, device):
        """ Check if a device is on line again """
        for _ in range(30):
            try:
                thrs = threading.enumerate()
                if thrs[0]._is_stopped: # MainThread
                    break
                device['objOfCapture'] = self.initializeDevice(device)
                self.getData(device)
                self.InactiveDevices.remove(device)
                break
            except:
                pass

            sleep(int(Misc.hasKey(self.CONFIG, 'CHECKING_TIME', 10)))

    def stop(self):
        """ Stop module and getting data """
        self.running = False

    @abc.abstractmethod
    def showData(self, data:Data):
        """  Implement me! :: To show data if this module start standalone.
        call init_standalone before start. """
        pass
    @abc.abstractmethod
    def simulateData(self, device):
        """  Implement me! :: Allows to simulate data if this module start standalone.
        call init_standalone before start. """
        pass
