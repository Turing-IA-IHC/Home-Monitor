"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the communication channles that can be loaded.
"""

import abc
from os.path import dirname, abspath, exists, split, normpath
import logging
from time import time

import Misc
from Component import Component
from DataPool import DataPool

class Dispatch:
    """ Structure to represent a message to send throw aome channel.
    """
    born = time()       # Momentum when message was created
    of:str = ''         # Sender
    to:str = ''         # Receiver       
    cc:str = ''         # Other receiver to copy       
    bcc:str = ''        # Other hidden receiver
    subject:str = ''    # Title of message 
    message:str = ''    # Body of message
    aux:str = ''        # Auxiliar data

    def __init__(self, of:str = '', to:str = '', cc:str = '', bcc:str = '', subject:str = '', message:str = '', aux:str = ''):
        self.of = of
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.message = message
        self.aux = aux

class CommChannel(Component):
    """ Generic class that represents all the communication channles that can be loaded. """
    
    def __init__(self, cfg=None):
        self.dp = DataPool()        # Object to send information
        self.URL = ""               # Pool URL
        self.Me_Path = "./"         # Path of current component
        self.Standalone = False     # If a child start in standalone
        
        self.Config = cfg           # Object with all config params

        self.loggingLevel = None    # logging level to write
        self.loggingFile = None     # Name of file where write log
        self.loggingFormat = None   # Format to show the log

    """ Abstract methods """
    @abc.abstractmethod
    def preLoad(self):
        """ Implement me! :: Load configurations for to send message """
        pass
  
    def notify(self, msg:Dispatch):
        """ Send a message """
        self.preNotify(msg)
        self.tryNotify(msg)

    @abc.abstractmethod    
    def preNotify(self, msg:Dispatch):
        """ Implement me! :: Triggered before try to send message """
        pass

    @abc.abstractmethod
    def tryNotify(self, msg:Dispatch):
        """ Implement me! :: Send message. """
        pass
    