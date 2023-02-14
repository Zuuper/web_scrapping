from scraper import collect_surface_data

if __name__ == '__main__':
    keyword_list = './search_keyword.txt'
    collect_surface_data(keyword_list,'./surface_scraping_result')