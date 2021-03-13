import pdb
import datetime    
import os
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.applications import VGG16
from keras.layers import Dense, Dropout, Flatten
from keras.models import Model
import matplotlib.pyplot as plt 
import numpy as np
import cv2
import time

def create_model(height, width, num_categories):
    """Create new VGG-16 model. Return model."""
    # Fetch base VGG16 model 
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(height, width, 3))

    # Add top to model
    base = base_model.output
    flat = Flatten()(base)
    fc1 = Dense(128, activation='relu', name='fc1')(flat)
    fc2 = Dense(128, activation='relu', name='fc2')(fc1)
    fc3 = Dense(128, activation='relu', name='fc3')(fc2)
    drop = Dropout(0.5)(fc3)
    fc4 = Dense(64, activation='relu', name='fc4')(drop)
    out = Dense(num_categories, activation='softmax')(fc4)
    model = Model(inputs=base_model.input, outputs=out)

    # Train top layers only
    for layer in base_model.layers:
        layer.trainable = False

    return model

def build_and_save_model(x_train_paths, y_train, model_dir):
    """Build and save new VGG-16 model using confident predictions from database. Return trained model path and training date."""
    # define callback functions
    model_checkpoint = ModelCheckpoint(filepath=model_dir, save_best_only=True)
    early_stopping = EarlyStopping(monitor='val_accuracy',
                                min_delta=0,
                                patience=10,
                                verbose=1,
                                mode='auto',
                                restore_best_weights=True)
                                
    # get images
    x_train = []
    for path in x_train_paths:
        frame = cv2.imread(path)
        (_, frame) = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
        x_train.append(frame)
    x_train = np.array(x_train)

    # create model
    height = x_train.shape[1]
    width = x_train.shape[2]
    num_categories = y_train.shape[1]
    try: 
        assert x_train.shape[3] == 3
    except AssertionError:
        print(f'[ERROR] Training data has {x_train.shape[3]} color layers. Model requires 3.')
    model = create_model(height, width, num_categories)
    model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # fit model
    start_time = time.time()
    model.fit(x_train, y_train, epochs=1, batch_size=64, validation_split=0.1, verbose=1, callbacks=[early_stopping, model_checkpoint])
    print(f'[INFO] Model training took {time.time() - start_time} seconds')

    # save model
    training_date = datetime.datetime.now()
    date = training_date.strftime("%Y-%m-%d_T%H_%M")
    model_name = date + '.h5'
    model_path = os.path.join(model_dir, model_name)
    model.save(model_path)
    print(f'[INFO] Model built. New model saved at {model_path}')

    return [model_path, training_date]