from selenium import webdriver
import string
from os import listdir, path
from bs4 import BeautifulSoup
import requests
from datetime import datetime


def get_next_year_month(old_year, old_month):
    new_month = str(((int(old_month) % 12) + 1)).zfill(2)
    if int(new_month) < int(old_month):
        new_year = str(int(old_year) + 1)
    else:
        new_year = old_year

    return new_year, new_month


def get_current_shoes_loaded():
    shoe_names = []
    if not path.isdir("./train_data"):
        return []

    for filename in listdir("./train_data"):
        shoe_names.append(filename)

    return shoe_names


class SoleLinkScraper:
    def __init__(self):
        self.shoes = []

    def get_shoe_names(self, num_shoes=20000):
        starting_year = "2011"
        starting_month = "09"
        starting_link = "https://solecollector.com/sneaker-release-dates/all-release-dates/" + \
                        starting_year + "/" + starting_month + "/"
        today = datetime.today()
        print(today.month)

        page = requests.get(starting_link)
        cur_year, cur_month = starting_year, starting_month
        while page.status_code == 200 and len(self.shoes) < num_shoes:
            soup = BeautifulSoup(page.content, 'html.parser')
            shoes_on_page = soup.find_all("div", {"class": "sneaker-release__img-container"})
            for shoe in shoes_on_page:
                names = shoe.findChildren("img")
                for name in names:
                    self.shoes.append(name.attrs["alt"])

            cur_year, cur_month = get_next_year_month(cur_year, cur_month)
            if int(cur_month) > today.month and int(cur_year) >= today.year:
                break

            next_link = "https://solecollector.com/sneaker-release-dates/all-release-dates/" + \
                        cur_year + "/" + cur_month + "/"
            print(len(self.shoes))
            page = requests.get(next_link)
            print(next_link)
            print(page.status_code)

        return self.shoes
