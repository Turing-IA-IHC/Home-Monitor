"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code allow to increse cuantity of image to process
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""

# Code based in: http://sigmoidal.ai/reduzindo-overfitting-com-data-augmentation/

import numpy as np
from keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
import os

# === Configuration vars ===
# Path of image folder (use slash at the end)
INPUT_PATH = "M:/IA/HomeOLD/33Extracted/"
# Path where new images goes to put (use slash at the end)
OUTPUT_PATH = "M:/IA/HomeOLD/34Augmented/"
 
# Quantity of images to generate concurrently
BATCH = 1
# Quantity of images to generate per each
QUANTITY = 20
# === ===== ===== ===== ===

Rutas = ["train/01Infarct/", "train/00None/", "val/01Infarct/", "val/00None/", "test/01Infarct/", "test/00None/"]

for r in Rutas:
    RutaImagenes = INPUT_PATH + r
    RutaSalida = OUTPUT_PATH + r
    
    if not os.path.exists(RutaSalida):
        os.makedirs(RutaSalida)

    imgAug = ImageDataGenerator(rotation_range=40, width_shift_range=0.2,
                                height_shift_range=0.2, zoom_range=0.1,
                                fill_mode='nearest', horizontal_flip=True,
                                brightness_range=[0.5, 1.0])

    imgGen = imgAug.flow_from_directory(RutaImagenes, save_to_dir=RutaSalida,
                        save_format='png',
                        batch_size=BATCH)

    qty = len(imgGen.filenames)
    print('Total images of source:', qty)

    counter = 0
    for (i, newImage) in enumerate(imgGen):
        counter += 1
        # Limits Quantity to generate
        if counter >= qty * QUANTITY / BATCH:
            break