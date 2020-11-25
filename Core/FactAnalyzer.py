"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Generic class that represents all the analyzers that can be loaded.
"""

if __name__ == "__main__":
    print('\n\tAlert!! This class can not start itself. Please start using main.py file.')
    exit(0)

import sys
from os.path import dirname, normpath
from multiprocessing import Process, Queue, Value
from time import time, sleep
import abc

import Misc
from Component import Component
from DataPool import Data, Messages, LogTypes, SourceTypes
from LoaderOfChannel import LoaderOfChannel

class FactAnalyzer(Component):
    """ Generic class that represents all the analyzers that can be loaded. """
    MODEL = None
    CLASSES = []
    DATA_FILTER = Data()
    Limit:int = -1
    LastTime:float = -1
    LoaderOfChannelsThread:Process = None
    queueMessages:Queue = None

    def start(self):
        """ Start module isolated """
        self.DATA_FILTER.id = None
        self.DATA_FILTER.package = Misc.hasKey(self.ME_CONFIG, 'FILTER_PACKAGE', '')
        self.DATA_FILTER.source_type = SourceTypes.RECOGNIZER
        self.DATA_FILTER.source_name = Misc.hasKey(self.ME_CONFIG, 'FILTER_NAME', '')
        self.DATA_FILTER.source_item = Misc.hasKey(self.ME_CONFIG, 'FILTER_ITEM', '')
        self.Limit = Misc.hasKey(self.ME_CONFIG, 'FILTER_LIMIT', -1)
        self.CLASSES = Misc.hasKey(self.ME_CONFIG, 'CLASSES', [])

        self.setLoggingSettings(self.loggingLevel)

        self.preLoad()
        self.loadModel()
        self.loadChannels()
        self.loaded()
        
        self.running = True
        failedSend = 0
        lastAnalizedTime = time() - 60

        while self.running:

            gdList = []
            try:
                if self.Simulating:
                    gdList = self.simulateData(self.DATA_FILTER)
                else:
                    gdList = self.receive(self.DATA_FILTER, limit=self.Limit, lastTime=self.LastTime)

                self.LastTime = float(gdList[0]['queryTime'])
            except:
                self.log(self.CP.errorDetail(Messages.analyzer_error_get), LogTypes.ERROR)

            auxData = '"t":"json", \
                "source_id":"{}", "source_type":"{}", "source_name":"{}", "source_item":"{}", \
                "source_package":"{}", "source_aux":"{}"'

            if time() - lastAnalizedTime > 60 * 1: # 1 minute
                dataNoEvent = Data()
                dataNoEvent.data = ''
                dataNoEvent.aux = '{"no_event":"no event", "source_aux":{"no_event":"no event"} }'
                gdList.append(dataNoEvent)

            for objData in gdList[1:]:
                try:
                    lastAnalizedTime = time()
                    t0 = time()
                    dataAnalizedList = self.analyze(objData)
                    self.log('Time elapsed to get prediction: ' + str(round(time() - t0, 4)), logType=LogTypes.DEBUG, item=self.ME_NAME)
                    #print('Time elapsed to get prediction: ' + str(round(time() - t0, 4)), end='\r')
                    for dataAnalized in dataAnalizedList:
                        dataAnalized.source_type = self.ME_TYPE
                        dataAnalized.source_name = self.ME_NAME
                        if dataAnalized.package == '' or dataAnalized.package == None:
                            dataAnalized.package = objData.package
                        if dataAnalized.aux == '' or dataAnalized.aux == None:
                            dataAnalized.aux = auxData.format(objData.id, 
                                objData.source_type, objData.source_name, objData.source_item,
                                dataAnalized.package, dataAnalized.aux)
                            dataAnalized.aux = '{' + dataAnalized.aux + '}'
                        
                        if self.ME_STANDALONE:
                            self.showData(dataAnalized, objData)
                        else:
                            print(time(),': Notifing a', dataAnalized.data)
                            self.notify(dataAnalized)
                            self.send(dataAnalized)
                        failedSend = 0
                except:
                    self.log(Messages.analyzer_error_send, LogTypes.ERROR)
                    failedSend += 1
                    if failedSend > 2:
                        self.stop()
                        break
        print(':o me sali')

    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Do anything necessary for processing """
        pass

    @abc.abstractmethod
    def loadModel(self):
        """ Loads model """
        raise ValueError('Implement me! :: Load the model')

    def loadChannels(self):
        """ Loads available channels """
        self.log(Messages.system_channels_start, LogTypes.INFO)
        loc = LoaderOfChannel(self.ME_CONFIG, self.CP)
        loc.ANALYZER_PATH = self.ME_PATH
        self.queueMessages = Queue()
        self.LoaderOfChannelsThread = Process(target=loc.start, args=(self.queueMessages,))
        self.LoaderOfChannelsThread.start()
        #del loc
        self.log(Messages.system_channels_started, LogTypes.INFO)

    @abc.abstractmethod
    def loaded(self):
        """  Implement me! :: Just after load the model """
        pass
    
    @abc.abstractmethod
    def analyze(self, data:Data):
        """ Implement me! :: Exec prediction to recognize an activity """
        raise ValueError('Implement me! :: Exec analyze of activity')

    def notify(self, data:Data):
        """ Send data to pool of messages to notify """
        self.queueMessages.put(data.toString(dataPlain=True,auxPlain=True))
