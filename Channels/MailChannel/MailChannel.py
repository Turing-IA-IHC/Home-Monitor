from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
 
 #https://accounts.google.com/b/0/DisplayUnlockCaptcha
 #https://myaccount.google.com/lesssecureapps

class MailChannel:
    """ Class to notify using Mail channel """
    NOMBRE = ''
    VERSION = ''

    FROM = 'example@gmail.com'
    PASSWORD = 'password'

    def __init__(self, cfg = None):
        """ Start loading configuration of variables """
        # TODO: Load config from YAML

    def Send(self, Subject, Message, To, CC='', BCC=''):
        """ Send mail """

        try:        
            msg = MIMEMultipart()
            # setup the parameters of the message
            msg['From'] = self.FROM
            msg['To'] = To
            msg['Subject'] = Subject
            #create server  
            server = smtplib.SMTP('smtp.gmail.com', 587)  
            server.starttls()    
            # Login Credentials for sending the mail
            server.login(msg['From'], self.PASSWORD) 
            # add in the message body
            msg.attach(MIMEText(Message, 'plain'))    
            
            # send the message via the server.
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            
            server.quit()            
        except :
            import sys
            print("Fail to send message:( ", sys.exc_info()[0], Subject, Message, To)
            # TODO: Crear manejador de exepciones
