"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code split image in Train, Validate and Test
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""

import os
from os import scandir, getcwd
from distutils.dir_util import copy_tree
import shutil

# === Configuration vars ===
# Path of image folder (use slash at the end)
INPUT_PATH = "M:/IA/HomeOLD/001PersonExtracted/"
# Path where new images goes don't put (use slash at the end)
OUTPUT_PATH = "M:/IA/HomeOLD/0010Data"

# Percent to take for each folder
TRAIN = .7
VAL = .15
TEST = .15
# === ===== ===== ===== ===
OUTPUT_PATH = OUTPUT_PATH + "_" + str(int(TRAIN * 100)) + "_" + str(int(VAL * 100)) + "_" + str(int(TEST * 100)) + "/"
os.mkdir(OUTPUT_PATH)


def lsFiles(ruta = getcwd()):
    """
    Returns files names in a folder
    """
    files = [arch.name for arch in scandir(ruta) if arch.is_file()]
    return files

def lsFolders(ruta = getcwd()):
    """
    Returns folders names in a folder parent
    """
    folders = [arch.name for arch in scandir(ruta) if arch.is_file() == False]
    return folders

# Creates base folders
if not os.path.exists(OUTPUT_PATH + "/train/"):
    os.mkdir(OUTPUT_PATH + "/train/")
if not os.path.exists(OUTPUT_PATH + "/val/"):
    os.mkdir(OUTPUT_PATH + "/val/")
if not os.path.exists(OUTPUT_PATH + "/test/"):
    os.mkdir(OUTPUT_PATH + "/test/")

# The class are indentify for each sub folder
folders = lsFolders(INPUT_PATH)

totalImages = 0
totalTrain = 0
totalVal = 0
totalTest = 0

for f in folders:
    # Make final folders
    if not os.path.exists(OUTPUT_PATH + "/train/" + f):
        os.mkdir(OUTPUT_PATH + "/train/" + f)
    if not os.path.exists(OUTPUT_PATH + "/val/" + f):
        os.mkdir(OUTPUT_PATH + "/val/" + f)
    if not os.path.exists(OUTPUT_PATH + "/test/" + f):
        os.mkdir(OUTPUT_PATH + "/test/" + f)
    
    files = lsFiles(INPUT_PATH + f)

    copy = 0
    deTrain = int(len(files) * TRAIN) + 1
    deVal = int(len(files) * VAL)
    deTest = int(len(files) * TEST)

    print(len(files), "images to copy from", f)
    print("\tTo train:", deTrain)
    print("\tTo validation:", deVal)
    print("\tTo test:", deTest)
    totalImages = totalImages + len(files)
    totalTrain = totalTrain + deTrain
    totalVal = totalVal + deVal
    totalTest = totalTest + deTest

    dest = "/train/"
    for a in files:
        if copy < deTrain:
            dest = "/train/"
        elif copy < deTrain + deVal:
            dest = "/val/"
        else:
            dest = "/test/"            

        shutil.copyfile(INPUT_PATH + f + "/" + a, OUTPUT_PATH + dest + f + "/" + a)
        copy = copy + 1
    
    print("Moved:", copy,"from", f)

print("Total moved:", totalImages)
print("\tTo train:", totalTrain)
print("\tTo validation:", totalVal)
print("\tTo test:", totalTest)
