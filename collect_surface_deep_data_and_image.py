
from scraper import collect_surface_and_deep_data, collect_image_of_current_data, \
    setup_surface_scraping_result_with_consistent_name, check_duplicates, \
    setup_input_from_surface_result_with_group

if __name__ == '__main__':
    data = setup_input_from_surface_result_with_group()
    collect_surface_and_deep_data('search_keyword.txt', 'surface_scraping_result')
    setup_surface_scraping_result_with_consistent_name()
    check_duplicates(data)
    collect_image_of_current_data(f'surface_result_with_group/{data}')
