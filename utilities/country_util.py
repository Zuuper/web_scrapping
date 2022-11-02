import json
import string
import time
from multiprocessing import Queue, cpu_count, Process
import threading
import queue
import random
from re import S

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
from geopy.geocoders import Nominatim


def main():
    country_state_json = '../country_list/countries+states.json'
    cities_json = r'../country_list/cities.json'
    country_data = json.load(open(country_state_json, encoding="utf8"))
    cities_data = json.load(open(cities_json, encoding="utf8"))
    provinces = []
    regencies = []
    villages = []
    for country in country_data:
        data = {}
        if country['name'] == 'Indonesia':
            state_collection = country['states']
            for state in state_collection:
                provinces.append(state)
                temp_cities = [x for x in cities_data if
                               x['country_name'] == country['name'] and x['state_id'] == state['id']]
                country_name = country['name']
                province_name = state['name']
                total_cpu = cpu_count()
                temp_cities = np.array_split(temp_cities, total_cpu)
                result_regencies = Queue()
                result_villages = Queue()
                jobs = []
                for cities in temp_cities:
                    job = Process(target=get_regency, args=[cities, province_name, country_name, result_regencies,
                                                            result_villages])
                    jobs.append(job)
                    job.start()
                for job in jobs:
                    job.join()
                while not result_regencies.empty():
                    regencies.append(result_regencies.get())
                while not result_villages.empty():
                    villages.append(result_villages.get())
    print(f"total provinces: {len(provinces)} || total regencies: {len(regencies)} || total villages: {len(villages)}")
    df_collection = [provinces, regencies, villages]
    df_collection_name = ['provinces', 'regencies', 'villages']

    for idx in range(len(df_collection)):
        df = pd.DataFrame(df_collection[idx])
        df.to_csv(f"{df_collection_name[idx]}_in_indonesia.csv")


def get_regency(queries, province, country, queue_regencies: Queue, queue_villages: Queue):
    max_thread = 1
    regencies = []
    for city in queries:
        kabutapen_validation = "Kabupaten"
        kota_validation = "Kota"
        data_collected_name = ['id', 'name', 'state_id', 'country_id', 'latitude', 'longitude']
        data = {}
        if kabutapen_validation in city['name'] or kota_validation in city['name']:
            for data_name in data_collected_name:
                data[data_name] = city[data_name]
            queue_regencies.put(data)
            kabupaten_word_removed = city['name'].replace("Kabupaten", "")
            kota_word_removed = kabupaten_word_removed.replace("Kota", "")
            primary_query = kota_word_removed
            # print(kabupaten_word_removed)
            temp_villages = wiki_search(city['name'], primary_query)
            temp_villages_slice = np.array_split(temp_villages, max_thread)
            jobs = []
            temp_regencies = queue.Queue()
            for villages in temp_villages_slice:
                job = threading.Thread(target=get_coordinate, args=[villages, province, country, data['id'],
                                                                    data['state_id'], data['country_id'],
                                                                    temp_regencies])
                jobs.append(job)
                job.start()
            for job in jobs:
                job.join()

            while not temp_regencies.empty():
                queue_villages.put(temp_regencies.get())

    return regencies


def wiki_search(query: str, primary_query: str):
    prefix_xpath = '//*[@id="mw-content-text"]/div[1]/table[4]'
    x_path_row_3 = f'{prefix_xpath}/tbody/tr/td[3]/a'
    x_path_row_2 = f'{prefix_xpath}/tbody/tr/td[2]/a'
    x_path_row_1 = f'{prefix_xpath}/tbody/tr/td[1]/a'
    prefix_link = "https://id.wikipedia.org/wiki/"
    new_query = f"{prefix_link}{query.replace(' ', '_')}"
    page = requests.get(new_query)
    soup = BeautifulSoup(page.content, 'html.parser')
    page_html = etree.HTML(str(soup))
    dom = page_html.xpath(x_path_row_3) if page_html.xpath(x_path_row_3) else \
        page_html.xpath(x_path_row_2) if page_html.xpath(x_path_row_2) else page_html.xpath(x_path_row_1)
    # print(dom)
    temp_result = []
    for x in dom:
        temp_result.append(x.text)
    print(f"total village for {query} is: {len(temp_result)} ")
    return temp_result


def get_villages_pandas():
    prefix_link = "https://pmb.unsiq.ac.id/kecamatan.php"
    page = requests.get(prefix_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    indiatable = soup.find('table', {'class': "t1"})
    df = pd.read_html(str(indiatable))
    df = pd.DataFrame(df[0])
    return df


def villages_search(query: str, primary_query: str, ):
    prefix_link = "https://pmb.unsiq.ac.id/kecamatan.php"
    new_query = f"{prefix_link}{query.replace(' ', '_')}"
    page = requests.get(new_query)
    soup = BeautifulSoup(page.content, 'html.parser')
    page_html = etree.HTML(str(soup))

    temp_result = []
    # for x in dom:
    #     temp_result.append(x.text)
    print(f"total village for {query} is: {len(temp_result)} ")
    return temp_result


def get_coordinate(queries, province, country, regency_id, state_id, country_id, queue_: Queue):
    if len(queries) > 0:
        for query in queries:
            if query:
                new_query = query.replace(",", " ")
                split_query = new_query.split("  ")
                # app_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
                # geolocator = Nominatim(user_agent=app_name)
                # location = geolocator.geocode(f"{queries} {province} {country}")
                data = {
                    'name': query[0],
                    'regency_id': regency_id,
                    'state_id': state_id,
                    'country_id': country_id,
                    'latitude': '00',
                    'longitude': '-19.20'
                }
                queue_.put(data)


if __name__ == "__main__":
    # main()
    get_villages_pandas()
    # wiki_search("kabupaten badung",'badung')
