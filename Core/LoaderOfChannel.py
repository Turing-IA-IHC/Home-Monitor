"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to control all Channels to load in system.
"""

#import sys
import os
from os.path import normpath
#import logging
from time import sleep, time
from multiprocessing import Process, Queue, Value
import hashlib
#
import Misc, Formats
from Component import Component
from DataPool import Data, LogTypes, SourceTypes, Messages, CommPool
from CommChannel import CommChannel, Dispatch

class Carrier:
    """ Class to keep couple message and channel """
    born = time()                   # Momentun of creation
    sent = False                    # Turn to True when message was sent
    message : Dispatch              # Message to send
    channel : CommChannel           # Channel used to send message
    attempt : int = 0               # Failed Attempts
    def __init__(self, message : Dispatch, channel : CommChannel):
        self.message = message
        self.channel = channel
        self.born = time()

    def equals(self, carrier):
        """ Verify if two coarrier has a similar message throw same channel """
        return self.message.equals(carrier.message) and \
            self.channel.ME_PATH == carrier.channel.ME_PATH

class LoaderOfChannel:
    """ Class to control all Channels to load in system. """
    POOL_DISPATCHES = []            # List of messages to send
    ANALYZER_PATH   = "./"          # Path of current analyzer

    def __init__(self, config, commPool:CommPool):
        """ Initialize all variables """
        self.CONFIG = config
        self.COMMPOOL = commPool
        self.CHECKING_TIME = int(Misc.hasKey(self.CONFIG, 'CHECKING_TIME', 10)) # Time in seconds to check service availability
        self.channels = {}                  # List of channels
        self.authoraizedChannels = []       # List of authorized channels to notify
        self.authoraizedAttachments = []    # List of authorized attachments to notify

    def start(self, queueMessages:Queue):
        """ Start load of all device channels """
        self.COMMPOOL.logFromCore(Messages.system_channels_connect.format(self.COMMPOOL.URL_BASE), LogTypes.INFO, self.__class__.__name__)

        self.authoraizedChannels = Misc.hasKey(self.CONFIG,'AUTHORIZED_CHANNELS', [])
        self.authoraizedAttachments = Misc.hasKey(self.CONFIG,'AUTHORIZED_ATTACHMENTS', [])
        
        if not os.path.exists("./Channels"):
            os.makedirs("./Channels")
        if not os.path.exists(self.ANALYZER_PATH + "/attachments/"):
            os.makedirs(self.ANALYZER_PATH + "/attachments/")            

        while True:
            self.COMMPOOL.logFromCore(Messages.channel_searching, LogTypes.INFO, self.__class__.__name__)
            channelsFolders =  Misc.lsFolders("./Channels")
            for cf in channelsFolders:
                if not Misc.existsFile("config.yaml", cf):
                    continue

                config = Misc.readConfig(normpath(cf + "/config.yaml"))
                comp = Misc.hasKey(self.channels, cf, None)
                if comp == None or comp.ME_CHECK != hashlib.md5(str(config).encode('utf-8')).hexdigest():
                    comp = self.loadChannel(config, cf)
                    self.channels[cf] = comp
            
            for _ in range(self.CHECKING_TIME):
                if not queueMessages.empty():
                    msj = queueMessages.get()
                    self.putMessagePool(Data().parse(msj, True, True))

                for disp in self.POOL_DISPATCHES:
                    try:
                        if disp.sent:
                            if time() - disp.born > Misc.hasKey(self.CONFIG, 'MESSAGES_LIFE', 90): # Keep 90 seconds
                                self.POOL_DISPATCHES.remove(disp)
                        else:
                            disp.channel.notify(disp.message)
                            disp.sent = True
                            #del disp.message
                    except:
                        disp.attempt += 1
                        if disp.attempt > 2:
                            self.POOL_DISPATCHES.remove(disp)
                            del disp.message              

                sleep(1)

        self.COMMPOOL.logFromCore(Messages.channel_stop, LogTypes.INFO, self.__class__.__name__)

    def loadChannel(self, config, cf:str):
        """ Load channel objects """
        file_class = Misc.hasKey(config, 'FILE_CLASS', '')
        class_name = Misc.hasKey(config, 'CLASS_NAME', '')
        if file_class != '' and class_name != '': 
            _cls = Misc.importModule(cf, file_class, class_name)
            obj = _cls()
            obj.CONFIG =  config
            obj.ME_PATH = cf
            obj.COMMPOOL = self.COMMPOOL
            obj.ME_CHECK = hashlib.md5(str(obj.CONFIG).encode('utf-8')).hexdigest()
            obj.ENABLED = Misc.toBool(Misc.hasKey(obj.CONFIG, 'ENABLED', 'False'))
            obj.ME_TYPE = SourceTypes.parse(Misc.hasKey(obj.CONFIG, 'TYPE', None))
            obj.ME_NAME = Misc.hasKey(obj.CONFIG, 'NAME', class_name)
            return obj
        else:
            comp = Component()
            comp.ENABLED = False
            return comp

    def putMessagePool(self, data:Data):
        """ Put new messages into pool to send then """
        try:
            d = Dispatch()

            d.tokens = {}
            d.tickets = []
            d.events = []
            d.alerts = []
            d.files = []
            d.alerts.append(data)

            dataRecognizer = []
            auxAnalyzer = data.strToJSon(data.aux)
            filterRecognizer = Data()
            filterRecognizer.id = ''
            filterRecognizer.package = Misc.hasKey(auxAnalyzer, 'source_package', '-')
            filterRecognizer.source_type = SourceTypes.RECOGNIZER
            dataRecognizer = self.COMMPOOL.receive(data=filterRecognizer, limit=-1, lastTime=0, onlyActive=False)
            event = Data()
            for ev in dataRecognizer[1:]:
                event = Data().fromDict(ev)
                d.events.append(event)

            dataController = []
            auxRecognizer = event.strToJSon(event.aux)
            filterController = Data()
            filterController.id =  ''
            filterController.package = Misc.hasKey(auxRecognizer, 'source_package', '-')
            filterController.source_type = SourceTypes.CONTROLLER
            dataController = self.COMMPOOL.receive(data=filterController, limit=-1, lastTime=0, onlyActive=False)
            ticket = Data()
            for ti in dataController[1:]:
                ticket = Data().fromDict(ti)
                d.events.append(ticket)
                for attallow in self.authoraizedAttachments:
                    attsallow = attallow.split(':')
                    if len(attsallow) == 3 and \
                        (attsallow[0] == '*' or SourceTypes.parse(attsallow[0]) == ticket.source_type) and \
                        (attsallow[1] == '*' or attsallow[1] == ticket.source_name) and \
                        (attsallow[2] == '*' or attsallow[2] == ticket.source_item):
                        f = ticket.toFile(path="./" + self.ANALYZER_PATH)
                        if f != '':
                            d.files.append(f)

            # Tokens list            
            d.tokens['server_time'] =               time()
            d.tokens['server_time_human'] =         Misc.timeToString(time(), '%H:%M')
            d.tokens['analyzer_source_name'] =      data.source_name
            d.tokens['analysis_time'] =             data.born
            d.tokens['analysis_time_human'] =       Misc.timeToString(data.born, '%H:%M')
            d.tokens['analysis_phrase'] =           Misc.hasKey(Misc.hasKey(auxAnalyzer, 'source_aux', ''), 'phrase', '')
            d.tokens['analysis_data'] =             data.data
            d.tokens['analysis_aux'] =              data.aux
            d.tokens['analysis_id'] =               data.id
            d.tokens['event_data'] =                event.source_item 
            d.tokens['recognizer_source_id'] =      event.id
            d.tokens['recognizer_source_id_0'] =    event.id
            d.tokens['recognizer_source_id_1'] =    event.id
            d.tokens['recognizer_source_id_2'] =    event.id
            d.tokens['recognizer_source_name'] =    event.source_name
            d.tokens['recognizer_source_name_0'] =  event.source_name
            d.tokens['recognizer_source_name_1'] =  event.source_name
            d.tokens['recognizer_source_name_2'] =  event.source_name 
            d.tokens['recognizer_source_item'] =    event.source_item 
            d.tokens['recognizer_source_item_0'] =  event.source_item
            d.tokens['recognizer_source_item_1'] =  event.source_item
            d.tokens['recognizer_source_item_2'] =  event.source_item
            d.tokens['controller_source_id'] =      ticket.id 
            d.tokens['controller_source_id_0'] =    ticket.id 
            d.tokens['controller_source_id_1'] =    ticket.id 
            d.tokens['controller_source_id_2'] =    ticket.id 
            d.tokens['controller_source_name'] =    ticket.source_name 
            d.tokens['controller_source_name_0'] =  ticket.source_name 
            d.tokens['controller_source_name_1'] =  ticket.source_name 
            d.tokens['controller_source_name_2'] =  ticket.source_name 
            d.tokens['controller_source_item'] =    ticket.source_item
            d.tokens['controller_source_item_0'] =  ticket.source_item
            d.tokens['controller_source_item_1'] =  ticket.source_item
            d.tokens['controller_source_item_2'] =  ticket.source_item
            
            for c in self.channels:
                chnl = self.channels[c]
                if chnl.ENABLED:
                    if len(self.authoraizedChannels) > 0 and chnl.ME_NAME not in self.authoraizedChannels:
                        continue # Skip not authorized channels

                    msg = d.copy()                               
                    msg.to = Misc.hasKey(chnl.ME_CONFIG, 'TO', '')
                    msg.message = Misc.hasKey(chnl.ME_CONFIG, 'MESSAGE', '')
                    crr = Carrier(msg, chnl)
                    
                    existsCarrier = False
                    for crrDis in self.POOL_DISPATCHES:
                        if crrDis.equals(crr):
                            existsCarrier = True
                            break
                        else:
                            crrDis.equals(crr)
                    if not existsCarrier:
                        self.POOL_DISPATCHES.append(crr)                        
        except:
            dataE = Data()
            dataE.source_type = SourceTypes.ANALYZER
            dataE.source_name = 'LoaderOfChannel'
            dataE.source_item = ''
            dataE.data = self.COMMPOOL.errorDetail(Messages.channel_error_put_msg)
            dataE.aux = ''
            self.COMMPOOL.logFromCore(dataE, LogTypes.ERROR)