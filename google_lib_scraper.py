from google_images_download import google_images_download
import os
import random
import shutil

# creating object
response = google_images_download.googleimagesdownload()


def download_images(query, limit=500):
    # keywords is the search query
    # format is the image file format
    # limit is the number of images to be downloaded
    # print urs is to print the image file url
    # size is the image size which can
    # be specified manually ("large, medium, icon")
    # aspect ratio denotes the height width ratio
    # of images to download. ("tall, square, wide, panoramic")
    arguments = {
        "chromedriver": "./chromedriver.exe",
        "keywords": "\"" + query + "\"",
        "format": "jpg",
        "size": "medium",
        "limit": limit,
        "print_urls": False,
        "output_directory": "./train_data",
        "image_directory": query
    }
    try:
        response.download(arguments)

        # Handling File NotFound Error
    except FileNotFoundError:
        # Providing arguments for the searched query
        try:
            # Downloading the photos based
            # on the given arguments
            response.download(arguments)
        except:
            pass


def move_random_images_to_test(percent_test=0.2):
    try:
        os.mkdir(os.getcwd() + "/test_data/")
    except OSError:
        print("Error making test directory for general testing, fail")
        return

    for filename in os.listdir("./train_data"):
        # randomly pick some of them and move them to testing data
        test_path = os.getcwd() + "/test_data/" + filename
        try:
            os.mkdir(test_path)
        except OSError:
            print("Error making test directory for " + filename)  # do nothing

        try:
            file_names = os.listdir(os.getcwd() + "/train_data/" + filename).copy()
        except FileNotFoundError:
            print("Error finding file for " + filename + " when moving images")
            return

        num_to_pick = int(len(file_names) * percent_test)
        random.shuffle(file_names)
        num_picked = 0

        while num_picked < num_to_pick:
            name = file_names[num_picked]
            shutil.move(os.getcwd() + "/train_data/" + filename + "/" + name,
                        os.getcwd() + "/test_data/" + filename + "/" + name)
            num_picked += 1

        print("NAME: " + filename + "\tMoved " + str(num_picked) + " to testing")
