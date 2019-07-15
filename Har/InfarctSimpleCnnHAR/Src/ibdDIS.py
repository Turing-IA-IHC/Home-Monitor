"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code allows to invoke event detection disconnected from Home-Monitor
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""

import os
import numpy as np
import tensorflow
from keras import backend as K
from keras.preprocessing.image import load_img, img_to_array

# === Configuration vars ===
MODEL_PATH = './har/InfarctHAR/IBD/Model/model.h5'
WEIGHTS_PATH = './har/InfarctHAR/IBD/Model/weights.h5'
# === ===== ===== ===== ===

class ibdDIS:
    """ Use this class to detect infarcts """

    def __init__(self, MODEL_PATH, WEIGHTS_PATH):
        from keras.models import load_model
        print("Loading model from:", MODEL_PATH)
        self.NET = load_model(MODEL_PATH)
        print("Loading weights from:", WEIGHTS_PATH)
        self.NET.load_weights(WEIGHTS_PATH)

    def predict(self, img, verbose = False):        
        array = self.NET.predict(img)
        result = array[0]
        answer = np.argmax(result)
        if verbose:
            print("[Infarct, None]", result)

        clase = 'Infarct' if answer == 0 else 'None'
        return [[clase],[result[0]]]

if __name__ == "__main__":
    print("main")
    ibd = ibdDIS(MODEL_PATH, WEIGHTS_PATH)
    img = load_img("M:/IA/Home-Monitor/Har/InfarctHAR/IBD/Src/demo.png", target_size=(256, 256))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    classes = ibd.predict(img)
    print(classes)