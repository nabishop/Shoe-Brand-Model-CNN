import urllib
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
import urllib.request
import urllib.error
import shutil
import os
from os import listdir
import random


class GoogleScraper:
    # percent_test is the percentage of results for each query that will be used for testing data
    def __init__(self, percent_test=0.2):
        self.link = "https://www.google.com/imghp?hl=en"
        self.percent_test = percent_test
        self.train_data_dir = "/train_data/"
        self.test_data_dir = "/test_data/"

        try:
            os.mkdir(os.getcwd() + self.train_data_dir)
        except OSError:
            print("Could not make training directory")  # do nothing

        try:
            os.mkdir(os.getcwd() + self.test_data_dir)
        except OSError:
            print("Could not make testing directory")  # do nothing

    def move_random_images_to_test(self, query, train_path):
        # randomly pick some of them and move them to testing data
        test_path = os.getcwd() + "/test_data/" + query
        try:
            os.mkdir(test_path)
        except OSError:
            print()  # do nothing

        try:
            file_names = listdir(train_path).copy()
        except FileNotFoundError:
            return

        num_to_pick = int(len(file_names) * self.percent_test)
        random.shuffle(file_names)
        num_picked = 0

        while num_picked < num_to_pick:
            name = file_names[num_picked]
            shutil.move("." + self.train_data_dir + query + "/" + name, "." + self.test_data_dir + query + "/" + name)
            num_picked += 1

    def download_images(self, query, elements, count):
        print(query)
        train_path = os.getcwd() + self.train_data_dir + query
        try:
            os.mkdir(train_path)
        except OSError as e:
            if str(e).find("Cannot create a file when that file already exists") != -1:
                print("folder already exists for: " + query)
                return

            print(str(e))
            print("Error making dir for " + query + "\n")  # do nothing

        for cnt in range(count):
            if cnt >= len(elements):
                return

            src = elements[cnt].get_attribute('src')
            if src is None:
                continue
            filename = query + "_" + str(cnt) + ".jpg"
            try:
                urllib.request.urlretrieve(src, filename)
            except:
                continue

            try:
                img = Image.open(filename)
                img.verify()  # I perform also verify, don't know if he sees other types o defects

                img = Image.open(filename)
                img.save(filename)
                img.close()  # reload is necessary in my case
                shutil.move("./" + filename, "." + self.train_data_dir + query + "/" + filename)
            except OSError:
                os.remove(filename)

    def scrape_images(self, queries, num_images_per_query=400):
        if len(queries) < 1:
            return None

        browser = webdriver.Chrome(executable_path="./chromedriver.exe")
        browser.maximize_window()
        browser.get(self.link)

        search = browser.find_element_by_xpath("//*[@id=\"sbtc\"]/div/div[2]/input")
        # type query, then press enter
        search.send_keys(queries[0])
        search.send_keys(Keys.ENTER)

        numQuery = 0
        while numQuery < len(queries):
            try:
                imgs = browser.find_elements_by_tag_name("img")
                print(len(imgs))
                self.download_images(queries[numQuery], imgs, num_images_per_query)

                try:
                    next_search = browser.find_element_by_xpath("//*[@id=\"sbtc\"]/div/div[2]/input")
                except NoSuchElementException:
                    break

                numQuery += 1
                if numQuery == len(queries):
                    break

                next_search.clear()
                next_search.send_keys(queries[numQuery])
                next_search.send_keys(Keys.ENTER)
            except TimeoutException:
                browser = webdriver.Chrome(executable_path="./chromedriver.exe")
                browser.get(self.link)
                next_search = browser.find_element_by_xpath("//*[@id=\"sbtc\"]/div/div[2]/input")
                next_search.send_keys(queries[numQuery])
                next_search.send_keys(Keys.ENTER)

        browser.close()
