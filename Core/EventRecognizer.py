"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Generic class that represents all the activity recognizers modules that can be loaded.
"""

if __name__ == "__main__":
    print('\n\tAlert!! This class can not start itself. Please start using main.py file.')
    exit(0)

import sys
from os.path import dirname, normpath
from time import sleep, time
import abc

import Misc
from Component import Component
from DataPool import Data, Messages, LogTypes, SourceTypes, CommPool

class EventRecognizer(Component):
    """ Generic class that represents all the activity recognizers modules that can be loaded. """ 
    MODEL = None
    CLASSES = []
    DATA_FILTER = Data()
    Limit:int = -1
    LastTime:float = -1

    def start(self):
        """ Start module isolated """
        self.DATA_FILTER.id = None
        self.DATA_FILTER.package = Misc.hasKey(self.ME_CONFIG, 'FILTER_PACKAGE', '')
        self.DATA_FILTER.source_type = SourceTypes.CONTROLLER
        self.DATA_FILTER.source_name = Misc.hasKey(self.ME_CONFIG, 'FILTER_NAME', '')
        self.DATA_FILTER.source_item = Misc.hasKey(self.ME_CONFIG, 'FILTER_ITEM', '')
        self.Limit = Misc.hasKey(self.ME_CONFIG, 'FILTER_LIMIT', -1)
        self.CLASSES = Misc.hasKey(self.ME_CONFIG, 'CLASSES', [])

        self.setLoggingSettings(self.loggingLevel)

        self.preLoad()
        self.loadModel()
        self.loaded()
        
        self.running = True
        failedSend = 0

        while self.running:

            gdList = []
            try:
                if self.Simulating:
                    gdList = self.simulateData(self.DATA_FILTER)
                else:
                    gdList = self.receive(self.DATA_FILTER)
                    
                self.LastTime = float(gdList[0]['queryTime'])                    
            except:
                self.log(self.CP.errorDetail(Messages.recognizer_error_get), LogTypes.ERROR)

            auxData = '"t":"json", \
                "source_id":"{}", "source_type":"{}", "source_name":"{}", "source_item":"{}", \
                "source_aux":"{}"'

            for objData in gdList[1:]:
                try:
                    t0 = time()
                    dataPredictedList = self.predict(objData)
                    self.log('Time elapsed to get prediction: ' + str(round(time() - t0, 4)), logType=LogTypes.INFO, item= self.ME_NAME)
                    
                    for dataPredicted in dataPredictedList:
                        dataPredicted.source_type = self.ME_TYPE
                        dataPredicted.source_name = self.ME_NAME
                        dataPredicted.package = objData.package
                        dataPredicted.aux = auxData.format(objData.id, 
                            objData.source_type, objData.source_name, objData.source_item,
                            dataPredicted.aux)
                        dataPredicted.aux = '{' + dataPredicted.aux + '}'

                        if self.ME_STANDALONE:
                            self.showData(dataPredicted, objData)
                        else:
                            self.send(dataPredicted)
                        failedSend = 0
                except:
                    self.log(Messages.recognizer_error_send, LogTypes.ERROR)
                    failedSend += 1
                    if failedSend > 2:
                        self.stop()
                        break

    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        pass

    @abc.abstractmethod
    def loadModel(self):
        """ Load the model """
        raise ValueError('Implement me! :: Load the model')

    @abc.abstractmethod
    def loaded(self):
        """  Implement me! :: Just after load the model """
        pass
    
    @abc.abstractmethod
    def predict(self, data:Data):
        raise ValueError('Implement me! :: Exec prediction to recognize an activity')
