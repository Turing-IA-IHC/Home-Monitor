"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)

Class information:
    Class to general propouses and generic utilities functions
"""

__version__ = '1.0.0'

def getOriginalData(t:str, data):
    """ Returns the real object data captured by devices.
        Formats availables:
            img: image captured using cv2 of openCV
    """
    if t == 'img':
        from cv2 import cv2
        cv2.imwrite('img.png', data)
