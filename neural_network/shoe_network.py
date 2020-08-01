from __future__ import absolute_import, division, print_function, unicode_literals

import os
import numpy as np
from os import listdir
from PIL import Image
import pickle

import tensorflow as tf
import matplotlib.pyplot as plt
import neural_network.image_processor as detailing

brand_shoe_map_path = "./brand_shoe_map.txt"


class SCNN:
    def __init__(self, labels, image_size=120):
        self.labels = labels
        self.brand_shoes_map = self.create_brand_shoes_map(labels)
        self.imageSize = (image_size, image_size)

        self.train_data = []
        self.test_data = []
        self.train_data_dir = "./test_data/"
        self.test_data_dir = "./test_data/"

        print("Creating training data from images")
        self.create_training_data()

        print("Creating testing data from images")
        self.create_testing_data()

    @staticmethod
    def create_brand_shoes_map(labels):
        brand_shoes_map = {}
        for model in labels:
            model_brand = detailing.label_brand(model)
            if model_brand == -1:
                print("ERROR: " + model + " (NO KNOWN BRAND IDENTIFIER)")
                continue

            if model_brand not in brand_shoes_map.keys():
                brand_shoes_map.update({model_brand: [model]})
            else:
                mbt = brand_shoes_map[model_brand]
                mbt.append(model)
                brand_shoes_map.update({model_brand: mbt})

        print(brand_shoes_map)
        with open(brand_shoe_map_path, "wb") as map_file:
            pickle.dump(brand_shoes_map, map_file)

        return brand_shoes_map

    def label_image(self, filename, brand):
        shoe_name = filename[0:filename.find("_")]
        shoes_in_brand = self.brand_shoes_map[brand]
        for i in range(len(shoes_in_brand)):
            if shoes_in_brand[i].find(shoe_name) != -1:
                return i

        return -1

    def create_np_info(self, filename, path, brand):
        label = self.label_image(filename, brand)
        img = Image.open(path + "/" + filename)
        # img = img.convert("L")  # grayscale
        img = img.resize(self.imageSize, Image.ANTIALIAS)
        return [np.array(img), label, brand]

    def create_training_data(self):
        for query in self.labels:
            brand = detailing.label_brand(query)

            path = self.train_data_dir + query
            for filename in listdir(path):
                self.train_data.append(self.create_np_info(filename, path, brand))

        np.random.shuffle(self.train_data)
        np.save("./npy_data/train_whole_data.npy", self.train_data)

    def create_testing_data(self):
        for query in self.labels:
            brand = detailing.label_brand(query)
            path = self.test_data_dir + query
            for filename in listdir(path):
                self.test_data.append(self.create_np_info(filename, path, brand))

        np.random.shuffle(self.test_data)
        np.save("./npy_data/test_whole_data.npy", self.test_data)

    def run_all_networks(self):
        # copy to avoid unwanted mutations in original data-set
        all_train_data = self.train_data.copy()
        all_test_data = self.test_data.copy()
        brand_results = {}

        # create folder for storing all brand network states
        network_paths = "./network_states"
        try:
            os.mkdir(network_paths)
        except OSError:
            print()

        # get all data under one brand, execute network for that data
        for brand in detailing.known_brands:
            if detailing.label_brand(brand) not in self.brand_shoes_map.keys():
                continue

            train_data = []
            test_data = []
            print(brand)

            for i in range(len(all_train_data)):
                train = all_train_data[i]
                if detailing.known_brands[train[2]] == brand:
                    train_data.append(train)

            for i in range(len(all_test_data)):
                test = all_test_data[i]
                if detailing.known_brands[test[2]] == brand:
                    test_data.append(test)

            np.random.shuffle(train_data)
            np.random.shuffle(test_data)
            test_loss, test_acc = self.run_network(brand, train_data, test_data, network_paths)
            brand_results.update({brand: [test_loss, test_acc]})

        for brand in brand_results.keys():
            print("BRAND: " + brand)
            print("Test loss: " + str(brand_results[brand][0]))
            print("Test accuracy: " + str(brand_results[brand][1]) + "\n")

    def run_network(self, brand, train_data, test_data, network_paths):
        num_epochs = 50

        model_path = "./" + network_paths + "/" + brand + "_network_state.h5"
        if os.path.isfile(model_path):
            print("Loading model for " + brand)
            model = tf.keras.models.load_model(model_path)
        else:
            model = self.create_model(brand)

        model = self.create_model(brand)

        images, targets, test_images, test_targets = self.reshape_images(train_data, test_data)
        print("Running model for " + brand)
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

    def create_model(self, brand=None):
        layers = tf.keras.layers
        dropout_rate = 0.2

        model = tf.keras.models.Sequential()
        model.add(layers.Conv2D(64, (4, 4), activation='relu', input_shape=(self.imageSize[0], self.imageSize[1], 1)))
        model.add(layers.MaxPooling2D((3, 3)))
        # model.add(layers.BatchNormalization())

        model.add(layers.Conv2D(128, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))

        model.add(layers.Conv2D(128, (3, 3), activation='relu'))

        model.add(layers.Flatten())
        model.add(layers.Dense(128, activation='relu'))

        model.add(layers.Dropout(dropout_rate))

        num_labels = len(self.labels) if brand is None else len(self.brand_shoes_map[detailing.label_brand(brand)])
        model.add(layers.Dense(num_labels, activation='softmax'))
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
