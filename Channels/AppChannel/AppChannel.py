"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    See LICENSE file for details

Class information:
    Class to send notifications to APP using WebSockets.
    # Previous requirements
    # Download the helper library from https://websockets.readthedocs.io/en/stable/intro.html
    pip install websockets
"""

import sys
from os.path import dirname, normpath
import asyncio
import websockets
import json
import base64


# Including Home Monitor Paths to do visible the modules
sys.path.insert(0, './Tools/')
sys.path.insert(0, './Core/')

import Misc
from CommChannel import CommChannel, Dispatch

class AppChannel(CommChannel):
    """ Class to send notifications to App using WebSockets. """

    State = {"value": 0}    # 0: Stoped, 1: Running
    Clients = set()         # List of clients conected
    Messages = set()        # List of messages to send

    async def notifyClients(self, msg):
        """ Sen message to all conected client """
        if self.Clients:  # asyncio.wait doesn't accept an empty list
            await asyncio.wait([user.send(msg) for user in self.Clients])

    async def readMessages(self):
        """ Read list of messages to send """
        while True:
            if len(self.Messages) > 0:
                await asyncio.wait([self.notifyClients(msg) for msg in self.Messages])
                self.Messages.clear()
            await asyncio.sleep(5)

    async def newClient(self, websocket, path):
        """ Add clients to messaging """
        self.Clients.add(websocket)
        if self.State["value"] == 0:
            self.State["value"] = 1
            await self.readMessages()            
        try:
            async for _ in websocket:
                pass
        finally:
            self.Clients.remove(websocket)

    def preLoad(self):
        """ Loads configurations for to send message """
        server = Misc.hasKey(self.ME_CONFIG, "SERVER", '127.0.0.1')
        port = Misc.hasKey(self.ME_CONFIG, "PORT", 5678)
        start_server = websockets.serve(self.newClient, server, port)
        asyncio.get_event_loop().run_until_complete(start_server)
        #asyncio.get_event_loop().run_forever()
    
    def preNotify(self, msg:Dispatch):
        """ Implement me! :: Triggered before try to send message """
        pass

    def tryNotify(self, msg:Dispatch):
        """ To send the message """
        # setup the parameters of the message
        message = msg.message
        subject = msg.replace_tokens(Misc.hasKey(self.ME_CONFIG, "SUBJECT", ''))
        attachments = []
        for f in msg.files or []:
            with open(f, "rb") as fil:
                encoded_string = base64.b64encode(fil.read())                
            attachments.append(str(encoded_string).replace("b'", "")[0:-1])
            
        jsonMsg = json.dumps({'message': message, 'subject':subject, 'att':attachments })
        self.Messages.add(jsonMsg)

# =========== Start standalone =========== #
if __name__ == "__main__":
    comp = AppChannel()
    comp.init_standalone(path=dirname(__file__))
    comp.preLoad()
    dispatch = Dispatch( 
        to=comp.ME_CONFIG['TO'], 
        message=comp.ME_CONFIG['MESSAGE'])
    dispatch.files.append('img.png')
    comp.ME_CONFIG['FROM'] = comp.ME_CONFIG['FROM']
    comp.tryNotify(dispatch)
    asyncio.get_event_loop().run_forever()
