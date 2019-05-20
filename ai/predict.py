# Date: 11/27/2018
# Author: Pure-L0G1C
# Description: Predict using a trained model

from numpy import expand_dims
from keras.models import load_model
from keras.preprocessing import image


class Model(object):

    '''
            One-Hot Encoding (Categorical)

            [1 0] = Cat
            [0 1] = Dog
    '''

    def __init__(self, path_to_model, path_to_img):
        self.img = None
        self.model = None
        self.path_to_img = path_to_img
        self.path_to_model = path_to_model

    def load_model(self):
        self.model = load_model(self.path_to_model)

    def load_img(self):
        img = image.load_img(self.path_to_img, target_size=(64, 64))
        img = image.img_to_array(img)
        self.img = expand_dims(img, axis=0)

    def predict(self):
        self.load_img()
        self.load_model()
        output = self.model.predict(self.img)[0].tolist()
        cat, dog = output[0], output[1]
        return 'cat' if cat > dog else 'dog'


if __name__ == '__main__':
    path_to_img = 'dataset/valid/cats/img4.jpg'
    path_to_model = 'trained_models/cat_dog_1.h5'

    model = Model(path_to_model, path_to_img)
    prediction = model.predict()
    print('Predicted: {}'.format(prediction))
