"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to general propouses and generic utilities functions
"""
import sys
import logging

from enum import Enum, unique
import os
from os import scandir, getcwd
from time import time, strftime, gmtime

import random
import string

import yaml # pip install pyyaml

class Struct:
    """ Auxiliar class to convert a dictionary in object """
    def __init__(self, **entries):
        self.__dict__.update(entries)

def dictToObject(dict):
    """ Take a dictionary an generate an object with the atributes """
    s = Struct(**dict)
    return s

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

def createFolders(path):
    """ Create the path """
    if not os.path.exists(path):
        os.makedirs(path)

def saveByType(data, t:str, path:str):
    """ Save a file to disk according to its type.
        t is the type of data: image, csv
     """
    if t.lower() == 'image':
        from cv2 import cv2
        cv2.imwrite(path, data)

def readConfig(fileName):
    """ Read config file .yaml and returns object """
    config = yaml.safe_load(open(fileName, 'r'))
    return config

def showConfig(config):
    """ Shows data in config file loaded """
    print('\t' + str(config).replace(',', '\n\t'), '\n')    

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

def hasKey(dict, key, default):
    """ If key exists return its value ether return No 'key' """
    if key in dict:
        return dict[key]
    else:
        return default

def toBool(value:str):
    """ Chech if the value is true or false """
    return str.lower(str(value)) in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

def randomString(stringLength=10):
    """ Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def timeToString(t:time=None, format:str='%Y-%m-%d %H:%M:%S'):
    """ Returns a string with date time in human format 
        t is a time() object
        format is a string with order to generate result (see time.strftime function) 
    """
    t = time() if t == None else t
    s = strftime(format, gmtime(t))
    return s

