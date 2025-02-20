# -*- coding: utf-8 -*-
"""Rock Paper Scissor GitHub

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bC3cfmlRCUSjd4OX1CHpuVvIeO6bE8_I
"""

import tensorflow.compat.v2 as tf
import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage import io
import os
import pickle
import sys

"""Preparing our Data"""

DATA_PATH = sys.argv[1] # Path to folder containing data

# shape_to_label = {'rock':np.array([1.,0.,0.,0.]),'paper':np.array([0.,1.,0.,0.]),'scissor':np.array([0.,0.,1.,0.]),'ok':np.array([0.,0.,0.,1.])}
# arr_to_shape = {np.argmax(shape_to_label[x]):x for x in shape_to_label.keys()}
shape_to_label = {'rock':np.array([1.,0.,0.]),'paper':np.array([0.,1.,0.]),'scissor':np.array([0.,0.,1.])}
arr_to_shape = {np.argmax(shape_to_label[x]):x for x in shape_to_label.keys()}

imgData = list()
validationData = list()
labels = list()

for dr in os.listdir(DATA_PATH):
    if dr not in ['paper','scissor','rock']:
        continue
    lb = shape_to_label[dr]
    i = 0
    pictures = os.listdir(os.path.join(DATA_PATH, dr))
    for pic in pictures:
        if not pic.endswith("jpg"):
            continue
        path = os.path.join(DATA_PATH,dr+'/'+pic)
        img = cv2.imread(path)
        # img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        i += 1
        if i > len(pictures) * 4 / 5:
            validationData.append([img, lb])
            validationData.append([cv2.flip(img, 1), lb])  # horizontally flipped image
            validationData.append([cv2.resize(img[50:250, 50:250], (300, 300)), lb])  # zoom : crop in and resize
        else:
            imgData.append([img, lb])
            imgData.append([cv2.flip(img, 1), lb])  # horizontally flipped image
            imgData.append([cv2.resize(img[50:250, 50:250], (300, 300)), lb])  # zoom : crop in and resize



np.random.shuffle(imgData)

imgData,labels = zip(*imgData)

imgData = np.array(imgData)
labels = np.array(labels)

validationData, validationLabel = zip(*validationData)
validationData = np.array(validationData)
validationLabel = np.array(validationLabel)

"""Model"""

from keras.models import Sequential,load_model
from keras.layers import Dense,MaxPool2D,Dropout,Flatten,Conv2D,GlobalAveragePooling2D,Activation
from keras.callbacks import ModelCheckpoint, EarlyStopping
# from keras.optimizers import Adam
from keras.optimizers.legacy import Adam
from keras.applications.densenet import DenseNet121

# from keras.applications import MobileNetV2

# imgData = tf.keras.applications.densenet.preprocess_input(imgData)
"""DenseNet"""

densenet = DenseNet121(include_top=False, weights='imagenet', classes=3,input_shape=(300,300,3))
# densenet = MobileNetV2(include_top=False, weights='imagenet', input_shape=(300,300,3))
densenet.trainable=True

def genericModel(base):
    model = Sequential()
    model.add(base)
    model.add(MaxPool2D())
    model.add(Flatten())
    model.add(Dense(3,activation='softmax'))
    model.compile(optimizer=Adam(),loss='categorical_crossentropy',metrics=['acc'])
    # model.summary()
    return model

dnet = genericModel(densenet)

checkpoint = ModelCheckpoint(
    'model.h5', 
    monitor='val_acc', 
    verbose=1, 
    save_best_only=True, 
    save_weights_only=True,
    mode='auto'
)

es = EarlyStopping(patience = 3)

history = dnet.fit(
    x=imgData,
    y=labels,
    batch_size = 4,
    epochs=8,
    callbacks=[checkpoint,es],
    validation_data=(validationData, validationLabel)
    # validation_split=0.2
)

# dnet.save_weights('model.h5')

with open("model.json", "w") as json_file:
    json_file.write(dnet.to_json())
