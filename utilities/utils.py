import time

from geopy import Nominatim
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
import os


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


def find_value_of_element(element: WebElement, attr, x_path, element_position=0):
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

