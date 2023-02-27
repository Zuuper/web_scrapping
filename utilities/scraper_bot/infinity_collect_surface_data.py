from utilities.scraper_bot.scraper import collect_surface_data, setup_keyword_for_surface_search, parent_directory

if __name__ == '__main__':
    data = setup_keyword_for_surface_search()
    keyword_list = f'{parent_directory}/keywords/{data}'
    print(keyword_list)
    collect_surface_data(keyword_list, f'{parent_directory}/megatron_data/step_1')