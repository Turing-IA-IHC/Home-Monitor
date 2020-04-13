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
    """ Structure to represent a message to send throw some channel. """
    born = time()       # Momentum when message was created
    of:str = ''         # Sender
    to = []             # Receiver       
    cc = []             # Other receiver to copy       
    bcc = []            # Other hidden receiver
    subject:str = ''    # Title of message 
    message:str = ''    # Body of message
    aux:str = ''        # Auxiliar data
    tokens = {}         # List of variables availables to replace
    tickets = []        # Tickets related to dispatch
    events = []         # Events related to dispatch
    alerts = []         # Alerts related to dispatch
    files = []          # Path of files to attach

    def __init__(self, of:str = '', to=[], cc=[], bcc=[], subject:str='', message:str='', aux:str=''):
        """ Allow to create a message structure to send """
        self.of = of
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.message = message
        self.aux = aux

    def equals(self, dispatch):
        """ Compare two message and identify if are similar """
        return  self.of == dispatch.of and \
                self.to == dispatch.to and \
                self.subject == dispatch.subject and \
                self.message == dispatch.message

    def tokenize(self):
        """ Replace texts in all variables by tokens values """
        for key in self.tokens:
            self.of = self.of.replace('['+key+']', str(self.tokens[key]))
            for tos in self.to:
                tos = tos.replace('['+key+']', str(self.tokens[key]))
            for ccs in self.cc:
                ccs = ccs.replace('['+key+']', str(self.tokens[key]))
            for bccs in self.bcc:
                bccs = bccs.replace('['+key+']', str(self.tokens[key]))
            self.subject = self.subject.replace('['+key+']', str(self.tokens[key]))
            self.message = self.message.replace('['+key+']', str(self.tokens[key]))
            self.aux = self.aux.replace('['+key+']', str(self.tokens[key]))

    def copy(self):
        """ Return a copy of full message """
        d = Dispatch()
        d.born = self.born
        d.of = self.of
        d.to = self.to
        d.cc = self.cc
        d.bcc = self.bcc
        d.subject = self.subject
        d.message = self.message
        d.aux = self.aux
        d.tokens = self.tokens
        d.tickets = self.tickets
        d.events = self.events
        d.alerts = self.alerts
        d.files = self.files
        return d

class CommChannel(Component):
    """ Generic class that represents all the communication channels that can be loaded. """

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
    