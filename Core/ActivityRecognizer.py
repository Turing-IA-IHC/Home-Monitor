"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the activity recognizers modules that can be loaded.
"""

if __name__ == "__main__":
    print('\n\tAlert!! This class can not start itself. Please start using main.py file.')
    exit(0)

import sys
from os.path import dirname, normpath
from time import sleep
import abc

import Misc
from Component import Component
from DataPool import Data, Messages, LogTypes, SourceTypes, CommPool

class ActivityRecognizer(Component):
    """ Generic class that represents all the activity recognizers modules that can be loaded. """ 
    MODEL = None
    DATA_FILTER = Data()
    Limit:int = -1
    LastTime:float = -1
    CLASSES = []

    def start(self):
        """ Start module isolated """
        self.DATA_FILTER.id = None
        self.DATA_FILTER.package = Misc.hasKey(self.CONFIG, 'FILTER_PACKAGE', '')
        self.DATA_FILTER.source_type = SourceTypes.CONTROLLER
        self.DATA_FILTER.source_name = Misc.hasKey(self.CONFIG, 'FILTER_NAME', '')
        self.DATA_FILTER.source_item = Misc.hasKey(self.CONFIG, 'FILTER_ITEM', '')
        self.Limit = Misc.hasKey(self.CONFIG, 'FILTER_LIMIT', -1)
        self.CLASSES = Misc.hasKey(self.CONFIG, 'CLASSES', [])

        self.preLoad()
        self.loadModel()
        self.loaded()
        
        self.running = True
        failedSend = 0

        while self.running:

            gdList = []
            try:
                if Misc.toBool(self.STANDALONE):
                    gdList = self.simulateData(self.DATA_FILTER)
                else:
                    #gdList = self.simulateData(self.DATA_FILTER)
                    gdList = self.bring(self.DATA_FILTER)

                self.LastTime = float(gdList[0]['queryTime'])                    
            except:
                dataE = Data()
                dataE.source_type = SourceTypes.RECOGNIZER
                dataE.source_name = self.ME_NAME
                dataE.source_item = ''
                dataE.data = self.COMMPOOL.errorDetail(Messages.recognizer_error_get)
                dataE.aux = ''
                self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)

            for data in gdList[1:]:
                try:
                    package = Misc.randomString()
                    objData = Data().fromDict(data)
                    dataPredictedList = self.predict(objData)
                    for dataPredicted in dataPredictedList:
                        dataPredicted.package = package
                        auxData = '"t":"json", "source_id":"{}", "source_item":"{}", "source_name":"{}", "source_type":"{}", "source_package":"{}","source_aux":"{}"'
                        dataPredicted.aux = '{' + auxData.format(objData.id, objData.source_item, objData.source_name, objData.source_type, objData.package, dataPredicted.aux) + '}'

                        if Misc.toBool(self.STANDALONE):
                            self.showData(dataPredicted, objData)
                        else:
                            self.send(dataPredicted)
                        failedSend = 0
                except:
                    dataE = Data()
                    dataE.source_type = SourceTypes.RECOGNIZER
                    dataE.source_name = self.ME_NAME
                    dataE.source_item = ''
                    dataE.data = self.COMMPOOL.errorDetail(Messages.recognizer_error_send)
                    dataE.aux = ''
                    self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)

                    failedSend += 1

                    if failedSend > 2 and (Misc.toBool(self.STANDALONE) or not self.COMMPOOL.isLive()):
                        dataE = Data()
                        dataE.source_type = SourceTypes.RECOGNIZER
                        dataE.source_name = self.ME_NAME
                        dataE.source_item = ''
                        dataE.data = Messages.recognizer_error_stop
                        dataE.aux = ''
                        self.COMMPOOL.logFromComponent(dataE, LogTypes.WARNING)
                        self.stop()
                        break

    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        pass

    @abc.abstractmethod
    def loadModel(self):
        """ Loads model """
        pass

    @abc.abstractmethod
    def loaded(self):
        """  Implement me! :: Just after load the model """
        pass
    
    def bring(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Returns a list objects type Data from pool """
        return self.COMMPOOL.receive(dataFilter, limit=limit, lastTime=lastTime)

    @abc.abstractmethod
    def predict(self, data:Data):
        """ Implement me! :: Exec prediction to recognize an activity """
        pass

    def send(self, data:Data):
        """ Send data to pool """
        self.COMMPOOL.send(data)

    def stop(self):
        """ Stop module and getting data """
        self.running = False

    @abc.abstractmethod
    def showData(self, dataPredicted:Data, dataSource:Data):
        """  Implement me! :: To show data if this module start standalone """
        pass

    @abc.abstractmethod
    def simulateData(self, device):
        """  Implement me! :: Allows to simulate data if this module start standalone """
        pass
