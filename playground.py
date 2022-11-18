import os

import pandas as pd


def check_scraping_result(scraping_result_filename, surface_scraping_result):
    avail_scraping_df = False
    try:
        scraping_df = pd.read_csv(scraping_result_filename)
        avail_scraping_df = True
        print(' 9 success')
    except:
        scraping_df = None
        print('12 fail')
    if type(surface_scraping_result) == str:
        surface_scraping_df = pd.read_csv(surface_scraping_result)
    elif type(surface_scraping_result) == list:
        surface_scraping_df = pd.DataFrame(surface_scraping_result)
    else:
        surface_scraping_df = surface_scraping_result
        print('20 success')
    if avail_scraping_df:
        completed_title = scraping_df['title'].tolist()
        not_complete_data = surface_scraping_df[~surface_scraping_df['title'].isin(completed_title)]
        return not_complete_data.to_dict('records')
    else:
        return surface_scraping_df.to_dict('records')


def collect_data_from_csv(filedir):
    total_listing = os.listdir(filedir)
    total_data = 0
    for listing in total_listing:
        df = pd.read_csv(f'{filedir}/{listing}')
        total_listing = len(df)
        total_data += total_listing
    print(total_data)


collect_data_from_csv('surface_scraping_result')


# x = 'surface_scraping_result/accommodation in bali_17_11_2022.csv'
# y = 'surface_scraping_result/villa_16_11_2022.csv'
# z = 'result_1.csv'
# new_file = pd.DataFrame(check_scraping_result(y, z))
# new_file.to_csv('result_2.csv', index=False)

# df_1 = pd.read_csv('surface_scraping_result/accommodation in bali_17_11_2022.csv')
# df_2 = pd.read_csv('surface_scraping_result/accommodation ubud_17_11_2022.csv')
# df_3 = pd.read_csv('surface_scraping_result/villa_16_11_2022.csv')
#
# df_4 = df_1.append(df_2, ignore_index=True)
# df_5 = df_4.append(df_3, ignore_index=True)
#
# df_6 = df_5.drop_duplicates(keep='last')
# df_6.to_csv('result_3.csv')

# df_1 = pd.read_csv('result_3.csv')
# df_2 = pd.read_csv('surface_scraping_result/ubud villa_17_11_2022.csv')

# df_new = df_1.append(df_2, ignore_index=True)
# df_new = df_new.drop_duplicates(keep='last')
# df_new.to_csv('result_4.csv')
# print(f"total data for keyword 'ubud villa' => {len(df_2)}")
# print(f"total all data is => {len(df_new)}")


# print(f"we got {len()} duplicated data")

# def check_data(filename):
#     df = pd.read_csv(filename)
#     print(df.dtypes)
#
#
# check_data(y)
