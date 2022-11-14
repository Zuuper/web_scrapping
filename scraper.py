import datetime
import time
from multiprocessing.pool import Pool

import numpy as np
import pandas as pd
from multiprocessing import Queue, cpu_count, Process, pool, Manager, freeze_support

from tqdm import tqdm

from utilities.scraper_utility import google_maps_utility
from utilities.scraper_utility.google_maps_utility import MapsDataCollection
import requests
from selenium.webdriver.chrome.options import Options
from utilities.utils import setup_bag_of_search_word, setup_location
from hanging_threads import start_monitoring

pd.options.mode.chained_assignment = None  # default='warn'


def setup_scraper_configuration():
    bag_of_words = setup_bag_of_search_word()
    regencies, location = setup_location()
    regency_keyword = []
    for regency in regencies:
        regency_keyword.append(f"{regency} {location}".capitalize())
    return bag_of_words, regency_keyword


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
        premature_data = engine.location_search(max_iteration=max_iteration, vertical_coordinate=100000)
        # engine.driver.quit()
        time.sleep(1)
        print(f"{log} finish total data: {len(premature_data)}")
        data[param] = premature_data
        engine.driver.quit()
    # queue_.put(data)
    return data


def google_maps_deep_search(data, queue_: Queue):
    config_dir = "config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    engine = maps_collection(config_dir, options=init_second_options())
    result = engine.deep_search(data)
    queue_.put(result)
    return result


def multiprocessing_location_collection(search_param, locations, max_iteration, queue_: Queue = ""):
    config_dir = "config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    data = {}
    #   First search the surface
    for location in locations:
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
            premature_data = engine.location_search(max_iteration=max_iteration, vertical_coordinate=100000)
            # engine.driver.quit()
            time.sleep(1)
            print(f"{log} finish total data: {len(premature_data)}")
            data[param] = premature_data
    # queue_.put(data)
    return data


def save_surface_scraping_result(file_location, data):
    df = pd.DataFrame()
    data = pd.DataFrame(data)
    try:
        data.to_csv(file_location, mode='a', index=False, header=False)
    except:
        data.to_csv(file_location, index=False)


def check_surface_scarping_data(file_location):
    df = pd.read_csv(file_location)
    df.drop_duplicates()
    df.to_csv(file_location, mode="")


def main():
    cpu = int(cpu_count() / 2)
    bag_of_words, locations = setup_scraper_configuration()
    premature_data = {}
    data = []
    start_time = time.time()
    max_iteration = 2
    for word in bag_of_words:
        premature_data[word] = pd.DataFrame()

    for location in locations:
        data.append(google_maps_location_collection(bag_of_words, location, max_iteration))

    # with Pool(processes=cpu) as pool_:
    #     items = [(bag_of_words, location, max_iteration) for location in locations]
    #     pool_.starmap(google_maps_location_collection, items)
    #     pool_.close()
    #     pool_.join()
    #     # for key, val in result.items():
    #     #     premature_data[key] = val.concat(result, ignore_index=True)

    jobs = []
    # locations_split = np.array_split(locations, cpu)
    # for locations in locations_split:
    #     job = Process(target=multiprocessing_location_collection, args=(bag_of_words, locations, max_iteration))
    #     jobs.append(job)
    #     job.start()
    # for job in jobs:
    #     job.join()
    end_time = time.time()
    print(f"total data: {len(data)}")
    for result in data:
        for key, val in result.items():
            new_df = pd.DataFrame(val)
            premature_data[key] = pd.concat([premature_data.get(key), new_df])

    monitoring_thread = start_monitoring(seconds_frozen=10, test_interval=100)
    for data, val in premature_data.items():
        val.to_csv(f"surface_scraping_result/{data}_{str(datetime.datetime.now().strftime('%d_%m_%Y'))}.csv",
                   index=False)
        data_listing = val.to_dict('record')
        new_data = []
        data_split = np.array_split(data_listing, cpu)
        jobs = []
        queue_ = Queue()
        for ds in data_split:
            job = Process(target=google_maps_deep_search, args=(ds, queue_))
            job.start()
            jobs.append(job)
        for job in jobs:
            job.join()
        print(f"\n\n jobs done for collecting data: {data}")
        while not queue_.empty():
            res = queue_.get()
            new_data.extend(res)
        print(new_data)
        new_df = pd.DataFrame(new_data)
        new_df.to_csv(f"data_scraping_result/{data}_{str(datetime.datetime.now().strftime('%d_%m_%Y'))}.csv")
    print(f"total time taken to do jobs is: {end_time - start_time}")
    """
    :return:
    """


if __name__ == "__main__":
    # freeze_support()
    main()
