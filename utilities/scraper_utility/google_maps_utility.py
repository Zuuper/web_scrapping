import json
import threading
import time
from multiprocessing import Queue, Process

import numpy as np
from selenium.webdriver import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from utilities.utils import check_element, find_value_of_element
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def search_on_maps(query: str, position: dict, driver: WebDriver):
    """
    next implementation : biar bisa multiple position
    :param driver:
    :param query: something you want to search on google maps, ex: restaurant
    :param position: (lat, lon) koordinat yang ingin dicari
    :return:
    """

    url = 'https://www.google.com/maps/search/'
    query = query.replace(" ", '+')
    if 'lat' in position and 'lon' in position:
        new_url = f'{url}{query}/@{position["lat"]},{position["lon"]}'
        return driver.get(new_url)
    return ValueError('position should include lat and lon')


class MapsDataCollection:
    def __init__(self, config_dir, options, using_multiprocessor=False, total_cpu=1, max_thread=2):
        execute_path = r'E:\project\software_development\web_scrapping\chromeDriver\chromedriver.exe'
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),
                                       options=options)
        self.driver.maximize_window()
        self.prefix_url = "https://www.google.com/maps/search/"
        self.config = json.load(open(config_dir))
        self.premature_data = []
        self.position = ""
        self.using_multiprocessor = using_multiprocessor
        self.total_cpu = total_cpu
        self.max_thread = max_thread

    def init_location(self, position):
        self.driver.get(f"{self.prefix_url}{position}")
        self.position = self.driver.current_url

    def search_on_map(self, query, position):
        print("--- Start Web Crawler Engine --- ")
        query = query.replace(" ", '+')
        position = self.position if self.position else position
        try:
            if 'lat' in position and 'lon' in position:
                new_url = f'{self.prefix_url}{query}/@{position["lat"]},{position["lon"]}'
                self.driver.get(new_url)
        except Exception as e:
            raise ValueError('position should include lat and lon')
        print("--- Web Crawler Engine Ready to use --- ")

    def location_search(self, vertical_coordinate=1000000, max_iteration=1, type_search='surface'):
        self.premature_data = []
        utility_config = self.config['surface_search_config']['utility_xpath']
        search_area = utility_config['search_area']
        end_sign = utility_config['end_sign']
        list_area = utility_config['detail_search_area']
        loading_sign = utility_config['loading_icon']
        zoom_out = utility_config['zoom_out']
        zoom_in = utility_config['zoom_in']
        list_result = []

        num_iteration = 0
        loading_count = 0
        wait_loading_count = 0
        max_wait_loading_count = 4
        max_loading_count = 20
        is_zoom_out = True
        start_scrapping = False
        is_last_time_loading = False
        try:
            print('Start scraping data...')
            # self.driver.find_element(By.XPATH, zoom_out).click()
            while not start_scrapping:
                try:
                    search_result = self.driver.find_element(By.XPATH, search_area)
                    self.driver.execute_script("arguments[0].scrollTop = arguments[1]", search_result,
                                               vertical_coordinate)
                    list_result = self.driver.find_elements(By.XPATH, list_area)
                    is_loading = True if check_element(self.driver, loading_sign) and num_iteration >= 4 else False
                    if is_loading:
                        time.sleep(1)
                    is_loading = True if check_element(self.driver, loading_sign) and num_iteration >= 4 else False

                    if is_loading and is_last_time_loading:
                        if is_last_time_loading:
                            if loading_count <= max_loading_count:
                                if wait_loading_count == max_wait_loading_count:
                                    self.driver.find_element(By.XPATH, zoom_out).click()
                                    wait_loading_count = 0
                                    check_loading_count = True if loading_count < int(max_loading_count / 2) else False
                                    is_zoom_out = True if not is_zoom_out and check_loading_count \
                                        else False if zoom_out and check_loading_count else is_zoom_out
                                    loading_count += 1
                                elif wait_loading_count < max_wait_loading_count:
                                    wait_loading_count += 1
                        else:
                            is_last_time_loading = True
                    elif not is_loading:
                        if is_last_time_loading:
                            is_last_time_loading = False
                    start_scrapping = True if num_iteration >= max_iteration or check_element(self.driver,
                                                                                              end_sign) else False
                    num_iteration += 1
                except Exception as e:
                    print(e)
                    continue
            print('finish pre-collecting data, now collecting data')
            for element in list_result:
                self.premature_data.append({
                    'title': element.get_attribute('aria-label'),
                    'link': element.get_attribute('href')
                })
            length_list = len(self.premature_data)
            # if type_search == 'surface':
            #     if self.using_multiprocessor:
            #         pass
            #     else:
            #         data_result = []
            #         split_list_by = 2
            #         split_list = np.array_split(self.premature_data, split_list_by)
            #         jobs = []
            #         data_result = []
            # elif type_search == 'deep':
            #     pass

            return self.collecting_data("surface")
        except Exception as e:
            raise ValueError(e)

    def setup_jobs(self, jobs, split_list, type_search, data_result):
        for list_ in split_list:
            job = threading.Thread(target=self.collecting_data(type_search, list_), args=[])
            jobs.append(job)
        for job in jobs:
            job.start()
        for job in jobs:
            job.join()

    def collecting_data(self, collecting_type, queue_: Queue, premature_data=[], saved_list=[], total_cpu=1,
                        max_thread=2):

        final_data = []
        jobs = []
        job_queue = Queue()
        elements = self.premature_data
        print(f"we got at least {len(elements)} of data you searching for")
        split_element = np.array_split(elements, self.total_cpu)
        if collecting_type == "surface" or collecting_type == "deep":
            for element in split_element:
                job = Process(target=self.surface_search, args=[element, job_queue]) if collecting_type == "surface" \
                    else Process(target=self.deep_search, args=[element, job_queue])
                job.start()
            for job in jobs:
                job.join()
        else:
            raise ValueError("collection data is not supported")

        while not job_queue.empty():
            final_data.append(job_queue.get())

        print("Finish collecting data, now export data...")
        return final_data

    def surface_search(self, elements, queue_: Queue):
        config = self.config['surface_search_config']
        for el in elements:
            data = {}
            title = el['title']
            # print(title)
            for data_name in config['data_collected']:  # dc = Data Collected
                prefix_xpath = f'//div[@aria-label="{title}"]'
                x_path = f"{prefix_xpath}{config['data_xpath'][data_name]}"
                attr = config['data_area'][data_name]
                data[data_name] = find_value_of_element(self.driver, attr, x_path)
            queue_.put(data)

    def deep_search(self, elements, queue_: Queue):
        for el in elements:
            self.driver.get(el['link'])
            config = self.config['deep_search_config']
            for key,value in config['data_collection']:
                x_path = config['data_xpath'][key]
                pass

    def metadata_collections(self):
        pass
