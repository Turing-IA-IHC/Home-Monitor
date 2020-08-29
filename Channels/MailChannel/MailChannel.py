"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to send notifications using mail.
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
    """ Class to send notifications using mail. """

    def preLoad(self):
        """ Implement me! :: Loads configurations for to send message """
        pass
    
    def preNotify(self, msg:Dispatch):
        """ Implement me! :: Triggered before try to send message """
        pass

    def tryNotify(self, msg:Dispatch):
        """ To send the message """
        to = msg.to
        message = msg.message
        sender = Misc.hasKey(self.ME_CONFIG, "FROM", '')
        cc = Misc.hasKey(self.ME_CONFIG, "CC", [])
        bcc = Misc.hasKey(self.ME_CONFIG, "BCC", [])
        subject = msg.replace_tokens(Misc.hasKey(self.ME_CONFIG, "SUBJECT", ''))
        
        msgMail = MIMEMultipart()
        msgMail['From'] = sender
        msgMail['To'] = ', '.join(to)
        msgMail['Cc'] = ', '.join(cc)
        msgMail['Bcc'] = ', '.join(bcc)
        msgMail['Subject'] = subject
        #create server  
        server = smtplib.SMTP(self.ME_CONFIG["SMTP"], self.ME_CONFIG["PORT"])
        server.starttls()    
        # Login Credentials for sending the mail
        server.login(self.ME_CONFIG["USER"], self.ME_CONFIG["PASSWORD"]) 
        # add in the message body
        msgMail.attach(MIMEText(message, 'html'))
        
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
        server.sendmail(sender, to + cc + bcc, msgMail.as_string())        
        server.quit()

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = MailChannel()
    comp.init_standalone(path=dirname(__file__))
    dispatch = Dispatch( 
        to=['Gavit0@hotmail.com', 'Gavit0Rojas@gmail.com'], 
        message=comp.ME_CONFIG['MESSAGE'])
    dispatch.files.append('img.png')
    comp.ME_CONFIG['FROM'] = 'ProfesorGavit0@gmail.com'
    comp.ME_CONFIG['USER'] = 'ProfesorGavit0@gmail.com'
    comp.ME_CONFIG['PASSWORD'] = '4564gpfpxdpp'
    comp.tryNotify(dispatch)
