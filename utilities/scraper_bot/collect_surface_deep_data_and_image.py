from utilities.scraper_bot.scraper import collect_surface_and_deep_data, collect_image_of_current_data, \
    setup_surface_scraping_result_with_consistent_name, check_duplicates, \
    setup_input_from_surface_result_with_group,parent_directory


def collect_all_data():
    data = setup_input_from_surface_result_with_group()
    collect_surface_and_deep_data(f'{parent_directory}/keywords/search_keyword.txt', f'{parent_directory}/text_data/step_1')
    setup_surface_scraping_result_with_consistent_name()
    check_duplicates(f'{parent_directory}/text_data/step_1_grouped/{data}')
    collect_image_of_current_data(f'{parent_directory}/text_data/step_1_grouped/{data}')