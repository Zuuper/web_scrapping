import threading
import time
from selenium.webdriver.chrome.options import Options
import pandas as pd
from utilities import google_maps_utility, setup_search, google_utility, init_instagram_data_collection
from geopy.geocoders import Nominatim
import multiprocessing


def setup_search_backup():
    web_option_list = ['google maps', 'other']
    search_area = ['stay', 'restaurant', 'nature and ']
    print('!!! WEB SCRAPPER !!!')
    print("where do you want to search ? the options:")
    for idx in range(len(web_option_list)):
        print(f"{idx + 1}. {web_option_list[idx]}")
    website = int(input("your choice (pick number): "))
    if not website or website > len(web_option_list):
        website = int(input("pick again, make sure you pick a number of the options: "))
    website = web_option_list[website - 1]
    query = input("what you want to search ? ")
    location = input('where do you want to search ? pick only one location ')
    loc = Nominatim(user_agent="GetLoc")
    getloc = loc.geocode(location)
    position = {'lat': getloc.latitude, 'lon': getloc.longitude}
    print(getloc)
    print(f"your coordinate are : {position}")
    return website, query, position


def main_backup():
    config_dir = "config/map_search.json"
    website, query, position = setup_search()
    options = Options()
    # options.headless = True
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1336,768")
    if website == 'google maps':
        engine = google_maps_utility.MapsDataCollection(config_dir, options)
        engine.search_on_map(query, position)
        # engine.init_location(position)
        # print(engine.position)
        data = engine.surface_search(max_iteration=100, vertical_coordinate=100000)
        df = pd.DataFrame(data)
        df = df.drop_duplicates()
        df.to_excel(f'{query}_surface_search.xlsx')
        print('finish exporting data, web scraping is done 100%. enjoy')
    else:
        print('you only can search on google maps for now')


def google_maps_collection(search_param, location, max_iteration=100):
    config_dir = "config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    options = Options()
    # options.headless = True
    # options.add_argument("--kiosk")
    options.add_argument("--lang=en-US")
    options.add_argument(r"--user-data-dir=C:\Users\Asus\AppData\Local\Google\Chrome\User Data")
    options.add_argument(r'--profile-directory=Default')
    options.add_argument("--window-size=1336,768")
    engine = maps_collection(config_dir, options)
    position = {'lat': location.latitude, 'lon': location.longitude}
    engine.search_on_map(search_param, position)

    data = engine.surface_search(max_iteration=max_iteration, vertical_coordinate=100000)
    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    df.to_excel(f'{search_param}_surface_search.xlsx')
    print('finish exporting data, web scraping is done 100%. enjoy')
    return data


def google_collection(search_param):
    config_dir = "config/google_search.json"
    google = google_utility.GoogleCollection
    options = Options()
    options.headless = True
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1280,720")
    engine = google(config_dir, options)
    engine.search_data(search_param)
    return engine.get_first_search()


def get_instagram_user_from_google(search_value: list, search_area: str, search_location: str, saved_list: list):
    print(f'query param: {search_area} {search_value} {search_location} instagram')
    result = google_collection(f"{search_area} {search_value} {search_location} instagram").split(" ")
    for res in result:
        if res.startswith("("):
            res = res.replace('(', '')
            res = res.replace(')', '')
            if res.startswith('@'):
                query = res.replace("@", "")
                print(f'getting instagram post for {query}')
                saved_list.append(query)


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
    search_area, search_param, search_engine, search_location, detail_search_location, instagram_scrap = setup_search()
    print(search_area, search_param, search_engine, search_location, instagram_scrap)
    data = []
    if search_engine == 'google maps':
        data = google_maps_collection(f'{search_param} near {search_location.address}', search_location,
                                      max_iteration=100)
    elif search_engine == 'booking.com':
        pass

    queries = []
    search_value = list(dict.fromkeys([d['title'] for d in data]))

    # for d in data:
    #     search_value = d['title']
    #     result = google_collection(f"{search_value} instagram").split(" ")
    #     # print(f'possible instagram: {result}')
    #     for res in result:
    #         if res.startswith("("):
    #             res = res.replace('(', '')
    #             res = res.replace(')', '')
    #             if res.startswith('@'):
    #                 query = res.replace("@", "")
    #                 print(f'getting instagram post for {query}')
    #                 queries.append(query)
    jobs = []
    for search in search_value:
        job = threading.Thread(target=get_instagram_user_from_google, args=[search, search_area,
                                                                            detail_search_location, queries])
        jobs.append(job)
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()

    print(queries)
    # init_instagram_data_collection(queries, instagram_scrap, 20, False, total_pagination=5, total_media_pagination=4)


if __name__ == "__main__":
    main()
