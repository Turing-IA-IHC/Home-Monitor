def tryNotify(self, msg:Message)
    """ Send mail """

    try:        
        # setup the parameters of the message
        Of = Misc.hasKey(self.CONFIG, "OF", '') if msg.of == '' else msg.of
        To = Misc.hasKey(self.CONFIG, "TO", '') if msg.to == '' else msg.to
        Subject = Misc.hasKey(self.CONFIG, "SUBJECT", '') if msg.subject == '' else msg.subject
        Message = Misc.hasKey(self.CONFIG, "MESSAGE", '') if msg.message == '' else msg.message              

        msgMail = MIMEMultipart()
        msgMail['From'] = From
        msgMail['To'] = To
        msgMail['Subject'] = Subject
        #create server  
        server = smtplib.SMTP('smtp.gmail.com', 587)  
        server.starttls()    
        # Login Credentials for sending the mail
        server.login(msgMail['From'], self.Config["PASSWORD"]) 
        # add in the message body
        msgMail.attach(MIMEText(Message, 'html'))
        
        # send the message via the server.
        server.sendmail(msgMail['From'], msgMail['To'], msgMail.as_string())
        
        server.quit()            
    except:
        logging.exception('Fail to send message. :: Err:{}. Subject: {}, Message: {}, To: {}.'.format(sys.exc_info()[0], Subject, Message, To))