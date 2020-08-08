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

class ConsoleChannel(CommChannel):
    """ Class to send notifications. """

    def preLoad(self):
        """ Implement me! :: Loads configurations for to send message """
        pass
    
    def preNotify(self, msg:Dispatch):
        """ Implement me! :: Triggered before try to send message """
        pass

    def tryNotify(self, msg:Dispatch):
        """ To send the message """
        # setup the parameters of the message
        #of = Misc.hasKey(self.CONFIG, "OF", '') if msg.of == '' else msg.of
        #to = Misc.hasKey(self.CONFIG, "TO", []) if len(msg.to) == 0 else msg.to
        #cc = Misc.hasKey(self.CONFIG, "CC", []) if len(msg.cc) == 0 else msg.cc
        #bcc = Misc.hasKey(self.CONFIG, "BCC", []) if len(msg.bcc) == 0 else msg.bcc
        subject = Misc.hasKey(self.CONFIG, "SUBJECT", '') if msg.subject == '' else msg.subject
        message = Misc.hasKey(self.CONFIG, "MESSAGE", '') if msg.message == '' else msg.message
        
        print(f'\033[1;33;40m ==============================================================')
        print(subject)
        print(message)
        print(f'\033[1;33;40m ==============================================================')
        print(f'\033[0;37;48m ')

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = ConsoleChannel()
    comp.init_standalone(Me_Path=dirname(__file__), autoload=False)
    dispatch = Dispatch(of='', to='', subject='Asunto de consola', message='Mensaje de consola')
    comp.tryNotify(dispatch)
