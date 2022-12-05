import os
import pandas as pd


def collect_image_name():
    file_location = 'image_gallery'
    file_name_list = [dir_ for dir_ in os.listdir(file_location)]
    return file_name_list


def main():
    pass


print(collect_image_name())
