import pandas as pd

data = pd.read_excel('./excel_of_los_angeles_city.xlsx')
print(data)
# data.to_excel('hotel_scraping_result.xlsx', index=False)