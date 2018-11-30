# Date: 11/29/2018
# Author: Pure-L0G1C
# Description: Classifier

from numpy import expand_dims
from keras.models import load_model
from keras.preprocessing import image 
import tensorflow as tf 

global graph
graph = tf.get_default_graph() 


class Classifier(object):
	

	def __init__(self, path_to_model):
		self.img = None 
		self.model = load_model(path_to_model)


	def load_img(self, img):
		img = image.load_img(img, target_size=(64, 64))
		img = image.img_to_array(img)
		self.img = expand_dims(img, axis=0)


	def predict(self, img):
		with graph.as_default():
			self.load_img(img)
			output = self.model.predict(self.img)[0].tolist()
			cat, dog = output[0], output[1]
			return 'cat' if cat else 'dog'