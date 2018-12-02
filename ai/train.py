# Date: 11/27/2018
# Author: Pure-L0G1C
# Description: Train a model & save it

from os import path
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator 
from keras.layers import Dense, Conv2D, Dropout, Flatten, MaxPooling2D

class Model(object):


    def __init__(self, train_fld, valid_fld, output_file, epochs=10, batch_size=32):
        self.model = None
        self.epochs = epochs
        self.train_fld = train_fld
        self.valid_fld = valid_fld
        self.batch_size = batch_size
        self.output_file = self.get_output_path(output_file)


    def train(self):
        self.setup_model()
        self.compile()
        self.fit()
        self.save()


    def setup_model(self):
        total_classes = 2
        input_shape = (64, 64, 3)
        self.model = Sequential()
        self.model.add(Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=input_shape))
        self.model.add(Conv2D(32, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))
     
        self.model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
        self.model.add(Conv2D(64, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))
     
        self.model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
        self.model.add(Conv2D(64, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))
     
        self.model.add(Flatten())
        self.model.add(Dense(512, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(total_classes, activation='softmax'))


    def compile(self):
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']) 
        

    def fit(self):
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True
        )

        training_set = train_datagen.flow_from_directory(
            self.train_fld,
            target_size=(64, 64),
            batch_size=self.batch_size,
            class_mode='categorical'
        )

        valid_datagen = ImageDataGenerator(rescale=1./255)
        valid_set = valid_datagen.flow_from_directory(
            self.valid_fld,
            target_size=(64, 64),
            batch_size=self.batch_size,
            class_mode='categorical'
        )

        self.model.fit_generator(
            training_set,
            steps_per_epoch=4000, 
            epochs=self.epochs,
            validation_data=valid_set,
            validation_steps=800
        )


    def get_output_path(self, output_path):
        output_file = output_path
        ext = path.splitext(output_file)[1]
        file_name = path.splitext(output_file)[0]

        if ext != '.h5':
            output_file += '.h5'

        num = 1
        while path.exists(output_file):
            name = path.splitext(output_file)[0]
            name += '_' + str(num)

            output_file = name + '.h5'
            num += 1

        return output_file


    def save(self):
        self.model.save(self.output_file)
 


if __name__ == '__main__':


    '''
    Dataset
        train
            cats_fld
            dogs_fld

        valid
            cats_fld
            dogs_fld
    '''


    epochs = 5
    batch_size = 32
    valid_fld = 'dataset/valid'
    train_fld =  'dataset/train' 
    output_name = 'cat_dog_classifier'


    classifier = Model(train_fld, valid_fld, output_name, epochs, batch_size)
    classifier.train()