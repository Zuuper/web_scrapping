import datetime

from fuzzywuzzy import process

import pandas as pd
from geopy import Nominatim
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
import os

parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
parent_directory = f'{parent_directory}\web_scrapping'


def search_on_maps_only_query(query: str, driver: WebDriver):
    return driver.get(query) if query and driver else ValueError('parameter is missing')


def check_element(driver: WebDriver, x_path):
    try:
        driver.find_element(By.XPATH, x_path)
        return True
    except Exception as e:
        return False


def process_single_value(driver: WebDriver, attr, x_path):
    is_avail = check_element(driver, x_path)
    try:
        return driver.find_element(By.XPATH, x_path).text if attr == 'text' \
            else driver.find_element(By.XPATH, x_path).get_attribute(attr)
    except Exception as e:
        return ''


def find_value_of_element(element: WebDriver, attr, x_path, element_position=0):
    try:
        return element.find_element(By.XPATH, x_path).text if attr == "text" else \
            element.find_element(By.XPATH,
                                 f"({x_path}){[element_position]}" if element_position else x_path).get_attribute(attr)
    except Exception as e:
        return ""


def get_data_to_search():
    check_if_get_data = False
    data = ''
    while not check_if_get_data:
        try:
            query = str(input("what you want to search ? "))
            data = query if query else ""
            check_if_get_data = True if data else False
        except Exception as e:
            print(e)
            pass
    return data


def enable_advance_search():
    check_if_advance_search = False
    data = ''
    while not check_if_advance_search:
        try:
            is_advance_search = int(input("enable advance search ? \n "
                                          "1. enable \n"
                                          "0. disabled \n"
                                          "your choice : "))
            data = True if is_advance_search > 0 else False
            check_if_advance_search = True
        except Exception as e:
            print('oops, you should pick number, try again..')
            check_if_advance_search = False

    return data


def advance_setup_search():
    mark = "!" * 3
    print(f'{mark} ADVANCE WEB SCRAPPER {mark} \n')
    query = input("what you want to search ? ")
    check_if_advance_search = False
    while not check_if_advance_search:
        try:
            is_advance_search = int(input("enable advance search ? \n "
                                          "1. enable \n"
                                          "0. disabled \n"
                                          "your choice : "))
            is_advance_search = True if is_advance_search > 0 else False
            check_if_advance_search = True
        except Exception as e:
            print('oops, you should pick number, try again..')
            check_if_advance_search = False
    check_if_get_location = False
    while not check_if_get_location:
        try:
            location = input('where do you want to search ? pick only one location ')
            loc = Nominatim(user_agent="GetLoc")
            get_location = loc.geocode(location)
            print(get_location)
            print('')
        except Exception as e:
            print(e)


def get_location_on_map():
    get_location = False
    while not get_location:
        try:
            location = input('where do you want to search ? pick only one location ')
            loc = Nominatim(user_agent="GetLoc")
            get_location_area = loc.geocode(location)
            for x in get_location_area:
                print(x)
            location_validation = input('is this your true area location ? click enter if it correct ')
            get_location = True if not location_validation else False
        except Exception as e:
            print(e)
            get_location = False

    reverse_location = loc.reverse(f"{get_location_area.latitude}, {get_location_area.longitude}").raw
    print('pick specific location input for more detail search')
    location_num = 1
    detail_location = []
    address = reverse_location['address']
    for key, value in address.items():
        print(f"{location_num}. {key}: {value}")
        location_num += 1
        detail_location.append(key)
    detail_location_choice = input('your choice (can do multiple, ex = 1,2,3 ):  ').split(',')

    true_choice = []
    for choice in detail_location_choice:
        choice_value = detail_location[int(choice) - 1]
        true_choice.append(address[choice_value])
    user_choice = "".join(f"{str(value)} " for value in true_choice)
    return get_location_area, user_choice


def get_type_of_search():
    search_area = ['stay', 'restaurant', 'landmark and activity', 'other']
    get_search = False
    search = 0
    while not get_search:
        try:
            print('what type search your want ? select only one')
            for idx in range(len(search_area)):
                print(f'{idx + 1}. {search_area[idx]}')
            search = int(input('your choice (pick number): '))
            if search > len(search_area) or search <= 0:
                raise Exception('option is out of range')
            get_search = True
        except Exception as e:
            print('oops, you should pick number, try again..')
            get_search = False

    return search_area[search - 1]


def set_search_engine(search_area):
    search_area_list = ['stay', 'restaurant', 'landmark and activity', 'other']
    option = ['google maps']
    get_search_engine = False
    search = 0
    if search_area and search_area in search_area_list:
        if search_area == 'stay':
            option.append('booking.com')
        while not get_search_engine:
            try:
                print('where do you want to search? select only one')
                for idx in range(len(option)):
                    print(f'{idx + 1}. {option[idx]}')
                search = int(input('your choice (pick number): '))
                if search > len(search_area) or search <= 0:
                    raise Exception('option is out of range')
                get_search_engine = True
            except Exception as e:
                print('oops, you should pick number, try again..')
                get_search_engine = False
        return option[search - 1]

    raise Exception('something wrong with your search_area parameter :(')


def instagram_scrap_setup():
    options = ['feed', 'video', 'reels', 'igtv', 'albums']
    finish_setup = False
    while not finish_setup:
        try:
            print('for instagram setup, pick type content you want to collect')
            for idx in range(len(options)):
                print(f'{idx + 1}. {options[idx]} ')
            scrap_setup = input('your choice (can do multiple, ex = 1,2,3 ):  ').split(',')
            finish_setup = True
        except Exception as e:
            print(e)
            finish_setup = False
    print(scrap_setup)
    second_setup_finish = False
    while not second_setup_finish:
        data = {}
        try:
            for idx in scrap_setup:
                option_name = options[int(idx) - 1]
                if option_name in data and data[option_name]:
                    continue
                value = int(input(f"for the {option_name}, how much data you want to collect ? "))
                data[option_name] = value
            second_setup_finish = True
        except Exception as e:
            print(e)
            second_setup_finish = False

    return data


def setup_search():
    search_area = get_type_of_search()
    search_engine = set_search_engine(search_area)
    search_param = get_data_to_search()
    search_location, detail_search_location = get_location_on_map()
    instagram_scrap = instagram_scrap_setup()
    return search_area, search_param, search_engine, search_location, detail_search_location, instagram_scrap


def generate_folder(file_location, file_name='', is_parent_folder=True):
    folder_avail = os.path.isdir(file_location)
    if not folder_avail and is_parent_folder:
        os.makedirs(file_location)
        os.makedirs(f'{file_location}/photos')
        os.makedirs(f'{file_location}/videos')
        os.makedirs(f'{file_location}/reels')
        os.makedirs(f'{file_location}/igtv')
        os.makedirs(f'{file_location}/albums')

    elif folder_avail and not is_parent_folder:
        new_file_location = f'{file_location}/{file_name}'
        folder_avail_child = os.path.isdir(new_file_location)
        if not folder_avail_child:
            os.makedirs(new_file_location)


def setup_bag_of_search_word():
    validation = False
    while not validation:
        try:
            input_bag = input("set your bag of search word (support multiple value, separate keywords by ',' \n")
            bag = str(input_bag).split(",")
            print(bag)
            pre_validation = input('wanna change bag of search words ? (click enter to ignore)')
            validation = True if not pre_validation else False
        except Exception as e:
            print(e)
            continue
    return bag


def setup_collecting_surface_data():
    try:
        using_surface_search = True
        filename_ = ''
        date_now = str(datetime.datetime.now().strftime('%d_%m_%Y'))
        surface_folder = r'surface_scraping_result'
        surface_dir = os.listdir(surface_folder)
        file_with_date_today = []
        for dir_ in surface_dir:
            if date_now in dir_:
                file_with_date_today.append(dir_)
        if file_with_date_today:
            print(f"we found {len(file_with_date_today)} result for scraping today, want to use the latest result ? ")
            for idx in range(len(file_with_date_today)):
                print(f"{idx + 1}. {file_with_date_today[idx]}")
            print('0. create new scraping result')
            validation = False
            while not validation:
                try:
                    input_ = int(input("pick one of options \n"))
                    if input_ > len(file_with_date_today) or input_ < 0:
                        raise ValueError("wrong input, try again")
                    else:
                        pre_validation = input('wanna change of of location ? (click enter to ignore)')
                        validation = True if not pre_validation else False
                        using_surface_search = True if input_ == 0 else False
                        filename_ = file_with_date_today[input_ - 1] if input_ > 0 else ""
                except Exception as e:
                    print(e)
        return using_surface_search, filename_
    except Exception as e:
        print(e)


def get_duplicates(lst):
    frequency = {}
    duplicates = []
    for item in lst:
        item = item.lstrip().rstrip()
        if item in frequency:
            frequency[item] += 1
            duplicates.append(item)
        else:
            frequency[item] = 1
    return duplicates


def setup_location():
    df = pd.read_csv(f'{parent_directory}/country_data/worldcities.csv')
    validation = False
    while not validation:
        try:
            input_location = str(input("set your location of search "))
            regency = df.loc[df['country'] == input_location.title()]
            regency = regency['city'].drop_duplicates()
            print(regency)
            pre_validation = input('wanna change of of location ? (click enter to ignore)')
            validation = True if not pre_validation else False
            print('---' * 20)
        except Exception as e:
            print(e)
            continue
    regency_list = regency.to_list()

    second_validation = False
    duplicates = []
    specific_interest_location_list = ['los angeles', 'austin', 'dallas', 'houston', 'san diego']
    while not second_validation:
        try:
            pre_validation = input('do you want to do search on specific area ? (click enter to ignore)')
            if not pre_validation:
                second_validation = True
                duplicates = regency_list
                break
            input_specific = str(input("set your specific location of search, you can select more "
                                       "than 2 by seperate each words with commas ',' ")).lower()
            list_data = input_specific.split(',')
            total_list = [regency.lower() for regency in regency_list]

            for data_ in list_data:
                total_list.append(data_)
            duplicates = get_duplicates(total_list)
            for data_ in list_data:
                duplicates.append(data_)
            duplicates = get_duplicates(duplicates)
            if duplicates:
                second_validation = True
        except Exception as e:
            print(e)
            continue
    result = []
    for data_ in duplicates:
        admin = df.loc[df['city'] == data_.title()]
        admin_list = admin['admin_name'].to_list()
        if len(admin) > 1:
            valid = False
            print('there is more than 1 cities name with different administration name, please pick one of this '
                  'choices: ')
            for admin_idx in range(len(admin_list)):
                print(f'{admin_idx + 1}. {admin_list[admin_idx]}')
            while not valid:
                user_choice = int(input('your choice is: '))
                if not user_choice:
                    print('choose of the choices')
                    continue
                if user_choice > len(admin_list) or user_choice < 0:
                    print(f'pick one choices from 1 to {len(admin_list)}')
                    continue
                res = f'{data_}, {admin_list[user_choice - 1]}'
                valid = True
        else:
            res = f'{data_}, {admin_list}'
        result.append(res)
    for specific_interest_location in specific_interest_location_list:
        if specific_interest_location in duplicates:
            df_city = pd.read_excel(
                f'{parent_directory}/city_data/excel_of_{specific_interest_location.replace(" ", "_").lstrip().rstrip()}_city.xlsx')
            city_list = df_city['City'].to_list()
            for city in city_list:
                data = f"{city}, {specific_interest_location}, {input_location}"
                result.append(data)
    print(result, input_location)
    return result, input_location


def time_formatter(time: datetime.datetime):
    return time.strftime("%d/%m/%Y %H:%M:%S")


def check_word_similarities(config_filedir, text):
    list_config = os.listdir(config_filedir)
    similarity_point = {}
    for config in list_config:
        split_title = config.split('.')
        title = split_title[0]
        with open(f'{config_filedir}/{config}', 'r') as f:
            list_word = f.readlines()
            res = process.extract(text, list_word, limit=1)
            similarity = 0
            len_res = len(res)
            for r in res:
                similarity += r[1]
            print(f"{title} : {round(similarity / len_res, 1)}")
            similarity_point[title] = round(similarity / len_res, 1)

    return max(similarity_point, key=similarity_point.get)
