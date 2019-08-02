"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to general propouses and generic utilities functions
"""
from enum import Enum, unique
import os
from os import scandir, getcwd

import sys
import yaml # pip install pyyaml

import logging

def singleton(cls):
    """ Allows to implemenet singleton pattern using a decorator """    
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls

def lsFolders(path = getcwd()):
    """
    Returns folders names in a folder parent
    """
    folders = [path + "/" + arch.name for arch in scandir(path) if arch.is_dir()]
    return folders

def lsFiles(path = getcwd()):
    """
    Returns files names in a folder
    """
    files = [path + "/" + arch.name for arch in scandir(path) if arch.is_file()]
    return files

def existsFile(fileName, path = getcwd()):
    """
    Returns files a bool to indicate if file exists
    """
    files = [arch.name for arch in scandir(path) if arch.name == fileName]
    return len(files) > 0

def readConfig(fileName):
    """ Read config file .yaml and returns object """
    config = yaml.safe_load(open(fileName, 'r'))
    return config

def showConfig(config):
    """ Shows data in config file loaded """
    print('\t' + str(config).replace(',', '\n\t'))
    print('')
    

def importModule(path:str, moduleName:str, className:str=None):
    """ Load and returns a module.
        path: Path of folder where is the modeule
        moduleName: Name of file .py
        className: Name of class in module, if is none returns the module else return the class
    """
    sys.path.insert(-1, path)
    mod = __import__(moduleName)
    if className != None and className != "":
        mod = getattr(mod, className)
    return mod

def loggingConf(loggingLevel=logging.INFO, loggingFile=None, loggingFormat=None ):
    """ Set default logging """

    if loggingLevel == None:
        loggingLevel = logging.INFO

    if loggingFormat == None:
        loggingFormat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=loggingLevel,
        filename=loggingFile, 
        format=loggingFormat)
    
def hasKey(dict, key):
    """ If key exists return its value ether return No 'key' """
    if key in dict:
        return dict[key]
    else:
        return 'No ' + str(key)

def toBool(value:str):
    """ Chech if the value is true or false """
    return str.lower(value) in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']