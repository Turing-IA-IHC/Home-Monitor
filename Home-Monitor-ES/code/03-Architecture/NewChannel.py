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
        """ Load configurations for to send message """
        pass

    def tryNotify(self, msg:Dispatch):
        """ Implement me! :: To send the message """
        # setup the parameters of the message
        Of = Misc.hasKey(self.CONFIG, "OF", '') if msg.of == '' else msg.of
        To = Misc.hasKey(self.CONFIG, "TO", '') if msg.to == '' else msg.to
        Subject = Misc.hasKey(self.CONFIG, "SUBJECT", '') if msg.subject == '' else msg.subject
        Message = Misc.hasKey(self.CONFIG, "MESSAGE", '') if msg.message == '' else msg.message                

        # TODO: Put here any method to send messages

""" =========== Start standalone =========== """
if __name__ == "__main__":
    comp = NewChannel()
    comp.init_standalone(Me_Path=dirname(__file__), autoload=False)
    dispatch = Dispatch(of='', to='', subject='', message='')
    comp.tryNotify(dispatch)

