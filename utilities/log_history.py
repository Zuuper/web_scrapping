import os
import pandas as pd


def collect_image_name():
    file_location = '../backup (do not touch)/image_gallery'
    file_name_list = [dir_ for dir_ in os.listdir(file_location)]
    return file_name_list


def main():
    image_profile_list = collect_image_name()
    with open('history_result/image_gallery_folder_name.txt', 'r+', encoding="utf-8") as f:
        file_list = f.read().splitlines()
        file_list = file_list + image_profile_list if file_list else image_profile_list
        result_image_file = list(dict.fromkeys(file_list))
        f.writelines(s + '\n' for s in result_image_file)


main()
