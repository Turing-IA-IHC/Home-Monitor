"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to send notifications by mail.
"""

import sys
from os.path import dirname, normpath, basename

# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from CommChannel import CommChannel, Dispatch

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# GMAIL Documentation:
# Enable access:    https://accounts.google.com/b/0/DisplayUnlockCaptcha
#                   https://myaccount.google.com/lesssecureapps

class MailChannel(CommChannel):
    """ Class to send notifications by mail. """

    def preLoad(self):
        """ Implement me! :: Loads configurations for to send message """
        pass

    def preNotify(self, msg:Dispatch):
        """ Implement me! :: Triggered before try to send message """
        pass

    def tryNotify(self, msg:Dispatch):
        """ To send the message """
        # setup the parameters of the message
        Of = Misc.hasKey(self.CONFIG, "OF", '') if msg.of == '' else msg.of
        To = Misc.hasKey(self.CONFIG, "TO", '') if msg.to == '' else msg.to
        cc = Misc.hasKey(self.CONFIG, "CC", '') if msg.cc == '' else msg.cc
        bcc = Misc.hasKey(self.CONFIG, "BCC", '') if msg.bcc == '' else msg.bcc
        #To = [x.encode('utf-8') for x in To]
        Subject = Misc.hasKey(self.CONFIG, "SUBJECT", '') if msg.subject == '' else msg.subject
        Message = Misc.hasKey(self.CONFIG, "MESSAGE", '') if msg.message == '' else msg.message                
        
        msgMail = MIMEMultipart()
        msgMail['From'] = Of
        msgMail['To'] = ', '.join(To)
        msgMail['Cc'] = ', '.join(cc)
        msgMail['Bcc'] = ', '.join(bcc)
        msgMail['Subject'] = Subject
        #create server  
        server = smtplib.SMTP(self.CONFIG["SMTP"], self.CONFIG["PORT"])
        server.starttls()    
        # Login Credentials for sending the mail
        server.login(Of, self.CONFIG["PASSWORD"]) 
        # add in the message body
        msgMail.attach(MIMEText(Message, 'html'))
        
        for f in msg.files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msgMail.attach(part)
        
        # send the message via the server.
        server.sendmail(msgMail['From'], msgMail['To'] + msgMail['Cc'] + msgMail['Bcc'], msgMail.as_string())
        
        server.quit() 

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = MailChannel()
    comp.init_standalone(Me_Path=dirname(__file__), autoload=False)
    dispatch = Dispatch(of='profesorGavit0@gmail.com', to=['Gavit0Rojas@gmail.com', 'gavit0@hotmail.com'], subject='HM Prueba', message='Prueba')
    dispatch.files.append('img.png')
    comp.tryNotify(dispatch)
