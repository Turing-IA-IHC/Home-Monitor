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
#from time import sleep
import abc

import Misc
from Component import Component
from DataPool import Data, Messages, LogTypes, SourceTypes
from LoaderOfChannel import LoaderOfChannel
class FactAnalyzer(Component):
    """ Generic class that represents all the analyzers that can be loaded. """
    MODEL = None
    DATA_FILTER = Data()
    limit:int = -1
    lastTime:float = -1
    LoaderOfChannelsThread:Process = None
    queueMessages:Queue = None
    
    CLASSES = []

    def start(self):
        """ Start module isolated """
        self.DATA_FILTER.id = None
        self.DATA_FILTER.package = Misc.hasKey(self.CONFIG, 'FILTER_PACKAGE', '')
        self.DATA_FILTER.source_type = SourceTypes.RECOGNIZER
        self.DATA_FILTER.source_name = Misc.hasKey(self.CONFIG, 'FILTER_NAME', '')
        self.DATA_FILTER.source_item = Misc.hasKey(self.CONFIG, 'FILTER_ITEM', '')
        self.limit = Misc.hasKey(self.CONFIG, 'FILTER_LIMIT', -1)
        self.CLASSES = Misc.hasKey(self.CONFIG, 'CLASSES', [])

        self.preLoad()
        self.loadModel()
        self.loadChannels()
        self.loaded()
        
        self.running = True
        failedSend = 0

        while self.running:

            # TODO: Ver hilo 
            #try:
            #    # Try to restart channels
            #    if self.LoaderOfChannelsThread == None or not self.LoaderOfChannelsThread.is_alive():
            #        self.loadChannels()
            #except:
            #    dataE = Data()
            #    dataE.source_type = SourceTypes.ANALYZER
            #    dataE.source_name = self.ME_NAME
            #    dataE.source_item = ''
            #    dataE.data = self.COMMPOOL.errorDetail(Messages.analyzer_error_Channels)
            #    dataE.aux = ''
            #    self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)

            gdList = []
            try:
                if Misc.toBool(self.STANDALONE):
                    gdList = self.simulateData(self.DATA_FILTER)
                else:
                    gdList = self.bring(self.DATA_FILTER, self.limit, self.lastTime)

                self.LastTime = float(gdList[0]['queryTime'])
            except:
                dataE = Data()
                dataE.source_type = SourceTypes.ANALYZER
                dataE.source_name = self.ME_NAME
                dataE.source_item = ''
                dataE.data = self.COMMPOOL.errorDetail(Messages.analyzer_error_get)
                dataE.aux = ''
                self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)

            for data in gdList[1:]:
                try:
                    package = Misc.randomString()
                    objData = Data().fromDict(data)
                    dataAnalizedList = self.analyze(objData)
                    for dataAnalized in dataAnalizedList:
                        dataAnalized.package = package
                        auxData = '"t":"json", "source_id":"{}", "source_item":"{}", "source_name":"{}", "source_type":"{}", "source_package":"{}","source_aux":{}'
                        dataAnalized.aux = '{' + auxData.format(objData.id, objData.source_item, objData.source_name, objData.source_type, objData.package, dataAnalized.aux) + '}'

                        if Misc.toBool(self.STANDALONE):
                            self.showData(dataAnalized, objData)
                        else:
                            self.notify(dataAnalized)
                        failedSend = 0
                except:
                    dataE = Data()
                    dataE.source_type = SourceTypes.ANALYZER
                    dataE.source_name = self.ME_NAME
                    dataE.source_item = ''
                    dataE.data = self.COMMPOOL.errorDetail(Messages.analyzer_error_send)
                    dataE.aux = ''
                    self.COMMPOOL.logFromComponent(dataE, LogTypes.ERROR)

                    failedSend += 1

                    if failedSend > 2 and (Misc.toBool(self.STANDALONE) or not self.COMMPOOL.isLive()):
                        dataE = Data()
                        dataE.source_type = SourceTypes.ANALYZER
                        dataE.source_name = self.ME_NAME
                        dataE.source_item = ''
                        dataE.data = Messages.analyzer_error_stop
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

    def loadChannels(self):
        """ Loads available channels """
        self.COMMPOOL.logFromCore(Messages.system_channels_start, LogTypes.INFO, self.__class__.__name__)
        loc = LoaderOfChannel(self.CONFIG, self.COMMPOOL)
        loc.ANALYZER_PATH = self.ME_PATH
        self.queueMessages = Queue()
        self.LoaderOfChannelsThread = Process(target=loc.start, args=(self.queueMessages,))
        self.LoaderOfChannelsThread.start()
        del loc
        self.COMMPOOL.logFromCore(Messages.system_channels_started, LogTypes.INFO, self.__class__.__name__)

    @abc.abstractmethod
    def loaded(self):
        """  Implement me! :: Just after load the model """
        pass
    
    def bring(self, dataFilter:Data, limit:int=-1, lastTime:float=-1):
        """ Returns a list objects type Data from pool """
        return self.COMMPOOL.receive(dataFilter, limit=limit, lastTime=lastTime)

    @abc.abstractmethod
    def analyze(self, data:Data):
        """ Implement me! :: Exec prediction to recognize an activity """
        pass

    def notify(self, data:Data):
        """ Send data to pool of messages to notify """
        self.queueMessages.put(data.toString(dataPlain=True,auxPlain=True))

    def stop(self):
        """ Stop module and getting data """
        self.running = False

    @abc.abstractmethod
    def showData(self, dataAnalized:Data, dataSource:Data):
        """  Implement me! :: To show data if this module start standalone """
        pass

    @abc.abstractmethod
    def simulateData(self, device):
        """  Implement me! :: Allows to simulate data if this module start standalone """
        pass
