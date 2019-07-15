"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code take a model to detect infarcts and retrain it
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""

import os
import sys
from time import time
import tensorflow as tf
import keras
from tensorflow.keras import backend as K
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dropout, Flatten, Dense, Activation
from tensorflow.keras.layers import  Convolution2D, MaxPooling2D, ZeroPadding2D

# === Configuration vars ===
DISACOUPLED = False         # True if exec out of Home-Monitor, if exect path is IBD.
TPU_WORKER = 'TPU'          # TPU Identifier

MODULE_NAME = 'InfarctSimpleCnnHAR'     # Name of module
BASE_PATH = "./" if DISACOUPLED else "./Har/" + MODULE_NAME + "/"

OUTPUT_DIR = BASE_PATH + "/Model/"
LOG_DIR = BASE_PATH + "/Log/"
MODEL_PATH = OUTPUT_DIR + "model.h5"
WEIGHTS_PATH = OUTPUT_DIR + "weights.h5"

# Path of image folder (use slash at the end)
INPUT_PATH_TRAIN = BASE_PATH + "../../Datasets/InfarctDS/10Data_70_15_15/train/"
INPUT_PATH_VAL = BASE_PATH + "../../Datasets/InfarctDS/10Data_70_15_15/val/"
INPUT_PATH_TEST = BASE_PATH + "../../Datasets/InfarctDS/10Data_70_15_15/test/"

# Checkpoints
EPOCH_CHECK_POINT = 2   # How many epoch til save next checkpoint
NUM_CHECK_POINT = 20     # How many epoch will be saved
KEEP_ONLY_LATEST = False# Keeping only the last checkpoint

# Notifier by mail
PROGRESS_NOTIFY = True
MAIL_TO = 'ProfesorGavit0@gmail.com'
MAIL_PATH = BASE_PATH + "../../Channels/MailChannel/MailChannel.py"

# Train configurations
WIDTH, HEIGHT = 256, 256# Size images to train
STEPS = 3500            # How many steps per epoch
VALIDATION_STEPS = 100  # How many steps per next validation
BATCH_SIZE = 8          # How many images at the same time, change depending on your GPU
LR = 0.001              # Learning rate
CLASES = 2              # Don't chage, 0=Infarct, 1=Normal
# === ===== ===== ===== ===

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

if PROGRESS_NOTIFY:
    import importlib.util
    spec = importlib.util.spec_from_file_location("MailChannel", MAIL_PATH)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    MailChannel = foo.MailChannel()

K.clear_session()

train_datagen = ImageDataGenerator()
val_datagen = ImageDataGenerator()
test_datagen = ImageDataGenerator()

train_gen = train_datagen.flow_from_directory(
    INPUT_PATH_TRAIN,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')
val_gen = val_datagen.flow_from_directory(
    INPUT_PATH_VAL,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')
test_gen = test_datagen.flow_from_directory(
    INPUT_PATH_TEST,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')


print("Loading model from:", MODEL_PATH)
NET = load_model(MODEL_PATH)
print("Loading weights from:", MODEL_PATH)
NET.load_weights(WEIGHTS_PATH)

sgd = SGD(lr=LR, decay=1e-7, momentum=0.9, nesterov=True)

NET.compile(optimizer=sgd, loss='binary_crossentropy', metrics=['acc', 'mse'])

NET.summary()

# Tensorboard
idLog = LOG_DIR + "{}".format(time())
tensorboard = keras.callbacks.TensorBoard(
        log_dir=idLog, 
        update_freq = 200
    )

if PROGRESS_NOTIFY:
    MailChannel.Send('Start to learning: {}.'.format(idLog), INPUT_PATH_TRAIN, MAIL_TO)

# Create TPU model from keras model
#tf.logging.set_verbosity(tf.logging.INFO) # Uncomment to show more details
tpu_model = tf.contrib.tpu.keras_to_tpu_model(
    model=NET,
    strategy=tf.contrib.tpu.TPUDistributionStrategy(
        tf.contrib.cluster_resolver.TPUClusterResolver(TPU_WORKER)))

for i in range(100, 100 + NUM_CHECK_POINT): 
    tpu_model.fit_generator(
        train_gen,
        steps_per_epoch=STEPS,
        epochs=EPOCH_CHECK_POINT,
        validation_data=val_gen,
        validation_steps=VALIDATION_STEPS,
        verbose=1,
        callbacks=[tensorboard]
        )
    
    print('Saving model: {:02}.'.format(i))
    tpu_model.save(OUTPUT_DIR + "{:02}_model.h5".format(i))
    tpu_model.save_weights(OUTPUT_DIR + "{:02}_weights.h5".format(i)) 
 
    scoreSeg = tpu_model.evaluate_generator(test_gen, 200)
    #scoreSeg = tpu_model.evaluate_generator(val_gen, 200)
    #scoreSeg = tpu_model.evaluate_generator(train_gen, 200)

    progress = '{:02}) loss: {}, acc: {}, sme: {}, id: {}'.format(i, 
        round(float(scoreSeg[0]), 4), 
        round(float(scoreSeg[1]), 4), 
        round(float(scoreSeg[2]), 4),
        idLog)
    print(progress)
    if PROGRESS_NOTIFY:
        MailChannel.Send(progress, '', MAIL_TO)         

    if KEEP_ONLY_LATEST:
        if os.path.exists(OUTPUT_DIR + "{:03}_model.h5".format((i-1))):
            os.remove(OUTPUT_DIR + "{:03}_model.h5".format((i-1)))
        if os.path.exists(OUTPUT_DIR + "{:03}_weights.h5".format((i-1))):
            os.remove(OUTPUT_DIR + "{:03}_weights.h5".format((i-1)))




"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code take a model to detect infarcts and retrain it
Written by Gabriel Rojas - 2019
Copyright (c) 2019 G0 S.A.S.
Licensed under the MIT License (see LICENSE for details)
"""
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dropout, Flatten, Dense, Activation
from tensorflow.keras.layers import  Convolution2D, MaxPooling2D
from tensorflow.keras import backend as K
import os
from os import scandir, getcwd
from distutils.dir_util import copy_tree
import shutil
"""
# === Configuration vars ===
# TPU Name
TPU_WORKER = 'gavit0rojas' 
# Version to validate
VERSION = 'Basic'
# Path of image folder (use slash at the end)
INPUT_PATH_TRAIN = "./" + VERSION + "/Dataset/10Data/train/"
INPUT_PATH_VAL = "./" + VERSION + "/Dataset/10Data/val/"

# Various
EPOCH_CHECK_POINT = 4
NUM_CHECK_POINT = 3
STEPS = 7000
VALIDATION_STEPS = 500
BATCH_SIZE = 64
LR = 0.002
CLASES = 2
KEEP_ONLY_LATEST = False
# Size image
WIDTH, HEIGHT = 256, 256
# === ===== ===== ===== ===

target_dir = './' + VERSION + '/Model/'
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

model = './' + VERSION + '/Model/model.h5'
weights = './' + VERSION + '/Model/weights.h5'
print("Loading model from:", model)

cnn = load_model(model)
cnn.load_weights(weights)

entrenamiento_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1. / 255)

entrenamiento_generador = entrenamiento_datagen.flow_from_directory(
    INPUT_PATH_TRAIN,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')

validacion_generador = test_datagen.flow_from_directory(
    INPUT_PATH_VAL,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')


cnn.compile(optimizer=tf.train.GradientDescentOptimizer(LR),
              loss='binary_crossentropy',
              metrics=['acc', 'mse'])
              
cnn.summary()

# Create TPU model from cnn model
#tf.logging.set_verbosity(tf.logging.INFO)
tpu_model = tf.contrib.tpu.keras_to_tpu_model(
    model=cnn,
    strategy=tf.contrib.tpu.TPUDistributionStrategy(
        tf.contrib.cluster_resolver.TPUClusterResolver(TPU_WORKER)))
 

modAnterior = ""
pesAnterior = ""
for i in range(10, 12):        
    tpu_model.fit_generator(
        entrenamiento_generador,
        steps_per_epoch=STEPS,
        epochs=EPOCH_CHECK_POINT,
        validation_data=validacion_generador,
        validation_steps=VALIDATION_STEPS
        )
    
    print("Saving model", i)
    tpu_model.save(target_dir + str(i) + 'model_R.h5')
    tpu_model.save_weights(target_dir + str(i) + 'weights_R.h5') 
 
    if KEEP_ONLY_LATEST:
        if os.path.exists(modAnterior):
            print("Delete before", i - 1)
            os.remove(modAnterior)
            os.remove(pesAnterior)
        modAnterior = target_dir + str(i) + 'model_R.h5'
        pesAnterior = target_dir + str(i) + 'weights_R.h5'
