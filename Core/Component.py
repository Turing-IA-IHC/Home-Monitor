"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Generic class that represents all the components that can be coupled.
"""

import Misc

class Component:
    path:str = ""
    moduleName: str = ""
    moduleClass: str = ""
    cls = None
    config = None
    configFile:str = ""

    def createFromConfigFile(self, path:str, configFile:str = 'Config.yaml'):
        """ Load componente and class using config file information
            path: Path where is the config file
            configFile: Name of config file. If none load 'config.yaml'.
        """
        if Misc.existsFile(configFile, path):
            self.config = Misc.readConfig(path + "/" + configFile)
            self.path = path
            self.moduleName = self.config['moduleName']
            self.className = self.config['className']
            self.cls = Misc.importModule(self.path, self.moduleName, self.className)

