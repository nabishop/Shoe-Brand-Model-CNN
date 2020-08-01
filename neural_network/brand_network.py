from __future__ import absolute_import, division, print_function, unicode_literals

import os
import numpy as np
from os import listdir, remove
from PIL import Image

import tensorflow as tf
import matplotlib.pyplot as plt
import neural_network.image_processor as brand_detailing

model_path = "./network_states/brand_identifier/brand_network_state.h5"
train_np = "./npy_data/train_whole_data.npy"
test_np = "./npy_data/test_whole_data.npy"


class BCNN:
    def __init__(self, shoe_names, image_size=120):
        self.shoe_names = shoe_names
        self.imageSize = (image_size, image_size)

        self.train_data = []
        self.test_data = []
        self.train_data_dir = "./train_data/"
        self.test_data_dir = "./test_data/"

        if os.path.isfile(train_np):
            print("Loading training data from npy")
            self.train_data = np.load(train_np, allow_pickle=True)
            print("Loaded training data")
        else:
            print("Creating training data from images")
            self.create_training_data()
            print("Created training  data\n")

        if os.path.isfile(test_np):
            print("Loading testing data from npy")
            self.train_data = np.load(test_np, allow_pickle=True)
            print("Loaded testing data")
        else:
            print("Creating testing data from images")
            self.create_testing_data()
            print("Created testing data\n")

    def create_np_info(self, filename, path, brand):
        try:
            img = Image.open(path + "/" + filename)
        except OSError:
            print("removed " + filename)
            remove(os.getcwd() + "/" + path + "/" + filename)
            return None

        img = img.convert("L")  # grayscale
        img = img.resize(self.imageSize, Image.ANTIALIAS)
        return [np.array(img), brand]

    def create_training_data(self):
        for query in self.shoe_names:
            brand_label = brand_detailing.label_brand(query)
            if brand_label == -1:
                print(query)
            path = self.train_data_dir + query
            for filename in listdir(path):
                info = self.create_np_info(filename, path, brand_label)
                if info is None:
                    continue
                else:
                    self.train_data.append(info)

        np.random.shuffle(self.train_data)
        np.save("./npy_data/train_whole_data.npy", self.train_data)

    def create_testing_data(self):
        for query in self.shoe_names:
            brand_label = brand_detailing.label_brand(query)
            path = self.test_data_dir + query
            for filename in listdir(path):
                info = self.create_np_info(filename, path, brand_label)
                if info is None:
                    continue
                else:
                    self.test_data.append(info)

        np.random.shuffle(self.test_data)
        np.save("./npy_data/test_whole_data.npy", self.test_data)

    def run_network(self):
        num_epochs = 45

        if os.path.isfile(model_path):
            print("Loading model for brand identification")
            model = tf.keras.models.load_model(model_path)
        else:
            print("Creating model for brand identification")
            model = self.create_model()

        images, targets, test_images, test_targets = self.reshape_images(self.train_data, self.test_data)
        print("Running brand identifier model")
        history = model.fit(images, targets, epochs=num_epochs,
                            validation_data=(test_images, test_targets))

        model.save(model_path)

        plt.plot(history.history['accuracy'], label='accuracy')
        plt.plot(history.history['val_accuracy'], label='val_accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.ylim([0.5, 1])
        plt.legend(loc='lower right')
        # plt.show()

        test_loss, test_acc = model.evaluate(test_images, test_targets, verbose=2)
        print("Test loss: " + str(test_loss))
        print("Test accuracy: " + str(test_acc))
        return test_loss, test_acc

    def create_model(self):
        layers = tf.keras.layers
        dropout_rate = 0.2

        model = tf.keras.models.Sequential()
        model.add(layers.Conv2D(64, (4, 4), activation='relu', input_shape=(self.imageSize[0], self.imageSize[1], 1)))
        model.add(layers.MaxPooling2D((3, 3)))

        model.add(layers.Conv2D(128, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))

        model.add(layers.Conv2D(128, (3, 3), activation='relu'))

        model.add(layers.Flatten())
        model.add(layers.Dense(128, activation='relu'))

        model.add(layers.Dropout(dropout_rate))

        model.add(layers.Dense(len(brand_detailing.known_brands), activation='softmax'))
        model.summary()
        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        return model

    def reshape_images(self, train_data, test_data):
        # training input tensor
        print(len(train_data[0][0]))
        print(len(self.train_data[0][0]))
        x_inputs = np.array([i[0] for i in train_data]).reshape((-1, self.imageSize[0], self.imageSize[1], 1))
        # expected output
        y_train_targets = np.array([i[1] for i in train_data])

        # testing input tensor
        x_test = np.array([i[0] for i in test_data]).reshape((-1, self.imageSize[0], self.imageSize[1], 1))
        # expected output
        y_test_targets = np.array([i[1] for i in test_data])

        return x_inputs, y_train_targets, x_test, y_test_targets
