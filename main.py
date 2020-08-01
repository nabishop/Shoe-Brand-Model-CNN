from twitter.twitter_client import TwitterClient
from solelinks.solelink_info_scraper import ShoeInfoScraper
from image_scraper.google_scraper import GoogleScraper
from neural_network.shoe_network import SCNN
from neural_network.brand_network import BCNN
from os import listdir, path, getcwd, remove
from solecollector.solecollector_scraper import SoleLinkScraper
import shutil
import pickle

import google_lib_scraper

total_shoes_file = "./total_shoes.txt"


def get_twitter_analysis_map():
    shoe_info_scraper = ShoeInfoScraper()
    shoes = shoe_info_scraper.getShoeInfos(0)

    twitter_client = TwitterClient()

    shoe_analysis_map = {}
    for shoe in shoes:
        sentiments = twitter_client.get_sentiments_for_query(shoe.name)
        if sentiments is not None:
            shoe_analysis_map.update(sentiments)

    return shoe_analysis_map


def get_shoes_not_loaded(shoes_total):
    loaded = get_current_shoes_loaded()

    print(str(len(loaded)) + " " + str(len(shoes_total)))
    shoes_total[:] = [shoe.replace("/", "+") for shoe in shoes_total]
    shoes_total[:] = [shoe for shoe in shoes_total if shoe not in loaded]
    print(str(len(loaded)) + " " + str(len(shoes_total)))
    return shoes_total


def get_and_collect_shoes():
    shoe_info_scraper = SoleLinkScraper()

    if path.exists(total_shoes_file):
        with open(total_shoes_file, "rb") as fp:
            shoe_names = pickle.load(fp)
    else:
        shoe_names = shoe_info_scraper.get_shoe_names()
        with open(total_shoes_file, "wb") as fp:
            pickle.dump(shoe_names, fp)

    shoe_names = get_shoes_not_loaded(shoe_names)

    other_scraper = GoogleScraper()
    other_scraper.scrape_images(shoe_names)

    google_lib_scraper.move_random_images_to_test()

    return shoe_names


def run_network(shoe_names):
    network = SCNN(shoe_names)
    network.run_all_networks()


def run_brand_id_network(shoe_names):
    network = BCNN(shoe_names)
    network.run_network()


def main():
    # clean()
    # google_lib_scraper.move_random_images_to_test()
    # shoe_names = get_and_collect_shoes()
    # print(len(shoe_names))
    shoe_names = get_current_shoes_loaded()
    run_brand_id_network(shoe_names)


def clean():
    for filename in listdir("./test_data/"):
        file_names = listdir(getcwd() + "/test_data/" + filename).copy()
        for file in file_names:
            file_p = getcwd() + "/test_data/" + filename + "/" + file
            if path.isdir(file_p):
                print("removed " + file)
                shutil.rmtree(file_p)


def get_current_shoes_loaded():
    shoe_names = []
    for filename in listdir("./train_data"):
        shoe_names.append(filename)

    print(len(shoe_names))
    return shoe_names


if __name__ == '__main__':
    main()
