from utilities.scraper_bot.collect_surface_deep_data_and_image import collect_all_data
from utilities.scraper_bot.scraper import scraper, setup_keyword_for_surface_search, parent_directory

if __name__ == "__main__":
    data = setup_keyword_for_surface_search()
    keyword_list = f'{parent_directory}/keywords/{data}'
    scraper(keyword_list)
