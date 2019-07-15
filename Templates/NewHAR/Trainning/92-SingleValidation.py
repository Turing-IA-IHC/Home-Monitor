"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code tests specific case
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""

import numpy as np
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array

# === Configuration vars ===
DISACOUPLED = False     # True if exec out of Home-Monitor, if exec alone path is Module path.

MODULE_NAME = 'InfarctSimpleCnnHAR'     # Name of module
BASE_PATH = "./" if DISACOUPLED else "./Har/" + MODULE_NAME + "/" # Root path for script exectution
MODEL_PATH = BASE_PATH + "/Model/" + "model.h5"    # Full path of model

# Test configurations
WIDTH, HEIGHT = 256, 256# Size images to train
CLASES = ['Infarct', 'None'] # Classes to detect. they most be in same position with output vector
# === ===== ===== ===== ===

print("Loading model from:", MODEL_PATH)
NET = load_model(MODEL_PATH)
NET.summary()

def predict(file):
    x = load_img(file, target_size=(WIDTH, HEIGHT))
    x = img_to_array(x)
    x = np.expand_dims(x, axis=0)
    array = NET.predict(x)
    result = array[0]
    answer = np.argmax(result)
    print("\nDetected class:", CLASES[answer], "\tOutput layer:", result)

# Cases
INPUT_PATH = BASE_PATH + "/Trainning/demo.png" # Path of image to test
predict(INPUT_PATH)

