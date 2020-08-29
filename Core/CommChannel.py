"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

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
    to = []             # Receiver       
    message:str = ''    # Body of message
    tokens = {}         # List of variables availables to replace
    files = []          # Path of files to attach

    def __init__(self, to=[], message:str=''):
        """ Allow to create a message structure to send """
        self.to = to
        self.message = message
        
    def equals(self, dispatch):
        """ Compare two message and identify if are similar """
        return  self.to == dispatch.to and \
                self.message == dispatch.message

    def replace_tokens(self, text:str):
        """ Replace texts in all variables by tokens values """
        for key in self.tokens:
            text = text.replace('['+key+']', str(self.tokens[key]))            
        return text

    def copy(self):
        """ Return a copy of full message """
        d = Dispatch()
        d.born = self.born
        d.to = self.to
        d.message = self.message
        d.tokens = self.tokens
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
        msg.replace_tokens(msg.to)
        msg.replace_tokens(msg.message)
        self.tryNotify(msg)

    @abc.abstractmethod    
    def preNotify(self, msg:Dispatch):
        """ Implement me! :: Triggered before try to send message """
        pass

    @abc.abstractmethod
    def tryNotify(self, msg:Dispatch):
        """ Implement me! :: Send message. """
        pass
    
    def start(self):
        """ Method ignored """
        pass