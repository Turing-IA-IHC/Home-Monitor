"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code tests the success rate in detection
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""

from os import scandir
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
from keras.preprocessing.image import ImageDataGenerator

# === Configuration vars ===
DISACOUPLED = False     # True if exec out of Home-Monitor, if exec alone path is Module path.

MODULE_NAME = 'InfarctSimpleCnnHAR'     # Name of module
BASE_PATH = "./" if DISACOUPLED else "./Har/" + MODULE_NAME + "/" # Root path for script exectution

# Path of image folder
INPUT_PATH_TEST = BASE_PATH + "../../Datasets/InfarctDS/10Data_70_15_15/test/"

MODEL_PATH = BASE_PATH + "/Model/" + "model.h5"    # Full path of model

# Test configurations
WIDTH, HEIGHT = 256, 256# Size images to train
CLASS_COUNTING = True   # Test class per class and show detatils each 
BATCH_SIZE = 8          # How many images at the same time, change depending on your GPU
CLASES = ['Infarct', 'None'] # Classes to detect. they most be in same position with output vector
# === ===== ===== ===== ===

print("Loading model from:", MODEL_PATH)
NET = load_model(MODEL_PATH)
NET.summary()

def predict(file):
    """
    Returns values predicted
    """
    x = load_img(file, target_size=(WIDTH, HEIGHT))
    x = img_to_array(x)
    x = np.expand_dims(x, axis=0)
    array = NET.predict(x)
    result = array[0]
    answer = np.argmax(result)
    return CLASES[answer], result

print("\n======= ======== ========")

if CLASS_COUNTING:
    folders = [arch.name for arch in scandir(INPUT_PATH_TEST) if arch.is_file() == False]

    generalSuccess = 0
    generalCases = 0
    for f in folders:
        files = [arch.name for arch in scandir(INPUT_PATH_TEST + f) if arch.is_file()]
        clase = f.replace(INPUT_PATH_TEST, '')
        print("Class: ", clase)
        indivSuccess = 0
        indivCases = 0
        for a in files:
            p, r = predict(INPUT_PATH_TEST + f + "/" + a)
            if p == clase:
                indivSuccess = indivSuccess + 1
            #else:
            #    print(a, r)
            indivCases = indivCases + 1

        print("\tCases", indivCases, "Success", indivSuccess, "Rate", indivSuccess/indivCases)
        
        generalSuccess = generalSuccess + indivSuccess
        generalCases = generalCases + indivCases

    print("Totals: ")
    print("\tCases", generalCases, "Success", generalSuccess, "Rate", generalSuccess/generalCases)
else:
    test_datagen = ImageDataGenerator()
    test_gen = test_datagen.flow_from_directory(
    INPUT_PATH_TEST,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')
    scoreSeg = NET.evaluate_generator(test_gen, 200)
    progress = 'loss: {}, acc: {}, mse: {}'.format(
        round(float(scoreSeg[0]), 4), 
        round(float(scoreSeg[1]), 4), 
        round(float(scoreSeg[2]), 4)
        )
    print(progress)

print("======= ======== ========")
