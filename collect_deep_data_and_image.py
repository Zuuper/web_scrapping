from scraper import collect_image_of_current_data, \
    setup_surface_scraping_result_with_consistent_name, check_duplicates, \
    setup_input_from_surface_result_with_group, collect_deep_data

if __name__ == '__main__':
    data = setup_input_from_surface_result_with_group()
    setup_surface_scraping_result_with_consistent_name()
    check_duplicates(f'surface_result_with_group/{data}')
    collect_deep_data(data)
    collect_image_of_current_data(f'surface_result_with_group/{data}')
