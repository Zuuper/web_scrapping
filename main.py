import threading, queue
import time

import numpy as np
from selenium.webdriver.chrome.options import Options
import pandas as pd
from utilities import google_maps_utility, setup_search, google_utility, init_instagram_data_collection
from geopy.geocoders import Nominatim
from multiprocessing import cpu_count, Process, Queue, Lock
from hanging_threads import start_monitoring
import ssl
ssl._DEFAULT_CIPHERS = 'DES-CBC3-SHA'

monitoring_thread = start_monitoring(seconds_frozen=10, test_interval=100)


def google_maps_collection(search_param, location, max_iteration=100, using_multiprocessor=False, total_cpu=0):
    config_dir = "config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    options = Options()
    options.headless = True
    # options.add_argument("--kiosk")
    options.add_argument("--lang=en-US")
    options.add_argument(r"--user-data-dir=C:\Users\Asus\AppData\Local\Google\Chrome\User Data")
    options.add_argument(r'--profile-directory=Default')
    options.add_argument("--window-size=1336,768")
    engine = maps_collection(config_dir, options)
    position = {'lat': location.latitude, 'lon': location.longitude}
    engine.search_on_map(search_param, position)
    new_param = search_param.split(" ")
    new_param = new_param[2:]
    data = engine.location_search(max_iteration=max_iteration, vertical_coordinate=100000, location_detail=new_param)

    df = pd.DataFrame(engine.deep_search(data))
    # df = df.drop_duplicates()
    df.to_excel(f'{search_param}_surface_search.xlsx')
    print('finish exporting data, web scraping is done 100%. enjoy')
    return data


def google_collection(search_value, search_param, queue_: queue):
    config_dir = "config/google_search.json"
    google = google_utility.GoogleCollection
    options = Options()
    options.headless = True
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1280,720")
    results = []
    for search_ in search_value:
        engine = google(config_dir, options)
        engine.search_data(f'{search_} {search_param}')
        result = engine.get_first_search().split()
        for res in result:
            if res.startswith("("):
                res = res.replace('(', '')
                res = res.replace(')', '')
                if res.startswith('@'):
                    query = res.replace("@", "")
                    print(f'getting instagram post from {search_} with id {query}')
                    val = query
                    queue_.put([search_, val])
                    results.append(val)
    print('finish search')
    return results


def get_instagram_user_from_google(search_value: list, search_location: str, saved_list: list,
                                   queue_: Queue, using_queue=False, max_thread=2):
    """
    Get instagram user from Google search.
    :param search_value: list of value you want to search (ex: ['villa kembang sari', 'restaurant be guling'])
    :param search_location: location of search (ex: 'Badung Bali')
    :param saved_list: array where your want to put your temporary file
    :param queue_: Queue modul for multiprocessing
    :param using_queue:
    :param max_thread:
    :return:
    """
    jobs = []
    thread_queue = queue.Queue()
    print(f'length total of search value before checked is : {len(search_value)} ')
    search_value = [*set(search_value)]
    print(f'length total of search value before checked is : {len(search_value)} ')
    new_search_value = np.array_split(search_value, max_thread)

    for search_value in new_search_value:
        job = threading.Thread(target=google_collection, args=[search_value, f"{search_location} instagram",
                                                               thread_queue])
        jobs.append(job)
        job.start()

    for job in jobs:
        job.join()
    print('finishing all thread')
    while not thread_queue.empty():
        res = thread_queue.get()
        queue_.put(res)
    return saved_list


def main():
    """
    how it works ?
    1. get all premature data (ex: title) from primary source (ex: google maps, booking.com)
    2. find the instagram account based on premature data, search it from Google
    3. get all instagram user detail (total post, follower, following, etc)
    4. get all content needed based on user configuration
    5. profit :D
    :return:
    """
    total_cpu = int(cpu_count() / 2)
    print(total_cpu)
    max_thread = 2
    search_area, search_param, search_engine, search_location, detail_search_location, instagram_scrap = setup_search()
    # search_area, search_param, search_engine, search_location, \
    # detail_search_location, instagram_scrap = 'stay', 'villa', 'google maps', 'Badung, Bali, Indonesia', 'Badung, Bali', {'feed': 1}
    print(search_area, search_param, search_engine, search_location, detail_search_location, instagram_scrap)
    start = time.time()
    data = []
    if search_engine == 'google maps':
        data = google_maps_collection(f'{search_param} at {detail_search_location}', search_location,
                                      max_iteration=1, using_multiprocessor=True, total_cpu=total_cpu)
    elif search_engine == 'booking.com':
        pass
    end = time.time()
    print(f"total time consume to get all data from google maps is : {end - start} s")
    # queries = []
    # result = Queue()
    # search_value = list(dict.fromkeys([d['title'] for d in data]))
    # jobs = []
    print("collecting instagram ID...")
    # split_search_value = np.array_split(search_value, total_cpu)
    # for search_value in split_search_value:
    #     # search_value = [search_value[0], search_value[1], search_value[2]]
    #     job = Process(target=get_instagram_user_from_google, args=(search_value,
    #                                                                detail_search_location, queries,
    #                                                                result, True, max_thread))
    #     jobs.append(job)
    #     job.start()
    # print(f"line: 132 => {result}")
    #
    # for job in jobs:
    #     job.join()
    # print(f"line: 136 => {result}")
    # print(f'result after collecting data is {result}')
    # while not result.empty():
    #     queries.append(result.get())
    # print(f'total IG username is : {len(queries)}')
    # end = time.time()
    # print(f"total time consume to complete all is: {end - start}s")
    # print(queries)
    # init_instagram_data_collection(queries, instagram_scrap, 20, False, total_pagination=5, total_media_pagination=4)


if __name__ == "__main__":
    main()
