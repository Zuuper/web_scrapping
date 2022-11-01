import json
import time

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
    def __init__(self, config_dir, options):
        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.maximize_window()
        self.prefix_url = "https://www.google.com/maps/search/"
        self.config = json.load(open(config_dir))
        self.premature_data = []
        self.position = ""

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

    def surface_search(self, vertical_coordinate=1000000, max_iteration=1):
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
                    self.driver.execute_script("arguments[0].scrollTop = arguments[1]", search_result, vertical_coordinate)
                    list_result = self.driver.find_elements(By.XPATH, list_area)
                    is_loading = True if check_element(self.driver,loading_sign) and num_iteration >= 4 else False
                    if is_loading:
                        time.sleep(1)
                    is_loading = True if check_element(self.driver, loading_sign) and num_iteration >= 4 else False

                    if is_loading and is_last_time_loading:
                        if is_last_time_loading:
                            if loading_count <= max_loading_count:
                                if wait_loading_count == max_wait_loading_count:
                                    self.driver.find_element(By.XPATH, zoom_out).click()
                                    # self.driver.find_element(By.XPATH, search_area).send_keys(Keys.CONTROL + Keys.HOME)
                                    wait_loading_count = 0
                                    check_loading_count = True if loading_count < int(max_loading_count/2) else False
                                    is_zoom_out = True if not is_zoom_out and check_loading_count \
                                        else False if zoom_out and check_loading_count else is_zoom_out
                                    loading_count += 1
                                elif wait_loading_count < max_wait_loading_count:
                                    wait_loading_count += 1
                        else :
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
            return self.collecting_data("surface")
        except Exception as e:
            raise ValueError(e)

    def collecting_data(self, collecting_type):
        final_data = []
        if collecting_type == "surface":
            prefix_xpath = '//div[@class="Z8fK3b"]'
            config = self.config['surface_search_config']
            element = self.driver.find_elements(By.XPATH, prefix_xpath)
            print(f"we got at least {len(element)} of data you searching for")
            for el in self.premature_data:
                data = {}
                title = el['title']
                # print(title)
                for data_name in config['data_collected']:  # dc = Data Collected
                    prefix_xpath = f'//div[@aria-label="{title}"]'
                    x_path = f"{prefix_xpath}{config['data_xpath'][data_name]}"
                    attr = config['data_area'][data_name]
                    data[data_name] = find_value_of_element(self.driver, attr, x_path)
                final_data.append(data)

        elif collecting_type == "deep":
            pass
        else:
            raise ValueError("collection data is not supported")
        print("Finish collecting data, now export data...")
        return final_data

    def deep_search(self):
        pass
