import datetime
import json
import os
import sys
import threading
import time
from multiprocessing import Queue
from re import search
import numpy as np
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import utilities.utils
from utilities.utils import check_element, find_value_of_element
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import urllib.request
import socket
from utilities.telegram_bot import bot_send_message
from utilities.config import PC_CODE

socket.setdefaulttimeout(15)


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
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options,
                                       desired_capabilities={'browserName': 'chrome',
                                                             'version': 'latest',
                                                             'platform': 'ANY'
                                                             })
        self.driver.maximize_window()
        self.prefix_url = "https://www.google.com/maps"
        self.config = json.load(open(config_dir))
        self.premature_data = []
        self.position = ""
        self.using_multiprocessor = using_multiprocessor
        self.total_cpu = total_cpu
        self.max_thread = max_thread
        self.abs_path = sys.path[1]
        self.query = ""
        self.wait = WebDriverWait(self.driver, 30)

    def init_location(self, position):
        self.driver.get(f"{self.prefix_url}{position}")
        self.position = self.driver.current_url

    def setup_webdriver(self, options):
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),
                                       options=options)

    def open_google_maps(self):
        self.driver.get(self.prefix_url)

    def search_by_searchbar(self, search_keyword):
        searchbar = self.config['surface_search_config']['utility_xpath']['searchbar']
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, searchbar)))
        element.send_keys(search_keyword)
        element.send_keys(Keys.ENTER)

    def check_nearby(self):
        nearby_button = self.config['surface_search_config']['utility_xpath']['search_nearby']
        # time.sleep(2)
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, nearby_button)))
        element.click()

    def search_on_map(self, query, position):
        # print("--- Start Web Crawler Engine --- ")
        self.query = query
        query = query.replace(" ", '+')
        position = self.position if self.position else position

        try:
            if 'lat' in position and 'lon' in position:
                new_url = f'{self.prefix_url}{query}/@{position["lat"]},{position["lon"]},15z'
                self.driver.get(new_url)

        except Exception as e:
            error_name = 'position should include lat and lon'
            # bot_send_message(f"{PC_CODE} {error_name}")
            raise ValueError(error_name)
        # print("--- Web Crawler Engine Ready to use --- ")

    def location_search(self, vertical_coordinate=1000000, max_iteration=1,
                        type_search='surface', location_detail=""):

        self.premature_data = []
        utility_config = self.config['surface_search_config']['utility_xpath']
        search_area = utility_config['search_area']
        end_sign = utility_config['end_sign']
        list_area = utility_config['detail_search_area']
        loading_sign = utility_config['loading_icon']
        zoom_out = utility_config['zoom_out']
        zoom_in = utility_config['zoom_in']
        next_page = utility_config['next_page']
        list_result = []

        num_iteration = 0
        loading_count = 0
        wait_loading_count = 0
        max_wait_loading_count = 2
        max_loading_count = 5
        is_zoom_out = True
        start_scrapping = False
        is_last_time_loading = False
        scroll_position = -1
        is_same_position = 0
        try:
            # print('Start scraping data...')
            self.driver.find_element(By.XPATH, zoom_out).click()
            error_count = 0
            while not start_scrapping:
                try:
                    time.sleep(1)
                    # try:
                    search_result = self.driver.find_element(By.XPATH, search_area)
                    self.driver.execute_script("arguments[0].scrollTop = arguments[1]", search_result,
                                               vertical_coordinate)
                    all_result = self.driver.find_elements(By.XPATH, list_area)
                    for result in all_result:
                        list_result.append(result)
                    is_loading = True if check_element(self.driver, loading_sign) and num_iteration >= 4 else False
                    if is_loading:
                        time.sleep(1)
                    is_loading = True if check_element(self.driver, loading_sign) and num_iteration >= 4 else False
                    if is_loading:
                        if is_last_time_loading and loading_count <= max_loading_count:
                            if wait_loading_count == max_wait_loading_count:
                                if is_zoom_out:
                                    print('zoom out')
                                    self.driver.find_element(By.XPATH, zoom_out).click()
                                    is_zoom_out = False
                                else:
                                    self.driver.find_element(By.XPATH, zoom_in).click()
                                    is_zoom_out = True

                                wait_loading_count = 0
                                check_loading_count = True if loading_count < int(max_loading_count / 2) else False
                                is_zoom_out = True if not is_zoom_out and check_loading_count \
                                    else False if zoom_out and check_loading_count else is_zoom_out
                                loading_count += 1
                            elif wait_loading_count < max_wait_loading_count:
                                wait_loading_count += 1
                            else:
                                start_scrapping = True
                        else:
                            is_last_time_loading = True
                    elif not is_loading:
                        if is_last_time_loading:
                            is_last_time_loading = False

                    start_scrapping = True if num_iteration >= max_iteration or check_element(self.driver,
                                                                                              end_sign) else False
                    try:
                        search_area_scroll_position = self.driver.execute_script('return arguments[0].scrollTop;',
                                                                                 search_result)
                        pagination = self.driver.find_element(By.XPATH, next_page)
                        if search_area_scroll_position == scroll_position:
                            if is_same_position > 4:
                                pagination.click()
                                start_scrapping = False
                                is_same_position = 0
                            else :
                                is_same_position += 1
                        else:
                            scroll_position = search_area_scroll_position
                    except Exception as e:
                        print(e)
                        continue
                    # start_scrapping = True if num_iteration >= max_iteration else False
                    num_iteration += 1
                except Exception as e:
                    print(f"{datetime.datetime.now} {e}")
                    if error_count >= 10:
                        raise Exception("limit error is reached, stop location search")
                    time.sleep(1)
                    error_count += 1
                    continue
            for element in list_result:
                if len(self.premature_data) <= 1000:
                    self.premature_data.append({
                        'title': element.get_attribute('aria-label'),
                        'link': element.get_attribute('href')
                    })
            seen_value = set()
            clean_data = []
            for data in self.premature_data:
                if data['link'] not in seen_value:
                    clean_data.append(data)
                    seen_value.add(data['link'])
            self.premature_data = clean_data
            return self.premature_data
        except Exception as e:
            # bot_send_message(f"{PC_CODE} limit error is reached, stop location search")
            raise ValueError(e)

    def setup_jobs(self, jobs, split_list, type_search, data_result):

        for list_ in split_list:
            job = threading.Thread(target=self.collecting_data, args=(type_search, list_))
            jobs.append(job)

        for job in jobs:
            job.start()

        for job in jobs:
            job.join()

    def collecting_data(self, collecting_type, location_detail="", premature_data=[], saved_list=[], total_cpu=1,
                        max_thread=2):

        final_data = []
        # jobs = []
        job_queue = Queue()
        elements = self.premature_data
        # print(f"we got at least {len(elements)} of data you searching for")
        split_element = np.array_split(elements, self.total_cpu)
        if collecting_type == "surface" or collecting_type == "deep":
            final_data = self.surface_search(elements, location_detail) if collecting_type == 'surface' \
                else self.deep_search(elements)
            return final_data
        jobs = []
        # if collecting_type == "surface" or collecting_type == "deep":
        #     for element in split_element:
        #         job = Process(target=self.surface_search, args=(element, job_queue)) if collecting_type == "surface" \
        #             else Process(target=self.deep_search, args=(element, job_queue))
        #         job.start()
        #     for job in jobs:
        #         job.join()
        # else:
        #     raise ValueError("collection data is not supported")

        # while not job_queue.empty():
        #     final_data.append(job_queue.get())

        # print("Finish collecting data, now export data...")
        # return final_data

    def surface_search(self, elements, location_detail=""):
        config = self.config['surface_search_config']
        final_data = []
        for el in elements:
            data = {}
            title = el['title']
            # print(title)
            for data_name in config['data_collected']:  # dc = Data Collected
                prefix_xpath = f'//div[@aria-label="{title}"]'
                x_path = f"{prefix_xpath}{config['data_xpath'][data_name]}"
                attr = config['data_area'][data_name]
                data[data_name] = find_value_of_element(self.driver, attr, x_path)
            final_data.append(data)
            # queue_.put(data)

        return final_data

    def deep_search(self, elements, queue_: Queue = Queue()):
        final_data = []
        for el in elements:
            self.driver.get(el['link'])
            config = self.config['deep_search_config']
            data = {}

            for key, value in config['data_collection'].items():
                x_path = config['data_xpath'][key]
                attr = config['data_area'][key]
                avail_element = check_element(self.driver, x_path)
                try:
                    if not avail_element and value['alternative']:
                        alternative = value['alternative']
                        new_xpath = alternative['x_path']
                        new_attr = alternative['type']
                        result = find_value_of_element(self.driver, new_attr, new_xpath)
                    else:
                        if value and value['need_to_click']:
                            print(f"finding {key}")
                            if key != "images" and key != 'amenities':
                                self.driver.find_element(By.XPATH, x_path).click()

                            result = self.metadata_collections() if key == "metadata" \
                                else self.image_collection(el['title']) if key == "images" else \
                                self.amenities_collection()
                            if key == "metadata":
                                for key_res, value_res in result.items():
                                    data[key_res] = value_res
                            else:
                                data[key] = result
                            self.driver.get(el['link'])
                            continue
                        else:
                            result = find_value_of_element(self.driver, attr, x_path)
                            if key == 'contact_number':
                                temp_res = result.split(":")
                                result = temp_res[len(temp_res) - 1]
                            if key == 'open_hours':
                                result = result.replace("Hide open hours for the week", "")
                                temp_res = result.split(";")
                                for res in temp_res:
                                    res_split = res.split(",")
                                    if (len(res_split)) == 2:
                                        result = res_split[1]
                                        break
                            if key == "check_in" or key == "check_out":
                                temp = result.replace("time", "  ")
                                # temp_list = temp.split("  ")
                                # print(f"check in or check out: {result}")
                                # result = temp_list[1]
                                # result = result.replace(" : ", "")
                            if key == "address":
                                result = result.replace("Address: ", "")
                            # print(f"{key}: {result}")
                    # print(f"{key} : {result}")
                    data[key] = result
                except Exception as e:
                    print(f"error {key} not found")
                    continue

            curr_url = self.driver.current_url.split("/")
            coor_not_found = True
            while coor_not_found:
                for url in curr_url:
                    if url.startswith("@"):
                        url = url.replace("@", "")
                        url_split = url.split(",")
                        data['coordinate'] = f"{url_split[0]}, {url_split[1]}"
                        coor_not_found = False
                    # self.driver.refresh()
                    time.sleep(1)
                    curr_url = self.driver.current_url.split("/")
            try:
                regency = data['address'].split(',')
                for reg in regency:
                    has_regency = True if search("Kabupaten", reg) or search("Regency", reg) else False
                    has_city = True if search("Kota", reg) or search("City", reg) else False
                    if has_regency or has_city:
                        temp_reg = reg.replace("Kabupaten", "").replace("Kota", "").replace("Regency", "").replace(
                            "City",
                            "")
                        data['regency'] = temp_reg
            except Exception as e:
                print(e)
                continue
            final_data.append(data)
            queue_.put(data)
        return final_data

    def individual_deep_search(self, element):
        final_data = []
        el = element
        self.driver.get(el['link'])
        config = self.config['deep_search_config']
        data = {'title': el['title']}
        for key, value in config['data_collection'].items():
            x_path = config['data_xpath'][key]
            attr = config['data_area'][key]
            avail_element = check_element(self.driver, x_path)
            try:
                if not avail_element and value['alternative']:
                    alternative = value['alternative']
                    new_xpath = alternative['x_path']
                    new_attr = alternative['type']
                    result = find_value_of_element(self.driver, new_attr, new_xpath)
                else:
                    if value and value['need_to_click']:
                        if key != "images" and key != 'amenities':
                            self.driver.find_element(By.XPATH, x_path).click()

                        result = self.metadata_collections() if key == "metadata" \
                            else self.image_collection(el['title']) if key == "images" else \
                            self.amenities_collection()
                        if key == "metadata":
                            for key_res, value_res in result.items():
                                data[key_res] = value_res
                        else:
                            data[key] = result
                        self.driver.get(el['link'])
                        continue
                    else:
                        result = find_value_of_element(self.driver, attr, x_path)
                        # if key == 'contact_number':
                        #     temp_res = result.split(":")
                        #     result = str(temp_res[len(temp_res) - 1])
                        if key == 'open_hours':
                            result = result.replace("Hide open hours for the week", "")
                            temp_res = result.split(";")
                            for res in temp_res:
                                res_split = res.split(",")
                                if (len(res_split)) == 2:
                                    result = res_split[1]
                                    break
                        # if key == "check_in" or key == "check_out":
                        #     result = result.replace("Check-in time:", "").replace("Check-out time:","")
                        # temp_list = temp.split("  ")
                        # print(f"check in or check out: {result}")
                        # result = temp_list[1]
                        # result = result.replace(" : ", "")
                        if key == "address":
                            result = result.replace("Address: ", "")
                        # print(f"{key}: {result}")
                # print(f"{key} : {result}")
                data[key] = result
            except Exception as e:
                continue

        curr_url = self.driver.current_url.split("/")
        coor_not_found = True
        while coor_not_found:
            try:
                for url in curr_url:
                    if url.startswith("@"):
                        url = url.replace("@", "")
                        url_split = url.split(",")
                        data['coordinate'] = f"{url_split[0]}, {url_split[1]}"
                        coor_not_found = False
                    # self.driver.refresh()
                    time.sleep(1)
                    curr_url = self.driver.current_url.split("/")
            except Exception as e:
                print(e)
                break
        try:
            regency = data['address'].split(',')
            for reg in regency:
                has_regency = True if search("Kabupaten", reg) or search("Regency", reg) else False
                has_city = True if search("Kota", reg) or search("City", reg) else False
                if has_regency or has_city:
                    temp_reg = reg.replace("Kabupaten", "").replace("Kota", "").replace("Regency", "").replace(
                        "City",
                        "")
                    data['regency'] = temp_reg
        except Exception as e:
            pass

        data['link'] = el['link']
        print(data)
        final_data.append(data)
        return data

    def metadata_collections(self):
        print('open meta data...')
        prefix_xpath = '//div[@role="main"]//div[@class="iP2t7d fontBodyMedium"]'
        elements = self.driver.find_elements(By.XPATH, prefix_xpath)
        while len(elements) == 0:
            time.sleep(1)
            elements = self.driver.find_elements(By.XPATH, prefix_xpath)
            # print('element not found')
        print('element: ', elements)
        result = {}
        for el in elements:
            # print(role)
            try:
                title = el.find_element(By.TAG_NAME, 'h2').text
                child_xpath = '//ul/li/span'
                metadata_list = el.find_elements(By.XPATH, child_xpath)
                data = [child.text for child in metadata_list]
                result[title] = " | ".join(data)
            except Exception as e:
                # print(e)
                continue
        short_description_xpath = '//div[@jsan="t-1hiPW3JPYg0,7.PbZDve"]'
        try:
            short_description = self.driver.find_element(By.XPATH, short_description_xpath).text
            result['short_description'] = short_description
        except Exception as e:
            # print("short description not found")
            pass
        return result

    def amenities_collection(self):
        prefix_xpath = self.config['deep_search_config']['data_xpath']['amenities']
        elements = self.driver.find_elements(By.XPATH, prefix_xpath)
        result = []
        for el in elements:
            result.append(el.get_attribute('aria-label'))
        result = " | ".join(result)
        return result

    def info_detail_collection(self):
        prefix_path = '//div[@jsan="0.aria-expanded,0.aria-live,t-u_HOalkc3Fc"]/div'
        result = []
        try:
            elements = self.driver.find_elements(By.XPATH, prefix_path)
            for el in elements:
                result.append(el.text)
            result = " ".join(result)
        except:
            result = ""
            pass
        return result

    def more_detail_about_collection(self):
        result = {}
        data = self.driver

    def image_collection(self, title_name, file_path=""):
        print("getting images")
        image_config = self.config['deep_search_config']['image_collection']
        parent_xpath = image_config['parent']
        child_xpath = image_config['child']
        opening_element_xpath = image_config['opening_path']
        parent_tab_xpath = image_config['tab_image']
        banned_category = image_config['banned_category']

        elements = self.driver.find_elements(By.XPATH, parent_xpath)
        collection_names = [el.get_attribute('aria-label') for el in elements]
        collection_values = [el.get_attribute('data-carousel-index') for el in elements]
        # collection_names = [{el.get_attribute('aria-label'): el.get_attribute('data-carousel-index')} for el in
        #                     elements]
        if file_path:
            file_location = file_path
        else:
            file_location = os.path.join(self.abs_path, f"image_gallery/{title_name}")

        print(file_location)
        utilities.utils.generate_folder(file_location)
        try:
            profile_url = self.driver.find_element(By.XPATH, image_config['profile'])
            if profile_url:
                urllib.request.urlretrieve(profile_url.get_attribute('src'), f"{file_location}/profile.png")
            gate = self.driver.find_element(By.XPATH, opening_element_xpath)
            hover = ActionChains(self.driver).move_to_element(gate)
            hover.perform()
            gate.click()
            time.sleep(1)
            for idx in range(len(collection_names)):
                key = collection_names[idx]
                value = collection_values[idx]
                if key not in banned_category:
                    utilities.utils.generate_folder(file_location, key, False)
                    complete_tab_xpath = f'{parent_tab_xpath}/button[@data-tab-index="{value}"]'
                    gate = self.driver.find_element(By.XPATH, complete_tab_xpath)
                    gate.click()

                    elements = self.driver.find_elements(By.XPATH, child_xpath)
                    num_iteration = 0
                    max_iteration = 3
                    while not elements and num_iteration <= max_iteration:
                        elements = self.driver.find_elements(By.XPATH, child_xpath)
                        time.sleep(1)
                        # print("sleeping to get images...")
                        num_iteration += 1
                    try:
                        img_iteration = 0
                        max_img_iteration = 3
                        for el in elements:
                            parent_attr = el.get_attribute("data-photo-index")
                            el.click()
                            switch_to_frame = False
                            if key == "Videos":
                                video_url_xpath = image_config['video_on_frame']
                                try:
                                    # print("open frame")
                                    iframe_xpath = image_config['frame']
                                    WebDriverWait(self.driver, 20). \
                                        until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, iframe_xpath)))
                                    img_url = self.driver.find_element(By.XPATH, video_url_xpath).get_attribute("src")
                                    name_split = img_url.split('/')
                                    name = name_split[len(name_split) - 1].replace("?", "")
                                    try:
                                        urllib.request.urlretrieve(img_url,
                                                                   f"{file_location}/videos/{title_name}_{name}.mp4")
                                        print(f"{datetime.datetime.now()} succesfully download videos")
                                        img_iteration += 1
                                    except Exception as e:
                                        print(f'{datetime.datetime.now()} {e}')
                                        pass
                                    switch_to_frame = True
                                except Exception as e:
                                    # print(e)
                                    # print("fail to open frame")
                                    self.driver.switch_to.default_content()
                                    continue
                            else:
                                # time.sleep(1)
                                img_url_xpath = image_config['child_img']
                                child_xpath = image_config['child']
                                img_check = check_element(self.driver, img_url_xpath)
                                url_xpath = f'{child_xpath}[@data-photo-index={parent_attr}]{img_url_xpath}'
                                img_url = self.driver.find_element(By.XPATH, url_xpath).get_attribute("style")
                                url_list = []
                                if img_check and img_url:
                                    img_style_split = img_url.split("; ")
                                    for style in img_style_split:
                                        if style.startswith("background-image"):
                                            img_url_split = style.split(": ")
                                            for url in img_url_split:
                                                if url.startswith("url"):
                                                    new_url = url.replace("url", "").replace("(", "").replace('"',
                                                                                                              "").replace(
                                                        ";",
                                                        "") \
                                                        .replace(")", "")
                                                    temp_url = new_url.split("/")
                                                    code = temp_url[4]
                                                    code_fragment = code.split("=")
                                                    code_fragment = code_fragment[0]
                                                    new_url = f"{temp_url[0]}/{temp_url[1]}/{temp_url[2]}/p/{code_fragment}=s1536"
                                                    new_url2 = f"{temp_url[0]}/{temp_url[1]}/{temp_url[2]}/p/{code_fragment}=s1024"
                                                    new_url3 = f"{temp_url[0]}/{temp_url[1]}/{temp_url[2]}/p/{code_fragment}=s512"
                                                    url_list = [new_url, new_url2, new_url3]
                                                    img_url = new_url
                                                    break
                                if img_url:
                                    format_ = "webp" if img_check else "mp4"
                                    for url in url_list:
                                        try:
                                            url = url.replace("lh5.googleusercontent.com", "lh3.ggpht.com").replace(
                                                "lh6.googleusercontent.com", "lh3.ggpht.com"). \
                                                replace("lh4.googleusercontent.com", "lh3.ggpht.com").replace(
                                                "lh3.googleusercontent.com", "lh3.ggpht.com")
                                            name = url.split("/")
                                            # urllib.request.urlretrieve(url,
                                            #                        f"{file_location}/{key}/{title_name}_{name[4]}.{format_}")
                                            add_ons_path = f"{key}/" if key == 'menu' else f'story/' if key == "videos" else ""
                                            try:
                                                urllib.request.urlretrieve(url,
                                                                           f"{file_location}/{add_ons_path}{title_name}_{name[4]}.{format_}")
                                                img_iteration += 1
                                                print(f'{datetime.datetime.now()} sucessfully download images')
                                                break
                                            except Exception as e:
                                                print(f"{datetime.datetime.now()} {e}")
                                                continue
                                        except Exception as e:
                                            print(f"{datetime.datetime.now()} {e}")
                                            continue

                            if switch_to_frame:
                                # print("switch back to default content")
                                self.driver.switch_to.default_content()
                            if img_iteration >= max_img_iteration:
                                print(f'{datetime.datetime.now()} maximum images collection is reached')
                                break
                    except Exception as e:
                        print(e)
                        continue
        except Exception as e:
            print(e)
            raise e
