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
from time import sleep, time, localtime
from datetime import datetime, timedelta
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
        self.ME_CONFIG = config
        self.COMMPOOL = commPool
        self.CHECKING_TIME = int(Misc.hasKey(self.ME_CONFIG, 'CHECKING_TIME', 10)) # Time in seconds to check service availability
        self.channels = {}                  # List of channels
        self.authoraizedChannels = []       # List of authorized channels to notify
        self.authoraizedAttachments = []    # List of authorized attachments to notify

    def start(self, queueMessages:Queue):
        """ Start load of all device channels """
        self.COMMPOOL.logFromCore(Messages.system_channels_connect.format(self.COMMPOOL.URL_BASE), LogTypes.INFO, self.__class__.__name__)

        self.authoraizedChannels = Misc.hasKey(self.ME_CONFIG,'AUTHORIZED_CHANNELS', [])
        self.authoraizedAttachments = Misc.hasKey(self.ME_CONFIG,'AUTHORIZED_ATTACHMENTS', [])
        
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
                if comp == None or comp.Check != hashlib.md5(str(config).encode('utf-8')).hexdigest():
                    comp = self.loadChannel(config, cf)
                    self.channels[cf] = comp
            
            for _ in range(self.CHECKING_TIME):
                if not queueMessages.empty():
                    msj = queueMessages.get()
                    self.putMessagePool(Data().parse(msj, True, True))

                for disp in self.POOL_DISPATCHES:
                    try:
                        if disp.sent:
                            if time() - disp.born > Misc.hasKey(self.ME_CONFIG, 'MESSAGES_LIFE', 90): # Keep 90 seconds
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
            obj.ME_CONFIG =  config
            obj.ME_PATH = cf
            obj.COMMPOOL = self.COMMPOOL
            obj.ENABLED = Misc.toBool(Misc.hasKey(obj.ME_CONFIG, 'ENABLED', 'False'))
            obj.ME_TYPE = SourceTypes.parse(Misc.hasKey(obj.ME_CONFIG, 'TYPE', None))
            obj.ME_NAME = Misc.hasKey(obj.ME_CONFIG, 'NAME', class_name)
            obj.Check = hashlib.md5(str(obj.ME_CONFIG).encode('utf-8')).hexdigest()
            obj.preLoad()
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
            
            if len(dataRecognizer) == 0:
                return
            event = Data()
            for ev in dataRecognizer[1:]:
                #event = Data().fromDict(ev)
                d.events.append(ev)

            packages = []
            for ev in d.events:
                if not ev.package in packages:
                    packages.append(ev.package)

            for pck in packages:                
                dataController = []
                filterController = Data()
                filterController.id =  ''
                filterController.package = pck
                filterController.source_type = SourceTypes.CONTROLLER
                dataController = self.COMMPOOL.receive(data=filterController, limit=-1, lastTime=0, onlyActive=False)                
                for ticket in dataController[1:]:
                    d.tickets.append(ticket)
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
            t_s = time() - (5 * 60 * 60)
            data.born -= (5 * 60 * 60)
            d.tokens['server_time'] =               t_s
            d.tokens['server_time_human'] =         Misc.timeToString(t_s, '%H:%M')
            d.tokens['analyzer_source_name'] =      data.source_name
            d.tokens['analysis_time'] =             data.born
            d.tokens['analysis_time_human'] =       Misc.timeToString(data.born, '%H:%M')
            d.tokens['analysis_data'] =             data.data
            d.tokens['analysis_aux'] =              data.aux
            d.tokens['analysis_id'] =               data.id
            d.tokens['event_data'] =                data.data if len(d.events) == 0 else d.events[0].source_item 
            d.tokens['recognizer_source_id'] =      '' if len(d.events) == 0 else ','.join([str(x.id) for x in d.events])
            d.tokens['recognizer_source_id_0'] =    '' if len(d.events) == 0 else d.events[0].id if len(d.events) > 0 else ''
            d.tokens['recognizer_source_id_1'] =    '' if len(d.events) == 0 else d.events[1].id if len(d.events) > 1 else ''
            d.tokens['recognizer_source_id_2'] =    '' if len(d.events) == 0 else d.events[2].id if len(d.events) > 2 else ''
            d.tokens['recognizer_source_name'] =    '' if len(d.events) == 0 else ','.join([str(x.source_name) for x in d.events])
            d.tokens['recognizer_source_name_0'] =  '' if len(d.events) == 0 else d.events[0].source_name if len(d.events) > 0 else ''
            d.tokens['recognizer_source_name_1'] =  '' if len(d.events) == 0 else d.events[1].source_name if len(d.events) > 1 else ''
            d.tokens['recognizer_source_name_2'] =  '' if len(d.events) == 0 else d.events[2].source_name if len(d.events) > 2 else ''
            d.tokens['recognizer_source_item'] =    '' if len(d.events) == 0 else ','.join([str(x.source_item) for x in d.events])
            d.tokens['recognizer_source_item_0'] =  '' if len(d.events) == 0 else d.events[0].source_item if len(d.events) > 0 else ''
            d.tokens['recognizer_source_item_1'] =  '' if len(d.events) == 0 else d.events[1].source_item if len(d.events) > 1 else ''
            d.tokens['recognizer_source_item_2'] =  '' if len(d.events) == 0 else d.events[2].source_item if len(d.events) > 2 else ''
            d.tokens['controller_source_id'] =      '' if len(d.tickets) == 0 else ','.join([str(x.id) for x in d.tickets])
            d.tokens['controller_source_id_0'] =    '' if len(d.tickets) == 0 else d.tickets[0].id if len(d.tickets) > 0 else ''
            d.tokens['controller_source_id_1'] =    '' if len(d.tickets) == 0 else d.tickets[1].id if len(d.tickets) > 1 else ''
            d.tokens['controller_source_id_2'] =    '' if len(d.tickets) == 0 else d.tickets[2].id if len(d.tickets) > 2 else ''
            d.tokens['controller_source_name'] =    '' if len(d.tickets) == 0 else ','.join([str(x.source_name) for x in d.tickets])
            d.tokens['controller_source_name_0'] =  '' if len(d.tickets) == 0 else d.tickets[0].source_name if len(d.tickets) > 0 else ''
            d.tokens['controller_source_name_1'] =  '' if len(d.tickets) == 0 else d.tickets[1].source_name if len(d.tickets) > 1 else ''
            d.tokens['controller_source_name_2'] =  '' if len(d.tickets) == 0 else d.tickets[2].source_name if len(d.tickets) > 2 else ''
            d.tokens['controller_source_item'] =    '' if len(d.tickets) == 0 else ','.join([str(x.source_item) for x in d.tickets])
            d.tokens['controller_source_item_0'] =  '' if len(d.tickets) == 0 else d.tickets[0].source_item if len(d.tickets) > 0 else ''
            d.tokens['controller_source_item_1'] =  '' if len(d.tickets) == 0 else d.tickets[1].source_item if len(d.tickets) > 1 else ''
            d.tokens['controller_source_item_2'] =  '' if len(d.tickets) == 0 else d.tickets[2].source_item if len(d.tickets) > 2 else ''
            
            event_time = d.tokens['analysis_time_human']
            if len(d.events) > 0:
                aux_event0 = d.events[0].strToJSon(d.events[0].aux)
                if Misc.hasKey(aux_event0, 'source_aux', '') != '':
                    event_time = aux_event0['source_aux']['time']
                    event_time = datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S')
                    event_time = event_time.timestamp()
                    event_time -= (5 * 60 * 60)
                    event_time = Misc.timeToString(event_time, '%H:%M')

            d.tokens['analysis_phrase'] =  'At ' + event_time
            d.tokens['analysis_phrase'] += ' some ' + data.data
            d.tokens['analysis_phrase'] = d.tokens['analysis_phrase'] if len(d.events) == 0 else d.tokens['analysis_phrase'] + ' with ' + str(round(d.events[0].data['acc']*100,2)) + '% of accuracy was detected'
            d.tokens['analysis_phrase'] = d.tokens['analysis_phrase'] if len(d.events) == 0 else d.tokens['analysis_phrase'] + ' by ' + d.events[0].source_name
            d.tokens['analysis_phrase'] += '.'
            

            for c in self.channels:
                chnl = self.channels[c]
                if chnl.ENABLED:
                    if len(self.authoraizedChannels) > 0 and chnl.ME_NAME not in self.authoraizedChannels:
                        continue # Skip not authorized channels

                    msg = d.copy()                               
                    msg.to = Misc.hasKey(chnl.ME_CONFIG, 'TO', '')
                    msg.message = Misc.hasKey(chnl.ME_CONFIG, 'MESSAGE', '')                    
                    crr = Carrier(msg, chnl)
                    crr.message.message = crr.message.replace_tokens(crr.message.message)
                    
                    existsCarrier = False
                    for crrDis in self.POOL_DISPATCHES:
                        if crrDis.equals(crr):
                            existsCarrier = True
                            break
                    if not existsCarrier:
                        self.POOL_DISPATCHES.append(crr)                        
        except:
            dataE = Data()
            dataE.source_type = SourceTypes.ANALYZER
            dataE.source_name = 'LoaderOfChannel'
            dataE.source_item = ''
            dataE.data = self.COMMPOOL.errorDetail(Messages.channel_error_put_msg)
            dataE.aux = ''
            self.COMMPOOL.logFromCore(dataE, LogTypes.ERROR, self.__class__.__name__)
