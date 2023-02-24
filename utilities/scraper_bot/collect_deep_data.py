from utilities.scraper_bot.scraper import setup_surface_scraping_result_with_consistent_name, check_duplicates, \
    setup_input_from_surface_result_with_group, collect_deep_data


def collect_step_two():
    data = setup_input_from_surface_result_with_group()
    setup_surface_scraping_result_with_consistent_name()
    check_duplicates(f'surface_result_with_group/{data}')
    collect_deep_data(data)


if __name__ == '__main__':
    collect_step_two()
