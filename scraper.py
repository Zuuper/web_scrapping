import datetime
import time
import numpy as np
import pandas as pd
from multiprocessing import Queue, cpu_count, Process, pool, Manager, freeze_support
from selenium.webdriver.common.by import By
from tqdm import tqdm

from utilities.scraper_utility import google_maps_utility, google_utility
from selenium.webdriver.chrome.options import Options
from utilities.utils import setup_bag_of_search_word, setup_location, setup_collecting_surface_data
from hanging_threads import start_monitoring
import os

pd.options.mode.chained_assignment = None  # default='warn'


def setup_scraper_configuration():
    bag_of_words = []
    using_surface_search, filename = setup_collecting_surface_data()
    print(using_surface_search)
    if using_surface_search:
        bag_of_words = setup_bag_of_search_word()
    regencies, location = setup_location()
    regency_keyword = []
    for regency in regencies:
        regency_keyword.append(f"{regency} {location}".capitalize())
    return bag_of_words, regency_keyword, filename


def get_detail():
    pass


def init_options():
    options = Options()
    options.headless = True
    # options.add_argument("--kiosk")
    options.add_argument("--lang=en-US")
    options.add_argument(r"--user-data-dir=C:\Users\Asus\AppData\Local\Google\Chrome\User Data")
    options.add_argument(r'--profile-directory=Default')
    options.add_argument("--window-size=1336,768")
    return options


def init_second_options():
    options = Options()
    options.headless = True
    # options.add_argument("--kiosk")
    options.add_argument("--lang=en-US")
    options.add_argument(r"--user-data-dir=C:\Users\Asus\AppData\Local\Google\Chrome\User Data")
    options.add_argument(r'--profile-directory=Default')
    options.add_argument("--window-size=1336,768")
    return options


def google_maps_location_collection(search_param, location, max_iteration):
    config_dir = "config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    data = {}
    #   First search the surface
    for param in search_param:
        engine = maps_collection(config_dir, options=init_options())
        log = f"log for {location} | {param} =>"
        print(f"{log} Started ")
        engine.open_google_maps()
        print(f'{log} open google maps')
        engine.search_by_searchbar(location)
        print(f'{log} search on google maps')
        time.sleep(1)
        engine.check_nearby()
        print(f'{log} click nearby')
        time.sleep(1)
        engine.search_by_searchbar(param)
        print(f'{log} search again')
        print(f'{log} prepare...')
        time.sleep(1)
        premature_data = engine.location_search(max_iteration=max_iteration, vertical_coordinate=100000)
        # engine.driver.quit()
        print(f"{log} finish total data: {len(premature_data)}")
        data[param] = premature_data
        engine.driver.quit()
    # queue_.put(data)
    return data


def google_search(search_param):
    config_dir = r"config/google_search.json"
    google = google_utility.GoogleCollection
    options = Options()
    options.headless = True
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1280,720")
    engine = google(config_dir, options)

    #     short_description_search
    engine.search_data(f"{search_param} description")
    desc_list = []
    href_list = []

    search_xpath = '//div[@class="v7W49e"]//div[@class="kvH3mc BToiNc UK95Uc"]'
    href_xpath = f'{search_xpath}//div[@class="yuRUbf"]/a'
    desc_xpath = f'//{search_xpath}//div[@class="Z26q7c UK95Uc"]/div[@class="VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf"]/span'
    descriptions = engine.driver.find_elements(By.XPATH, desc_xpath)
    hrefs = engine.driver.find_elements(By.XPATH, href_xpath)

    for desc in descriptions:
        desc_list.append(desc.text)
    for href in hrefs:
        href_list.append(href.get_attribute('href'))

    for idx in range(len(desc_list)):
        pass
    param = ""
    prefix_xpath = f'//*[contains(text(),{param})]/parent::div'
    second_prefix_xpath = ""


def get_description_from_google(engine, param):
    prefix_xpath = f'//*[contains(text(),{param})]/parent::div'
    second_prefix_xpath = ""


def google_maps_deep_search(data, queue_: Queue):
    config_dir = "config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    engine = maps_collection(config_dir, options=init_second_options())
    result = engine.deep_search(data)
    queue_.put(result)
    return result


def deep_search_single_data(data, filename):
    config_dir = "config/map_search.json"
    for d in data:
        maps_collection = google_maps_utility.MapsDataCollection
        engine = maps_collection(config_dir, options=init_options())
        result = engine.individual_deep_search(d)
        df = pd.DataFrame([result])

        try:
            default_df = pd.read_csv(filename)
            new_df = pd.concat([default_df, df])
            new_df.to_csv(filename, index=False)
            # df.to_csv(filename, mode="a", index=True, header=is_using_header)
            print('success adding new data to csv')
        except:
            df.to_csv(filename, index=False)
            print('success creating new csv file')
        engine.driver.quit()
    pass


def multiprocessing_location_collection(search_param, locations, max_iteration, queue_: Queue = ""):
    config_dir = "config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    data = {}
    #   First search the surface
    for location in locations:
        for param in search_param:
            engine = maps_collection(config_dir, options=init_options())
            log = f"log for {location} | {param} =>"
            engine.open_google_maps()
            engine.search_by_searchbar(location)
            time.sleep(1)
            engine.check_nearby()
            time.sleep(1)
            engine.search_by_searchbar(param)
            premature_data = engine.location_search(max_iteration=max_iteration, vertical_coordinate=100000)
            # engine.driver.quit()
            print(f"{log} finish total data: {len(premature_data)}")
            data[param] = premature_data
    # queue_.put(data)
    return data


def save_surface_scraping_result(filename, data, keyword):
    data = pd.DataFrame(data)
    data = data.drop_duplicates()
    # desc
    # 0 = no data available |
    # 1 = some data collected, but the primary data (like title) is missing |
    # 2 = text data collected, but no images is collected
    # 3 = all data collected
    try:
        default_df = pd.read_csv(filename)
        new_df = pd.concat([default_df, data])
        res = new_df.drop_duplicates(keep="last")
        res['keyword'] = keyword
        res.to_csv(filename, index=False)
        # df.to_csv(filename, mode="a", index=True, header=is_using_header)
        print('success adding new data to csv')
    except:
        data['keyword'] = keyword
        data.to_csv(filename, index=False)
        print('success creating new csv file')


def check_duplicates(filename):
    df = pd.read_csv(filename)
    new_df = df.drop_duplicates(keep="last")
    new_df.to_csv(filename, index=False)


def check_surface_scarping_data(file_location):
    df = pd.read_csv(file_location)
    df.drop_duplicates()
    df.to_csv(file_location)


def search_description_and_email_from_google(keyword):
    config_dir = "config/google_search.json"
    google = google_utility.GoogleCollection
    options = Options()
    options.headless = True
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1280,720")
    results = []
    pass


def check_scraping_result(scraping_result_filename, surface_scraping_result):
    avail_scraping_df = False
    try:
        scraping_df = pd.read_csv(scraping_result_filename)
        avail_scraping_df = True
    except:
        scraping_df = None

    if type(surface_scraping_result) == str:
        surface_scraping_df = pd.read_csv(surface_scraping_result)
    elif type(surface_scraping_result) == list:
        surface_scraping_df = pd.DataFrame(surface_scraping_result)
    else:
        surface_scraping_df = surface_scraping_result
    if avail_scraping_df:
        completed_title = scraping_df['title'].tolist()
        not_complete_data = surface_scraping_df[~surface_scraping_df['title'].isin(completed_title)]
        return not_complete_data.to_dict('records')
    else:
        return surface_scraping_df.to_dict('records')


def collecting_image_from_google_maps(data):
    config_dir = "config/map_search.json"
    for d in data:
        maps_collection = google_maps_utility.MapsDataCollection
        engine = maps_collection(config_dir, options=init_options())
        engine.driver.get(d['link'])
        engine.image_collection(d['title'])
        engine.driver.quit()


def check_collecting_images_result(surface_scraping_result):
    img_gallery = os.listdir('image_gallery')
    if type(surface_scraping_result) == 'str':
        surface_scraping_df = pd.read_csv(surface_scraping_result)
    elif type(surface_scraping_result) == 'list':
        surface_scraping_df = pd.DataFrame(surface_scraping_result)
    else:
        surface_scraping_df = surface_scraping_result

    not_complete_data = surface_scraping_df[~surface_scraping_df['title'].isin(img_gallery)]

    return not_complete_data.to_dict('records')


def collect_image_of_current_data(scraping_result_location):
    df = pd.read_csv(scraping_result_location)
    new_df = df.head(20).to_dict('records')
    complete_collected_images = False
    not_complete_list = new_df
    while not complete_collected_images:
        jobs = []
        data_split = np.array_split(not_complete_list, 4)
        for ds in data_split:
            job = Process(target=collecting_image_from_google_maps, args=(ds,))
            jobs.append(job)
            job.start()

        for job in jobs:
            job.join()
        complete_collected_images = True


def check_surface_results_keyword(filedir, keywords: []):
    listdir = os.listdir(filedir)
    new_listdir = []
    for dir_ in listdir:
        title = dir_.split('_')
        new_listdir.append(title[0])
    new_keyword = []
    for word in keywords:
        if word not in new_listdir:
            new_keyword.append(word)

    return sorted(set(new_keyword))


def main():
    cpu = int(cpu_count() / 2)
    bag_of_words, locations, filename = setup_scraper_configuration()
    premature_data = {}
    data = []
    start_time = time.time()
    max_iteration = 100
    if bag_of_words:
        for word in bag_of_words:
            premature_data[word] = pd.DataFrame()
        for location in locations:
            data.append(google_maps_location_collection(bag_of_words, location, max_iteration))
        for result in data:
            for key, val in result.items():
                new_df = pd.DataFrame(val)
                premature_data[key] = pd.concat([premature_data.get(key), new_df])

    else:
        filedir = f'surface_scraping_result/{filename}'
        filename = filename.split("_")
        print(filename)
        premature_data[filename[0]] = pd.read_csv(filedir)
    monitoring_thread = start_monitoring(seconds_frozen=10, test_interval=100)

    # jobs = []
    # locations_split = np.array_split(locations, cpu)
    # for locations in locations_split:
    #     job = Process(target=multiprocessing_location_collection, args=(bag_of_words, locations, max_iteration))
    #     jobs.append(job)
    #     job.start()
    # for job in jobs:
    #     job.join()

    for data, val in premature_data.items():
        data = data.lstrip(" ")
        data_listing = val.to_dict('records')
        surface_scraping_filename = f"surface_scraping_result/{data}_{str(datetime.datetime.now().strftime('%d_%m_%Y'))}.csv"
        deep_scraping_filename = f"data_scraping_result/{data}_{str(datetime.datetime.now().strftime('%d_%m_%Y'))}.csv"
        save_surface_scraping_result(surface_scraping_filename, data_listing)
        completed = False
        not_complete_list = check_scraping_result(deep_scraping_filename, pd.DataFrame(data_listing))
        print(f"total not completed : {not_complete_list}")
        while not completed:
            jobs = []
            data_split = np.array_split(not_complete_list, cpu)
            for ds in data_split:
                job = Process(target=deep_search_single_data, args=(ds, deep_scraping_filename))
                jobs.append(job)
                job.start()
            for job in jobs:
                job.join()
            if not_complete_list:
                not_complete_list = check_scraping_result(deep_scraping_filename, pd.DataFrame(not_complete_list))
            if not not_complete_list:
                completed = True
        check_duplicates(deep_scraping_filename)
        complete_collected_images = False

        not_complete_list = check_collecting_images_result(pd.DataFrame(data_listing))
        while not complete_collected_images:
            jobs = []
            data_split = np.array_split(not_complete_list, cpu)
            for ds in data_split:
                job = Process(target=collecting_image_from_google_maps, args=(ds,))
                jobs.append(job)
                job.start()

            for job in jobs:
                job.join()
            not_complete_list = check_collecting_images_result(pd.DataFrame(data_listing))
            if not not_complete_list:
                complete_collected_images = True
        print('complete iteration')
    end_time = time.time()
    print(f"total time taken to do jobs is: {end_time - start_time}")
    """
    :return:
    """


def collect_surface_data(filename, surface_save_directory):
    used_keyword = []
    len_keyword = 1
    regencies, location = setup_location()
    locations = []
    max_iteration = 100
    for regency in regencies:
        locations.append(f"{regency} {location}".capitalize())

    while len_keyword != 0:
        with open(filename, 'r') as f:
            keyword_list = f.read().splitlines()
            keywords = check_surface_results_keyword(surface_save_directory, keyword_list)
            print(f"keywords are : {keywords} \n\n")
            for keyword in keywords:
                print(f"\n\nsearching keyword for : {keyword}")
                data = []
                premature_data = {}

                for location in locations:
                    surface_scraping_filename = f"surface_scraping_result/{keyword}_{str(datetime.datetime.now().strftime('%d_%m_%Y'))}.csv"
                    data.append(google_maps_location_collection([keyword], location, max_iteration))
                for result in data:
                    for key, val in result.items():
                        new_df = pd.DataFrame(val)
                        premature_data[key] = pd.concat([premature_data.get(key), new_df])
                for data, val in premature_data.items():
                    data_listing = val.to_dict('records')
                    save_surface_scraping_result(surface_scraping_filename, data_listing, keyword)
            len_keyword = len(check_surface_results_keyword(surface_save_directory, keyword_list))


def collect_deep_data():
    pass


def collect_image_data():
    pass


if __name__ == '__main__':
    # freeze_support()
    # setup_collecting_surface_data()
    # main()
    collect_surface_data('search_keyword.txt','surface_scraping_result')
    # collect_image_of_current_data(r'surface_scraping_result/villa_15_11_2022.csv')
