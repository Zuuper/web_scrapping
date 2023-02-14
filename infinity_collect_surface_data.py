from scraper import collect_surface_data, setup_keyword_for_surface_search

if __name__ == '__main__':
    data = setup_keyword_for_surface_search()
    keyword_list = f'./{data}'
    collect_surface_data(keyword_list, './surface_scraping_result')