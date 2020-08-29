"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to send notifications using SMS.
    # Previous requirements
    # Download the helper library from [https://www.twilio.com/docs/python/install](https://www.twilio.com/docs/python/install)
    pip install twilio
"""

import sys
from os.path import dirname, normpath
from twilio.rest import Client # SMS library

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from CommChannel import CommChannel, Dispatch

class SmsChannel(CommChannel):
    """ Class to send notifications using SMS. """

    def preLoad(self):
        """ Implement me! :: Loads configurations for to send message """
        pass
    
    def preNotify(self, msg:Dispatch):
        """ Implement me! :: Triggered before try to send message """
        pass

    def tryNotify(self, msg:Dispatch):
        """ To send the message using SMS Channel """
        # setup the parameters of the message
        to = msg.to
        message = msg.message
        sender = Misc.hasKey(self.ME_CONFIG, "FROM", '')
        # Your Account Sid and Auth Token from twilio.com/console
        account_sid = Misc.hasKey(self.ME_CONFIG, "ACCOUNT_SID", '')
        auth_token = Misc.hasKey(self.ME_CONFIG, "AUTH_TOKEN", '')
        client = Client(account_sid, auth_token)

        for number in to:
            sms = client.messages.create(
                to=number, 
                from_=sender,
                body=message)

            #print(sms.sid)

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = SmsChannel()
    comp.init_standalone(path=dirname(__file__))
    dispatch = Dispatch( 
        to=comp.ME_CONFIG['TO'], 
        message=comp.ME_CONFIG['MESSAGE'])
    dispatch.files.append('img.png')
    comp.ME_CONFIG['FROM'] = comp.ME_CONFIG['FROM']
    comp.tryNotify(dispatch)

