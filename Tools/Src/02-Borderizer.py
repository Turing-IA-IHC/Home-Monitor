"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code allow to increse cuantity of image to process
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""

# Code based in: https://programarfacil.com/blog/vision-artificial/detector-de-bordes-canny-opencv/

import numpy as np
import cv2
import os
from os import scandir, getcwd

# === Configuration vars ===
# Path of image folder (use slash at the end)
INPUT_PATH = "M:/IA/DAEPP/Infarct/Skeleton/Dataset/01PersonExtracted/"
# Path where new images goes to put (use slash at the end)
OUTPUT_PATH = "M:/IA/DAEPP/Infarct/Skeleton/Dataset/02Borderized/"
# === ===== ===== ===== ===


def ls(ruta = getcwd()):
    """
    Retorns all files including its full path
    """
    files = [ruta + arch.name for arch in scandir(ruta) if arch.is_file()]
    folders = [ruta + arch.name for arch in scandir(ruta) if arch.is_file() == False]
    for f in folders:
        files = files + ls(f + '/')
    return files

if __name__ == '__main__':

    images = ls(INPUT_PATH)
    
    count = 0
    for image in images:
        if not os.path.exists(image):
            continue
        
        frame = cv2.imread(image)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #frame = cv2.GaussianBlur(frame, (5,5), 0)
        #frame = cv2.Canny(frame, 80, 180)

        nuevo = image.replace(INPUT_PATH, OUTPUT_PATH)
        nuevoFolder = nuevo[0:nuevo.rindex('/')]
        if not os.path.exists(nuevoFolder):
            os.mkdir(nuevoFolder)
        cv2.imwrite(nuevo + '.Borderized.png', frame)
        count = count + 1

    print('Images borderized:', count)
