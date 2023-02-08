import pandas as pd

data = pd.read_csv('./master_data_scraping_result/master_hotel.csv')

data.to_excel('hotel_scraping_result.xlsx', index=False)