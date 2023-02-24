import time
import numpy as np
import pandas as pd
from multiprocessing import Queue, cpu_count, Process
from utilities.scraper_utility.google_maps_utility import MapsDataCollection
import requests
from selenium.webdriver.chrome.options import Options
from multiprocesspandas import applyparallel

pd.options.mode.chained_assignment = None  # default='warn'


def main():
    start = time.time()
    df_provinces = pd.read_csv('../backup (do not touch)/data/provinces.csv', names=['id_provinces', 'name_province'], header=None)
    df_regencies = pd.read_csv('../backup (do not touch)/data/regencies.csv', names=['id_regencies', 'id_provinces', 'name_regency'],
                               header=None)
    df_districts = pd.read_csv('../backup (do not touch)/data/districts.csv', names=['id_districts', 'id_regencies', 'name_district'],
                               header=None)
    df_villages = pd.read_csv('../backup (do not touch)/data/villages.csv', names=['id_villages', 'id_districts', 'name_village'], header=None)
    refine_df = pd.merge(df_villages, df_districts, on='id_districts')
    more_refine_df = pd.merge(refine_df, df_regencies, on="id_regencies")
    df = pd.merge(more_refine_df, df_provinces, on="id_provinces")
    df = df[['id_villages', 'id_districts', 'id_regencies', 'id_provinces', 'name_village',
             'name_district', 'name_regency', 'name_province']]
    # new_df = df.head(5)
    # df['latitude & longitude'] = df.apply_parallel(get_coordinate,num_processes=8)
    # new_df['latitude & longitude'] = new_df.apply_parallel(get_coordinate,num_processes=8)
    df.to_csv("villages_in_indonesia_with_longitude_latitude.csv", index=False)
    df.to_excel("villages_in_indonesia_with_longitude_latitude.xlsx")
    # new_df.to_csv("villages_in_indonesia_with_longitude_latitude.csv")
    end = time.time()
    print(f"finish get all coordinate :D")
    print(f"total time used: {(start - end) / 3600}")


def get_coordinate(df):
    query = f"{df['name_village']}+{df['name_district']}+{df['name_regency']}+{df['name_province']}"
    options = Options()
    options.headless = True
    options.add_argument("--kiosk")
    options.add_argument("--lang=en-US")
    options.add_argument("--window-size=1336,768")
    engine = MapsDataCollection("../config/map_search.json", options)
    lat, lon = '-8.6429085', '115.1525135'
    position = {'lat': '-8.6429085', 'lon': '115.1525135'}
    engine.search_on_map(query, position)
    same_url = True
    time_count = 0
    max_time_count = 6
    while same_url:
        url = engine.driver.current_url

        url_split = url.split("/")
        saved_url = ""
        for url in url_split:
            if url.startswith("@"):
                url = url.replace("@", "")
                url_split = url.split(",")
                saved_url = f"{url_split[0]}, {url_split[1]}"
                if lat == url_split[0] and lon == url_split[1] and time_count < max_time_count:
                    time_count += 1
                    time.sleep(1)
                else:
                    print(f"{df['name_village']}: {saved_url}")
                    return saved_url
    return saved_url


if __name__ == "__main__":
    main()
