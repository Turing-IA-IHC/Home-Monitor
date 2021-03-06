"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to send notifications.
"""

import sys
from os.path import dirname, normpath

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from CommChannel import CommChannel, Dispatch

class NewChannel(CommChannel):
    """ Class to send notifications. """

    def preLoad(self):
        """ Implement me! :: Loads configurations for to send message """
        pass
    
    def preNotify(self, msg:Dispatch):
        """ Implement me! :: Triggered before try to send message """
        pass

    def tryNotify(self, msg:Dispatch):
        """ Implement me! :: To send the message """
        # setup the parameters of the message
        to = msg.to
        message = msg.message
        sender = Misc.hasKey(self.ME_CONFIG, "FROM", '')
        subject = msg.replace_tokens(Misc.hasKey(self.ME_CONFIG, "SUBJECT", ''))

        # TODO: Put here any method to send messages

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = NewChannel()
    comp.init_standalone(path=dirname(__file__))
    dispatch = Dispatch( 
        to=comp.ME_CONFIG['TO'], 
        message=comp.ME_CONFIG['MESSAGE'])
    dispatch.files.append('img.png')
    comp.ME_CONFIG['FROM'] = comp.ME_CONFIG['FROM']
    comp.tryNotify(dispatch)

