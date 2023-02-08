from scraper import setup_surface_scraping_result_with_consistent_name, check_duplicates, \
    setup_input_from_surface_result_with_group, collect_deep_data

if __name__ == '__main__':
    data = setup_input_from_surface_result_with_group()
    setup_surface_scraping_result_with_consistent_name()
    check_duplicates(data)
    collect_deep_data(data)

