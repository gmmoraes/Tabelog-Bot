import math
import os
import requests
import sys
import time
import pandas as pd
import json
import time
import threading
import numpy as np
import platform
import multiprocessing
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from multiprocessing import Process
from firebase import firebase
from selenium.webdriver.common.action_chains import ActionChains

start = time.time()


def multiProcess(processors, array, method,optional_arg=""):
        threads = list()
        _processors = checkProcessorsLimit(processors)
        ListSplit = np.array_split(np.array(array), _processors)

        if __name__ == '__main__':
            for i in range(_processors):
                if optional_arg != "":
                    x =threading.Thread(target=method, args=(ListSplit[i], _processors,optional_arg))
                else:
                    x = threading.Thread(target=method, args=(ListSplit[i], _processors,))
                threads.append(x)
                x.start()

            for index, thread in enumerate(threads):
                if thread.daemon:
                    continue
                else:
                    thread.join()



def checkProcessorsLimit(processors):
    totalProcessors = multiprocessing.cpu_count() - 1

    if processors > totalProcessors:
        print("The total amount of processors from your computer is:" + " " +  str(totalProcessors) + " " + "and you requested " + " "  + str(
            processors) + ".Since the amount of processors is higher the the total from your computer, we have changed to: " + " " + str(totalProcessors))
        return totalProcessors

    else:
        return processors


class cityBot:
    def __init__(self, city, processors, chosenExportFormat, foodToSearch):
        self.processors = processors
        self.chosenExportFormat = chosenExportFormat
        self.city = city[0]
        self.foodToSearch = foodToSearch

        # ----------------Driver-----------------------------#
        self.chromeOptions = webdriver.ChromeOptions()
        self.prefs = {'profile.managed_default_content_settings.images': 2}
        self.chromeOptions.add_experimental_option("prefs", self.prefs)
        self.chromeOptions.add_argument("--window-size=1920x1080")
        self.chromeOptions.add_argument("--incognito")
        self.driver = None

        # -------------------Configuration---------------------#
        self.result_array = []
        self.baseUrl = ""
        self.totalPageCount = 0
        self.url = 'https://tabelog.com/en/rstLst/'

        self.chosenosOption = ''

    def get_driver(self):
        systemName = platform.system()

        if systemName == "Windows":
            chrome_driver = os.getcwd() + "\chromedriver.exe"
            driver = webdriver.Chrome(options=self.chromeOptions, executable_path=chrome_driver)
        elif systemName == "Darwin":
            PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
            DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
            driver = webdriver.Chrome(executable_path=DRIVER_BIN)

        self.driver = driver

        self.searchCities()



    def searchCities(self):

        self.driver.get(self.url)
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "search-filter--default")))
        time.sleep(5)
        inputElement = self.driver.find_element_by_xpath('//input[@class="global-headline__search-textfield"]')
        inputElement.click()
        time.sleep(5)
        inputElement.send_keys(self.city)

        selectedCity = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, "//span[contains(@class, 'pac-matched')]")))

        time.sleep(2)
        selectedCity.click()
        time.sleep(5)
        self.searchFood(self.foodToSearch)

    def searchFood(self, food):

        # ---------- Returns a restaurant list based on a food ----------#
        time.sleep(5)
        try:
            browse = self.driver.find_element_by_xpath(
                '//button[@class="c-btn c-btn--link gly-b-arrowdown search-filter-browse__trigger"]')
            time.sleep(2)
            browse.click()
        except Exception as e:
            print(e)
            time.sleep(5)
            try:
                browses = self.driver.find_element_by_xpath('//button[@id="js-category-browse-trigger"]')
                time.sleep(5)
                browse.click()
            except Exception as e:
                print(e)
                try:
                    browses = self.driver.find_element_by_xpath(
                        '//button[@class="c-btn c-btn--link gly-b-arrowdown search-filter-browse__trigger"]')
                    time.sleep(5)
                    browse.click()
                except Exception as e:
                    print(e)
                    try:
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                         '//button[@class="c-btn c-btn--link gly-b-arrowdown search-filter-browse__trigger"]'))).click()
                    except Exception as e:
                        print(e)
                        try:
                            ActionChains(self.driver).move_to_element(self.driver.find_element_by_xpath(
                                '//button[@class="c-btn c-btn--link gly-b-arrowdown search-filter-browse__trigger"]')).click().perform()
                        except Exception as e:
                            print(e)
                            pass

        time.sleep(10)


        try:
            ramen = self.driver.find_element_by_xpath('//p[@data-value="%s"]' % (food,))
            time.sleep(2)
            ramen.click()

        except Exception as e:
            print(e)
            time.sleep(5)

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//p[@data-value="%s"]' % (food,)))).click()

            except Exception as e:
                print(e)
                time.sleep(5)
                try:
                    ActionChains(self.driver).move_to_element(
                        self.driver.find_element_by_xpath('//p[@data-value="%s"]' % (food,))).click().perform()
                except Exception as e:
                    print(e)
                    pass

        time.sleep(5)
        totalResults = self.driver.find_element_by_xpath(
            '//div[@class="c-display-count lookup-result-count js-map-search-count"]').text[10:]
        self.totalPageCount = abs(int(totalResults)/20) 

        for pageNumber in range(0, int(self.totalPageCount)):
            self.getNextPage(self.baseUrl, self.totalPageCount, pageNumber)


        self.export()

    def searchRestaurants(self):
        restaurants_url = []
        self.baseUrl = self.driver.current_url
        elems = self.driver.find_elements_by_xpath('//a[@class="list-rst__name-main js-detail-anchor"]')
        for elem in elems:
            restaurants_url.append(elem.get_attribute("href"))


        self.getRestaurantsURL(restaurants_url,self.processors)


    def getRestaurantsURL(self, restaurants_url, optionalProcessors):

        for url in restaurants_url:
            newUrl = url + "dtlmap/"
            self.driver.get(newUrl)
            address = self.driver.find_element_by_xpath('//p[@class="rd-detail-info__rst-address"]')
            name = self.driver.find_element_by_xpath('//span[@class="rd-detail-info__rst-name-main"]')
            stars = self.driver.find_element_by_xpath('//b[@class="c-rating__val c-rating__val--strong"]')
            time.sleep(2)
            idUrl = self.driver.current_url
            newList = idUrl.rsplit('/', 2)
            newList = newList[0][:-1]
            newList = newList.rsplit('/', 2)
            result_dict = dict()
            result_dict['name'] = name.text
            result_dict['address'] = address.text
            result_dict['stars'] = stars.text
            result_dict['city'] = self.city
            result_dict['id'] = newList[-1]
            self.result_array.append(result_dict)

        self.driver.quit()



    def getNextPage(self, baseUrl, totalPageCount,currentPage):
        innerRestaurants_url = []

        if currentPage == 0:
            self.searchRestaurants()

        else:
            try:
                nextPage = self.driver.find_element_by_xpath(
                    '//a[@class="c-pagination__target c-pagination__target--next js-pjax-anchor"]')
                time.sleep(5)
                nextPage.click()
            except Exception as e:
                print(e)
                time.sleep(5)
                try:
                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH,
                         '//a[@class="c-pagination__target c-pagination__target--next js-pjax-anchor"]'))).click()
                except Exception as e:
                    print(e)
                    time.sleep(5)
                    try:
                        ActionChains(self.driver).move_to_element(self.driver.find_element_by_xpath(
                            '//a[@class="c-pagination__target c-pagination__target--next js-pjax-anchor"]')).click().perform()
                    except Exception as e:
                        print(e)
                        return
            time.sleep(5)
            self.searchRestaurants()



    def export(self):

        global firebase

        firebase_app = firebase.FirebaseApplication('https://tabelog-ffe28.firebaseio.com/', None)
        if self.chosenExportFormat == "Firebase":
            for dictionary in self.result_array:
                cityName = dictionary['city']
                cityId = dictionary['id']
                self.export_to_db(cityId, cityName, dictionary, firebase_app)
        elif self.chosenExportFormat == "json":

    def export_to_db(self, cityId, cityName, dictionary, firebase_app):
        getRequest = result = firebase_app.get('/tabelog-ffe28:/Cities/' + cityName, cityId)

        if getRequest is None:
            print("post")
            firebase_app.post('/tabelog-ffe28:/Cities/' + cityName + '/' + cityId, dictionary)
        else:
            print("put")
            firebase_app.put('/tabelog-ffe28:/Cities/' + cityName + '/', cityId, dictionary)


city_list = ["Tokyo", "Yokohama"]


def createBot(city, processors,foodToSearch):
    bot = cityBot(city, processors, "Firebase",foodToSearch)
    bot.get_driver()


multiProcess(2, city_list, createBot, "ramen")

