import pandas as pd
import os

from utilities.scraper_bot.scraper import check_scraping_result, scraping_result_with_consistent_name
from utilities.scraper_bot.collect_surface_deep_data_and_image import collect_all_data
from utilities.scraper_bot.scraper import scraper, setup_keyword_for_surface_search, parent_directory



def get_all_data():
    file_dirs = os.listdir('backup (do not touch)/All PC Data')
    for filedir in file_dirs:
        filedata_dirs = os.listdir(f'backup (do not touch)/All PC Data/{filedir}')
        try:
            activity_df = pd.read_csv('backup (do not touch)/All PC Data master/activity.csv')
        except:
            activity_df = pd.DataFrame()
        try:
            hotel_df = pd.read_csv('backup (do not touch)/All PC Data master/hotel.csv')
        except:
            hotel_df = pd.DataFrame()
        try:
            restaurant_df = pd.read_csv('backup (do not touch)/All PC Data master/restaurant.csv')
        except:
            restaurant_df = pd.DataFrame()
        try:
            villa_df = pd.read_csv('backup (do not touch)/All PC Data master/villa.csv')
        except:
            villa_df = pd.DataFrame()

        for filedata in filedata_dirs:
            df = pd.read_csv(f'backup (do not touch)/All PC Data/{filedir}/{filedata}')
            if 'activity' in filedata:
                activity_df = pd.concat([activity_df, df], ignore_index=True)
                # setup_master_file('activity', df)
            if 'hotel' in filedata:
                hotel_df = pd.concat([hotel_df, df], ignore_index=True)
                # setup_master_file('hotel', df)
            if 'restaurant' in filedata:
                restaurant_df = pd.concat([restaurant_df, df], ignore_index=True)
                # setup_master_file('restaurant', df)
            if 'villa' in filedata:
                villa_df = pd.concat([villa_df, df], ignore_index=True)
                # setup_master_file('villa', df)

        list_data = [activity_df, hotel_df, restaurant_df, villa_df]
        for data in range(len(list_data)):
            idx = data - 1
            filename = filedata_dirs[idx]
            print(filename)
            list_data[idx].to_csv(f'./All PC Data Master/{filename}', index=False)
            try:
                missing_data = setup_master_file(filename.replace('.csv',''), list_data[idx])
                new_df = pd.DataFrame.from_dict(missing_data)
                try:
                    old_df = pd.read_csv(f'./All PC Data Master Not Complete/{filename}.csv')
                except:
                    old_df = pd.DataFrame()
                new_df = pd.concat([old_df,new_df], ignore_index=True)
                new_df.to_csv(f'./All PC Data Master Not Complete/{filename}')


            except:

                continue
            print('---' * 20)
        print('---' * 20)


def setup_master_file(file_name, data_frame):
    master_file = 'backup (do not touch)/All PC Data master'
    master_df = ''
    if 'activity' in file_name:
        master_df = './master_data_scraping_result/master_activity.csv'
    if 'hotel' in file_name:
        master_df = './master_data_scraping_result/master_hotel.csv'
    if 'restaurant' in file_name:
        master_df = './master_data_scraping_result/master_restaurant.csv'
    if 'villa' in file_name:
        master_df = './master_data_scraping_result/master_villa.csv'

    data_frame['title'] = data_frame['title'].str.replace(r'[^\w\s]+', '', regex=True)

    not_complete_list = check_scraping_result(master_df, data_frame)
    print(f"total missing in {file_name} is: {len(not_complete_list)}")
    return not_complete_list


def create_new_saved_file():
    pass


if __name__ == '__main__':
    scraping_result_with_consistent_name('step_2')
