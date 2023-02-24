import datetime
import json
import os
import time
from multiprocessing import Queue, cpu_count, Process

import numpy as np
import pandas as pd
from dill.pointers import parent
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from utilities.scraper_utility import google_maps_utility, google_utility
from utilities.utils import setup_bag_of_search_word, setup_location, setup_collecting_surface_data, \
    check_word_similarities

pd.options.mode.chained_assignment = None  # default='warn'
used_cpu = int(cpu_count() / 2) if int(cpu_count() / 2) >= 1 else 1
parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
parent_directory = f'{parent_directory}\web_scrapping'


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


def setup_input_from_surface_result_with_group():
    list_dir = os.listdir(f'{parent_directory}/text_data/step_1_grouped')
    print('select data you want to search by csv file')
    list_dir_len = len(list_dir)
    for index in range(list_dir_len):
        print(f' {index + 1}. {list_dir[index]}')
    input_success = False
    while not input_success:
        try:
            input_user = int(input('pick the number above: '))
            if input_user > list_dir_len or input_user < 1:
                raise Exception(f'you should put number between 1 and {list_dir_len}')

            return list_dir[input_user - 1]
        except Exception as e:
            print(e)


def setup_keyword_for_surface_search():
    list_dir = ['search_keyword_activity.txt', 'search_keyword_hotel.txt', 'search_keyword_restaurant.txt',
                'search_keyword_villa.txt']
    print('select file keyword you want to user: ')
    list_dir_len = len(list_dir)
    for index in range(list_dir_len):
        print(f' {index + 1}. {list_dir[index]}')
    input_success = False
    while not input_success:
        try:
            input_user = int(input('pick the number above: '))
            if input_user > list_dir_len or input_user < 1:
                raise Exception(f'you should put number between 1 and {list_dir_len}')

            return list_dir[input_user - 1]
        except Exception as e:
            print(e)


def init_options():
    options = Options()
    data = json.load(open(f'{parent_directory}/config/browser_option.json'))
    options.headless = data['headless']
    # options.add_argument("--kiosk")
    options.add_argument(data['lang'])
    options.add_argument(data['user-data-dir'])
    options.add_argument(data['profile-dir'])
    options.add_argument(data['windows-size'])
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
    config_dir = f"{parent_directory}/config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    data = {}
    #   First search the surface
    for param in search_param:
        try:
            engine = maps_collection(config_dir, options=init_options())
            log = f"log for {location} | {param} =>"
            print(f"{datetime.datetime.now()} {log} Started ")
            engine.open_google_maps()
            print(f'{datetime.datetime.now()} {log} open google maps')
            engine.search_by_searchbar(location)
            print(f'{datetime.datetime.now()} {log} search on google maps')
            time.sleep(1)
            engine.check_nearby()
            print(f'{datetime.datetime.now()} {log} click nearby')
            time.sleep(1)
            engine.search_by_searchbar(param)
            print(f'{datetime.datetime.now()} {log} search again')
            print(f'{datetime.datetime.now()} {log} prepare...')
            time.sleep(1)
            premature_data = engine.location_search(max_iteration=max_iteration, vertical_coordinate=100000)
            # engine.driver.quit()
            print(f"{datetime.datetime.now()} {log} finish total data: {len(premature_data)}")
            data[param] = premature_data
        except Exception as e:
            print(e)
            continue
        engine.driver.quit()
    # queue_.put(data)
    return data


def google_search(search_param):
    config_dir = f"{parent_directory}/config/google_search.json"
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


def google_maps_deep_search(data, queue_: Queue):
    config_dir = f"{parent_directory}/config/map_search.json"
    maps_collection = google_maps_utility.MapsDataCollection
    engine = maps_collection(config_dir, options=init_second_options())
    result = engine.deep_search(data)
    queue_.put(result)
    return result


def deep_search_single_data(data, filename):
    config_dir = f"{parent_directory}/config/map_search.json"
    daily_file_name = ""

    if "villa" in filename:
        daily_file_name = "villa"
    elif "restaurant" in filename:
        daily_file_name = "restaurant"
    elif "activity" in filename:
        daily_file_name = "activity"
    elif "hotel" in filename:
        daily_file_name = "hotel"

    for d in data:
        try:
            maps_collection = google_maps_utility.MapsDataCollection
            engine = maps_collection(config_dir, options=init_options())
            try:
                result = engine.individual_deep_search(d)
            except Exception as e:
                continue
            df = pd.DataFrame([result])

            try:
                default_df = pd.read_csv(filename)
                new_df = pd.concat([default_df, df])
                new_df.to_csv(filename, index=False)
                # df.to_csv(filename, mode="a", index=True, header=is_using_header)
                print(f'{datetime.datetime.now()} success adding new data to csv')
            except Exception as e:
                print(e)
                df.to_csv(filename, index=False)
                print(f'{datetime.datetime.now()} success creating new csv file')

            # daily_filename = f"data_scraping_daily/{daily_file_name}_{datetime.datetime.now().date()}.csv"
            # try:
            #     default_df = pd.read_csv(daily_filename)
            #     new_df = pd.concat([default_df, df])
            #     new_df.to_csv(daily_filename, index=False)
            #     print(f'{datetime.datetime.now()} success adding new data to daily result csv')
            # except Exception as e:
            #     print(f"error when adding data to daily csv {e}")
            #     new_df.to_csv(daily_filename, index=False)
            #     pass
            engine.driver.quit()
        except Exception as e:
            print(f"{datetime.datetime.now()} error : {e}")
            continue
    pass


def save_surface_scraping_result(filename, data, keyword):
    data = pd.DataFrame(data)
    data = data.drop_duplicates()
    try:
        default_df = pd.read_csv(filename)
        new_df = pd.concat([default_df, data])
        res = new_df.drop_duplicates(keep="last", subset=['title'])
        res['title'] = res['title'].str.replace(r'[^\w\s]+', '', regex=True)
        res['keyword'] = keyword
        res.to_csv(filename, index=False)
        # df.to_csv(filename, mode="a", index=True, header=is_using_header)
        print(f'{datetime.datetime.now()} success adding new data to csv')
    except Exception as e:
        print(e)
        data['keyword'] = keyword
        data['title'] = data['title'].str.replace(r'[^\w\s]+', '', regex=True)
        data.to_csv(filename, index=False)
        print(f'{datetime.datetime.now()} success creating new csv file')


def check_duplicates(filename):
    df = pd.read_csv(filename)
    print(len(df))
    new_df = df.drop_duplicates(keep="last", subset='title')
    print(len(new_df))
    new_df.to_csv(filename, index=False)


def check_surface_scarping_data(file_location):
    df = pd.read_csv(file_location)
    df.drop_duplicates(subset='title')
    df.to_csv(file_location, index=False)


def search_description_and_email_from_google(keyword):
    config_dir = f"{parent_directory}/config/google_search.json"
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
        not_complete_data = not_complete_data.drop_duplicates(keep='last')
        return not_complete_data.to_dict('records')
    else:
        surface_scraping_df = surface_scraping_df.drop_duplicates(keep='last')
        return surface_scraping_df.to_dict('records')


def check_excel_scraping_result(scraping_result_filename, surface_scraping_result):
    avail_scraping_df = False
    try:
        scraping_df = pd.read_excel(scraping_result_filename)
        avail_scraping_df = True
    except:
        scraping_df = None

    if type(surface_scraping_result) == str:
        surface_scraping_df = pd.read_excel(surface_scraping_result)
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
    config_dir = f"{parent_directory}/config/map_search.json"
    for d in data:
        maps_collection = google_maps_utility.MapsDataCollection
        engine = maps_collection(config_dir, options=init_options())
        engine.driver.get(d['link'])
        title = str(d['title']).strip(" ")
        try:
            engine.image_collection(title, f'{parent_directory}/image_data/{title}')
            print('finish')
            # set_report_image_result(title)
        except Exception as e:
            print(e)
        engine.driver.quit()


def set_report_image_result(title):
    data = {'title': title}
    df = pd.DataFrame(data, index=[0])
    daily_filename = f"data_scraping_images_daily/images_{datetime.datetime.now().date()}.csv"
    print(daily_filename)
    try:
        default_df = pd.read_csv(daily_filename)
        new_df = pd.concat([default_df, df])
        new_df.to_csv(daily_filename, index=False)
        # df.to_csv(filename, mode="a", index=True, header=is_using_header)
        print(f'{datetime.datetime.now()} success adding new data to csv')
    except Exception as e:
        print(e)
        df.to_csv(daily_filename, index=False)
        print(f'{datetime.datetime.now()} success creating new csv file')


def check_collecting_images_result(surface_scraping_result):
    img_gallery = os.listdir(f'{parent_directory}/images_data')
    if type(surface_scraping_result) == 'str':
        surface_scraping_df = pd.read_csv(surface_scraping_result)
    elif type(surface_scraping_result) == 'list':
        surface_scraping_df = pd.DataFrame(surface_scraping_result)
    else:
        surface_scraping_df = surface_scraping_result

    not_complete_data = surface_scraping_df[~surface_scraping_df['title'].isin(img_gallery)]
    print(not_complete_data)
    return not_complete_data.to_dict('records')


def collect_image_of_current_data(scraping_result_location):
    cpu = used_cpu
    df = pd.read_csv(scraping_result_location)
    complete_collected_images = False
    df['title'] = df['title'].str.replace(r'[^\w\s]+', '', regex=True)
    not_complete_list = check_collecting_images_result(pd.DataFrame(df))
    print(f"total not images profile missing is: {len(not_complete_list)}")
    jobs = []
    data_split = np.array_split(not_complete_list, cpu)
    for ds in data_split:
        job = Process(target=collecting_image_from_google_maps, args=(ds,))
        jobs.append(job)
        job.start()

    for job in jobs:
        job.join()
    not_complete_list = check_collecting_images_result(df)
    complete_collected_images = True
    print(f"{datetime.datetime.now()} finish all image collection")


def check_surface_results_keyword(filedir, keywords: [], location=""):
    listdir = os.listdir(filedir)
    new_listdir = []
    new_location_dir = []
    for dir_ in listdir:
        title = dir_.split('_')
        new_listdir.append(title[0])
        location_dir = title[1].split('.')
        new_location_dir.append(location_dir[0])
    new_keyword = []
    for word in keywords:
        if word in new_listdir and location in new_location_dir:
            continue
        new_keyword.append(word)
    return sorted(set(new_keyword))


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
            # keywords = check_surface_results_keyword(surface_save_directory, keyword_list, regencies)
            keywords = keyword_list
            print(f"keywords are : {keywords} \n\n")
            if len(keywords) == 0:
                break
            for keyword in keywords:
                print(f"\n\nsearching keyword for : {keyword}")
                data = []
                premature_data = {}

                for location in locations:
                    surface_scraping_filename = f"surface_scraping_result/{keyword}_{str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M'))}.csv "
                    data.append(google_maps_location_collection([keyword], location, max_iteration))
                for result in data:
                    for key, val in result.items():
                        new_df = pd.DataFrame(val)
                        premature_data[key] = pd.concat([premature_data.get(key), new_df])
                for data, val in premature_data.items():
                    data_listing = val.to_dict('records')
                    save_surface_scraping_result(surface_scraping_filename, data_listing, keyword)
            len_keyword = len(check_surface_results_keyword(surface_save_directory, keywords))
            print(f"result len keyword is {len_keyword}")


def setup_surface_scraping_result_with_consistent_name():
    list_dir = os.listdir(f'{parent_directory}/text_data/step_1')
    for dir_ in list_dir:
        name_split = dir_.split("_")
        name = name_split[0]
        true_name = check_word_similarities('config/scraper_result_classification', name)
        true_filename = f'surface_result_with_group/{true_name}.csv'
        print(f"{dir_} -> {true_name}")
        df = pd.read_csv(f"surface_scraping_result/{dir_}")
        print(len(df))
        try:
            save_surface_scraping_result(true_filename, df, '')
        except:
            df = df.drop_duplicates(subset='title', keep="last")
            df['title'] = df['title'].str.replace(r'[^\w\s]+', '')
            df.to_csv(true_filename, index=False)


def collect_surface_and_deep_data(filename, surface_save_directory):
    cpu = used_cpu
    regencies, location = setup_location()
    locations = []
    max_iteration = 100
    province = location
    for regency in regencies:
        locations.append(f"{regency} {location}".capitalize())
    with open(filename, 'r') as f:
        keyword_list = f.read().splitlines()
        keywords = check_surface_results_keyword(surface_save_directory, keyword_list, location)
        print(f"keywords are: {keywords} \n\n")
        for keyword in keywords:
            print(f"\n\nsearching keyword for : {keyword}")
            data = []
            premature_data = {}
            for location in locations:
                surface_scraping_filename = f"{parent_directory}/text_data/step_1/{keyword}_{province}.csv"
                result = google_maps_location_collection([keyword], location, max_iteration)
                data.append(result)

            print(f"\nFinish Collecting data for surface search")
            for result in data:
                for key, val in result.items():
                    new_df = pd.DataFrame(val)
                    premature_data[key] = pd.concat([premature_data.get(key), new_df])
            for data, val in premature_data.items():
                print(f"starting to do deep search")
                true_name = check_word_similarities(f"{parent_directory}/config/scraper_result_classification", keyword)
                true_dir = f'{parent_directory}/text_data/step_1_grouped/{true_name}.csv'
                deep_scraping_filename = f"{parent_directory}/text_data/step_1_grouped/{true_name}.csv"
                try:
                    df_temp = pd.read_csv(deep_scraping_filename)
                except Exception as e:
                    print(f'save directory is not available, creating new one')
                    df_temp = pd.DataFrame()

                df_temp.to_csv(deep_scraping_filename, index=False)

                not_complete_list = check_scraping_result(deep_scraping_filename, val)
                save_surface_scraping_result(true_dir, not_complete_list, keyword)
                save_surface_scraping_result(surface_scraping_filename, val.to_dict('records'), keyword)
                print(f"total data need to collected for {keyword} => {len(not_complete_list)}")
                completed = False

                while not completed:
                    jobs = []
                    data_split = np.array_split(not_complete_list, cpu)

                    for ds in data_split:
                        job = Process(target=deep_search_single_data, args=(ds, deep_scraping_filename))
                        jobs.append(job)
                        job.start()

                    for job in jobs:
                        job.join()

                    not_complete_list = check_scraping_result(deep_scraping_filename,
                                                              pd.DataFrame(not_complete_list))
                    if len(not_complete_list) == 0:
                        print(f"finish collecting all data for {keyword}")
                        completed = True


def collect_deep_data(surface_result_file_location=None):
    cpu = used_cpu
    listdir = os.listdir(f'{parent_directory}/text_data/step_1_grouped')

    def collect_scraping_result(dir_name, deep_scraping_result_filename):
        df = pd.read_csv(f"{parent_directory}/text_data/step_1_grouped/{dir_name}")
        return check_scraping_result(deep_scraping_result_filename, df)

    def jobs_process(job_data):
        job_data = job_data
        jobs = []
        data_split = np.array_split(job_data, cpu)
        for ds in data_split:
            job = Process(target=deep_search_single_data, args=(ds, deep_scraping_filename))
            jobs.append(job)
            job.start()
        for job in jobs:
            job.join()

    if surface_result_file_location:
        file_location = surface_result_file_location.split('/')
        deep_scraping_filename = f"{parent_directory}text_data/step_1/{file_location[len(file_location) - 1]}"
        not_complete_list = collect_scraping_result(surface_result_file_location, deep_scraping_filename)
        print(f"total not completed : {json.dumps(not_complete_list, indent=4)}")
        print(f"total not completed : {len(not_complete_list)}")
        jobs_process(not_complete_list)
    else:
        for dir_ in listdir:
            deep_scraping_filename = f"{parent_directory}text_data/step_1_grouped/{dir_}"
            not_complete_list = collect_scraping_result(dir_, deep_scraping_filename)
            # data_listing = df.to_dict('records')
            print(f"total not completed : {not_complete_list}")
            jobs_process(not_complete_list)


def format_scraping_result(filename):
    df = pd.read_csv(f"data_scraping_result/{filename}")
    villa_col_name = ['title', 'address', 'contact_number', 'amenities', 'coordinate', 'regency', 'link']
    food_col_name = ['title', 'short_description', 'address', 'contact_number', 'price_level', 'sub_category',
                     'amenities', 'regency', 'coordinate', 'open_hours', 'link']
    wow_col_name = ['title', 'sub_category', 'short_description', 'address', 'contact_number', 'site', 'amenities',
                    'regency', 'coordinate', 'open_hours', 'link']

    if "villa" in filename:
        new_df = df[villa_col_name]
    elif "restaurant" in filename:
        new_df = df[food_col_name]
    elif "activity" in filename:
        new_df = df[wow_col_name]
    else:
        return 0

    new_df.to_csv(f"data_scraping_for_bot/{filename}", index=False)


if __name__ == '__main__':
    # main()
    collect_surface_and_deep_data(f'{parent_directory}/keywords/search_keyword.txt', 'surface_scraping_result')
    # setup_surface_scraping_result_with_consistent_name()
    # check_duplicates('surface_result_with_group/villa.csv')
    collect_deep_data('villa.csv')
    collect_image_of_current_data(r'surface_result_with_group/villa.csv')
    format_scraping_result('villa.csv')
    # update