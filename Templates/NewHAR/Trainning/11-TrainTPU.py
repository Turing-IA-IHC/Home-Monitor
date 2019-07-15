"""
Home-Monitor: 
    AI system for the detection of anomalous and possibly harmful events for people.

This code make a neural network to detect infarcts using TPUs
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
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dropout, Flatten, Dense, Activation
from tensorflow.keras.layers import  Convolution2D, MaxPooling2D, ZeroPadding2D

# === Configuration vars ===
DISACOUPLED = True          # True if exec out of Home-Monitor, if exect path is IBD.
TPU_WORKER = 'TPU'          # TPU Identifier

MODULE_NAME = 'InfarctSimpleCnnHAR'     # Name of module
BASE_PATH = "./" if DISACOUPLED else "./Har/" + MODULE_NAME + "/"
OUTPUT_DIR = BASE_PATH + "/Model/"
LOG_DIR = BASE_PATH + "/Log/"

# Path of image folder (use slash at the end)
INPUT_PATH_TRAIN = BASE_PATH + "../../Datasets/InfarctDS/10Data_70_15_15/train/"
INPUT_PATH_VAL = BASE_PATH + "../../Datasets/InfarctDS/10Data_70_15_15/val/"
INPUT_PATH_TEST = BASE_PATH + "../../Datasets/InfarctDS/10Data_70_15_15/test/"

# Checkpoints
EPOCH_CHECK_POINT = 2   # How many epoch til save next checkpoint
NUM_CHECK_POINT = 10    # How many epoch will be saved
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
LR = 0.002              # Learning rate
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

NET = Sequential()

NET.add(Convolution2D(64, (3 ,3), padding ="same", input_shape=(256, 256, 3), activation='relu'))
NET.add(MaxPooling2D((3,3), strides=(3,3)))
NET.add(ZeroPadding2D((1,1)))
NET.add(Convolution2D(128, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((2,2), strides=(2,2)))
NET.add(ZeroPadding2D((1,1)))
NET.add(Convolution2D(256, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((2,2), strides=(2,2)))
NET.add(ZeroPadding2D((1,1)))
NET.add(Convolution2D(512, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((2,2), strides=(2,2)))
NET.add(ZeroPadding2D((1,1)))
NET.add(Convolution2D(1024, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((2,2), strides=(2,2)))
NET.add(ZeroPadding2D((1,1)))
NET.add(Convolution2D(512, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((2,2), strides=(2,2)))

NET.add(Dropout(0.1))
NET.add(Flatten())

for _ in range(10):
    NET.add(Dense(128, activation='relu'))

#NET.add(Dropout(0.4))  # Uncomment to reduce over fitting but learnning slower

NET.add(Dense(CLASES, activation='softmax'))

NET.compile(optimizer=tf.train.RMSPropOptimizer(LR),
              loss='binary_crossentropy',
              metrics=['acc', 'mse'])

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

for i in range(NUM_CHECK_POINT):
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

    progress = '{:02}) loss: {}, acc: {}, mse: {}, id: {}'.format(i, 
        round(float(scoreSeg[0]), 4), 
        round(float(scoreSeg[1]), 4), 
        round(float(scoreSeg[2]), 4),
        idLog)
    print(progress)
    if PROGRESS_NOTIFY:
        MailChannel.Send(progress, '', MAIL_TO)         

    if KEEP_ONLY_LATEST:
        if os.path.exists(OUTPUT_DIR + "{:02}_model.h5".format((i-1))):
            os.remove(OUTPUT_DIR + "{:02}_model.h5".format((i-1)))
        if os.path.exists(OUTPUT_DIR + "{:02}_weights.h5".format((i-1))):
            os.remove(OUTPUT_DIR + "{:02}_weights.h5".format((i-1)))
            