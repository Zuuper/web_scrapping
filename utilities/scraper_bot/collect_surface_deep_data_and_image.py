from utilities.scraper_bot.scraper import collect_surface_and_deep_data, collect_image_of_current_data, \
    scraping_result_with_consistent_name, check_duplicates, \
    setup_input_from_surface_result_with_group, parent_directory, setup_keyword_for_surface_search


def collect_all_data():
    data = setup_keyword_for_surface_search()
    keyword_list = f'{parent_directory}/keywords/{data}'
    data = setup_input_from_surface_result_with_group()
    collect_surface_and_deep_data(keyword_list, f'{parent_directory}/megatron_data/step_1')
    scraping_result_with_consistent_name()
    check_duplicates(f'{parent_directory}/megatron_data/step_1_grouped/{data}')
    collect_image_of_current_data(f'{parent_directory}/megatron_data/step_1_grouped/{data}')
