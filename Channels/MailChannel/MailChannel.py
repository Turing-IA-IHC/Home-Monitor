"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to send messages by email.
"""

import sys
from os.path import dirname, normpath
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from CommChannel import CommChannel

class MailChannel(CommChannel):
    """ Class to send messages by email. """
    # Documentation:
    # https://accounts.google.com/b/0/DisplayUnlockCaptcha
    # https://myaccount.google.com/lesssecureapps

    def preLoad(self):
        """ Load configurations for to send message """
        pass

    def send(self, Data='', Subject='', Message='', To='', CC='', BCC=''):
        """ Send mail """

        try:        
            # setup the parameters of the message
            From = self.Config["FROM"]
            To = Misc.hasKey(self.Config, "FROM", '') if To == '' else To
            CC = Misc.hasKey(self.Config, "CC", '') if To == '' else CC
            BCC = Misc.hasKey(self.Config, "BCC", '') if To == '' else BCC
            Subject = Misc.hasKey(self.Config, "SUBJECT", '') if Subject == '' else Subject
            Message = Misc.hasKey(self.Config, "MESSAGE", '') if Message == '' else Message                

            msg = MIMEMultipart()
            msg['From'] = From
            msg['To'] = To
            msg['Subject'] = Subject
            #create server  
            server = smtplib.SMTP('smtp.gmail.com', 587)  
            server.starttls()    
            # Login Credentials for sending the mail
            server.login(msg['From'], self.Config["PASSWORD"]) 
            # add in the message body
            msg.attach(MIMEText(Message, 'html'))
            
            # send the message via the server.
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            
            server.quit()            
        except:
            logging.exception('Fail to send message. :: Err:{}. Subject: {}, Message: {}, To: {}.'.format(sys.exc_info()[0], Subject, Message, To))

# =========== Start standalone =========== #
if __name__ == "__main__":
    config = Misc.readConfig(dirname(__file__) + "/config.yaml")
    chl = MailChannel(config)
    chl.Me_Path = dirname(__file__)
    chl.Standalone = True
    chl.send()

