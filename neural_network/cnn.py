import tensorflow as tf
import neural_network.image_processor as brand_detailing
from PIL import Image
import numpy as np
from neural_network.brand_network import model_path as brand_model_path
from neural_network.shoe_network import brand_shoe_map_path
import pickle


def predict(img_path):
    brand_prediction = predict_brand(img_path)
    shoe_prediction = predict_shoe(img_path, brand_prediction)
    print("FINAL PREDICTIONS: [" + img_path + "]" + "\n" + "Brand: " + brand_prediction + "\tShoe: " + shoe_prediction)


def predict_brand(img_path, ):
    model = tf.keras.models.load_model(brand_model_path)

    img = Image.open(img_path)
    img = img.convert("L")  # grayscale
    img = img.resize((120, 120), Image.ANTIALIAS)
    arr_img = np.array(img)

    predictions = model.predict(np.array(arr_img, dtype="float16")
                                .reshape((-1, 120, 120, 1)))[0]
    max_output_label = np.min
    prediction_num = 0
    for i in range(len(predictions)):
        if predictions[i] > max_output_label:
            max_output_label = predictions[i]
            prediction_num = i

    predicted_brand = brand_detailing.known_brands[prediction_num]
    print("BRAND:\tPath: " + img_path + "\nPredicted: " + predicted_brand + "\n\n")

    return predicted_brand


def predict_shoe(img_path, brand):
    model_path = "./network_states/" + brand + "_network_state.h5"
    model = tf.keras.models.load_model(model_path)

    img = Image.open(img_path)
    img = img.resize((120, 120), Image.ANTIALIAS)
    arr_img = np.array(img)

    predictions = model.predict(np.array(arr_img, dtype="float16")
                                .reshape((-1, 120, 120, 1)))[0]

    map_file = open(brand_shoe_map_path, "rb")
    brand_shoe_map = pickle.load(map_file)
    shoes_in_brand = brand_shoe_map[brand]

    max_output_label = np.min
    prediction_num = 0
    for i in range(len(predictions)):
        if predictions[i] > max_output_label:
            max_output_label = predictions[i]
            prediction_num = i

    print("MODEL:\tPath: " + img_path + "\nPredicted: " + shoes_in_brand[prediction_num] + "\n\n")

    return prediction_num
