import json
import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from utilities.utils import check_element, find_value_of_element
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import utilities.config as cfg
from selenium.webdriver.common.keys import Keys

class GoogleCollection:
    def __init__(self, config_dir, options):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.prefix_url = "https://www.google.com/"
        self.config = json.load(open(config_dir))
        self.premature_data = []

    def search_data(self, query):
        search_form = "//input[@jsaction='paste:puy29d;']"
        search_button = "//div[@class='FPdoLc lJ9FBc']//input[@type='submit'][@name='btnK']"
        self.driver.get(self.prefix_url)
        self.driver.find_element(By.XPATH, search_form).send_keys(query)
        self.driver.find_element(By.XPATH, search_form).send_keys(Keys.ENTER)

    def get_first_search(self):
        first_result_element = '//div[@class="MjjYud"]//a//h3'
        result = self.driver.find_element(By.XPATH, first_result_element).text
        return result



