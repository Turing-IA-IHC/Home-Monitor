"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

Matter class to manage HAR Modules
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""

import os
import sys
from os.path import dirname, abspath, exists, split, normpath

class ClassifierHAR:
    """ Matter class to manage HAR Modules """
    ME_PATH = __file__
    CONFIG_FILE = ""
    MODULE_PATH = ""
    NAME = ''
    VERSION = ''
    CONTROLLERS = []
    CLASSES = []
    def __init__(self, cfg=None):
        """ Start object with config vars """
        self.CONFIG_FILE = dirname(abspath(self.ME_PATH)) + "/Config.yaml"
        if not exists(self.CONFIG_FILE):
            self.CONFIG_FILE = split(dirname(abspath(self.ME_PATH)) + "/../")[0] + "/Config.yaml"
        
        if not exists(self.CONFIG_FILE):
            self.CONFIG_FILE = ""
            # TODO: Emitir error por no tener archivo config

        self.CONFIG_FILE = normpath(self.CONFIG_FILE)
        self.MODULE_PATH = dirname(self.CONFIG_FILE)

    def Predict(self, data):
        """ Método que retorna el listado de dispositivos disponibles """
    def start(self):
        """ Función que invocara el sistema para que el módulo inicie """
    def stop(self):
        """ Función que invocara el sistema para detener cualquier funcionamiento del módulo y descargar la memoria ocupada """
