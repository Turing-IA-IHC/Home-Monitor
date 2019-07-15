import os
import sys
import numpy as np
import tensorflow
from keras import backend as K
from keras.preprocessing.image import load_img, img_to_array
sys.path.append('./')
from Core.ClassifierHAR import ClassifierHAR

class ibdHAR(ClassifierHAR):
    
    def __init__(self):
        self.ME_PATH = __file__
        ClassifierHAR.__init__(self)
        print("Config path: ", self.CONFIG_FILE)
        print("Module path: ", self.MODULE_PATH)
        self.MODEL_PATH = './har/InfarctHAR/IBD/Model/model.h5'
        self.WEIGHTS_PATH = './har/InfarctHAR/IBD/Model/weights.h5'
        from keras.models import load_model
        print("Loading model from:", self.MODEL_PATH)
        self.NET = load_model(self.MODEL_PATH)
        print("Loading weights from:", self.WEIGHTS_PATH)
        self.NET.load_weights(self.WEIGHTS_PATH)

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
    ibd = ibdHAR()
    img = load_img("M:/IA/Home-Monitor/Har/InfarctHAR/IBD/Src/demo.png", target_size=(256, 256))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    classes = ibd.predict(img)
    print(classes)
    