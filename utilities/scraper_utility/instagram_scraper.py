import json
import threading
import time

from instagrapi import Client
from instagrapi.utils import json_value

from utilities import config as cfg
from utilities import utils
import os
import sys
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)


def rank_data_based_on_performance(medias, is_best_performance=True):
    data = []
    for media in medias:
        curr_media = {'media': media, 'like': media['like_count']}
        data.append(curr_media)
    return sorted(data, key=lambda i: i['like'], reverse=True if is_best_performance else False)


class InstagramUtility:
    def __init__(self, user_id, password):
        self.settings = None
        self.client = Client()
        print(user_id,password)
        self.client.login(username=user_id, password=password)
        # self.client.handle_exception = self.handle_exception
        self.photo_id, self.video_id, self.igtv_id, self.reel_id, self.album_id = 1, 2, 2, 2, 8
        self.video_type, self.igtv_type, self.reel_type = 'feed', 'igtv', 'clips'
        self.username = ''
        self.abs_path = sys.path[1]

    def get_user_id(self, username):
        try:
            self.username = self.client.user_id_from_username(username)
            return self.username
        except Exception as e:
            raise Exception(e)

    def get_media_from_user_id(self, user_id, total_media):
        maximum_medias = 10
        try:
            return self.client.user_medias(user_id=user_id,
                                           amount=total_media if total_media <= maximum_medias else maximum_medias)
        except Exception as e:
            raise Exception(e)

    def download_data(self, media, file_location):
        media_id = media['media_type']
        product_type = media['product_type']
        id_data = media['pk']
        try:
            self.client.account_info()
        except LoginRequired:
            print('re login is required...')
            self.client.relogin()
            time.sleep(60)
        if media_id == self.photo_id:
            # return self.client.photo_download(id_data, f"{file_location}/photos")
            return self.client.photo_download(id_data, f"{file_location}/")

        elif media_id == self.video_id and product_type == self.video_type:
            # return self.client.video_download(id_data, f"{file_location}/videos")
            return self.client.video_download(id_data, f"{file_location}/")
        elif media_id == self.reel_id and product_type == self.reel_type:
            # return self.client.clip_download(id_data, f"{file_location}/reels")
            return self.client.clip_download(id_data, f"{file_location}/")
        elif media_id == self.igtv_id and product_type == self.igtv_type:
            # return self.client.igtv_download(id_data, f"{file_location}/igtv")
            return self.client.igtv_download(id_data, f"{file_location}/")
        elif media_id == self.album_id:
            # utils.generate_folder(file_location=f"{file_location}/albums/", file_name=id_data, is_parent_folder=False)
            utils.generate_folder(file_location=f"{file_location}/", file_name=id_data, is_parent_folder=False)
            return self.client.album_download(id_data, f"{file_location}/{id_data}")
        else:
            raise Exception('')

    def split_data_based_on_media(self, medias):
        data = {
            'feed': [],
            'video': [],
            'reels': [],
            'igtv': [],
            'albums': [],
        }

        for media in medias:
            media = media.dict()
            media_id = media['media_type']
            product_type = media['product_type']


            if media_id == self.photo_id:
                data['feed'].append(media)
            elif media_id == self.video_id and product_type == self.video_type:
                data['video'].append(media)
            elif media_id == self.reel_id and product_type == self.reel_type:
                data['reels'].append(media)
            elif media_id == self.igtv_id and product_type == self.igtv_type:
                data['igtv'].append(media)
            elif media_id == self.album_id:
                data['albums'].append(media)
        return data

    def setup_file_location(self, username):
        # print(self.abs_path)
        file_location = os.path.join(self.abs_path, f"instagram_scraper_result/{username}")
        # print(file_location)
        utils.generate_folder(file_location)
        return file_location

    def collecting_data(self, instagram_config: dict, file_location: str, medias: list):
        medias_collection = self.split_data_based_on_media(medias)
        for config, config_value in instagram_config.items():
            medias = medias_collection[config]
            medias = rank_data_based_on_performance(medias)
            medias = medias[:config_value]
            for media in medias:
                # media = media.dict()
                print(media)
                # print(json.dumps(media, indent=2, default=str))
                self.download_data(media['media'], file_location)

    def handle_exception(self, e):
        if isinstance(e, BadPassword):
            self.logger.exception(e)
            self.set_proxy(self.next_proxy().href)
            if self.relogin_attempt > 0:
                self.freeze(str(e), days=7)
                raise ReloginAttemptExceeded(e)
            self.settings = self.rebuild_client_settings()
            return self.update_client_settings(self.get_settings())
        elif isinstance(e, LoginRequired):
            self.logger.exception(e)
            self.relogin()
            return self.update_client_settings(self.get_settings())
        elif isinstance(e, ChallengeRequired):
            api_path = json_value(self.last_json, "challenge", "api_path")
            if api_path == "/challenge/":
                self.set_proxy(self.next_proxy().href)
                self.settings = self.rebuild_client_settings()
            else:
                try:
                    self.challenge_resolve(self.last_json)
                except ChallengeRequired as e:
                    self.freeze('Manual Challenge Required', days=2)
                    raise e
                except (ChallengeRequired, SelectContactPointRecoveryForm, RecaptchaChallengeForm) as e:
                    self.freeze(str(e), days=4)
                    raise e
                self.update_client_settings(self.get_settings())
            return True
        elif isinstance(e, FeedbackRequired):
            message = self.last_json["feedback_message"]
            if "This action was blocked. Please try again later" in message:
                self.freeze(message, hours=12)
                # self.settings = self.rebuild_client_settings()
                # return self.update_client_settings(self.get_settings())
            elif "We restrict certain activity to protect our community" in message:
                # 6 hours is not enough
                self.freeze(message, hours=12)
            elif "Your account has been temporarily blocked" in message:
                """
                Based on previous use of this feature, your account has been temporarily
                blocked from taking this action.
                This block will expire on 2020-03-27.
                """
                self.freeze(message)
        elif isinstance(e, PleaseWaitFewMinutes):
            self.freeze(str(e), hours=1)
        raise e


def init_instagram_data_collection(user_search, instagram_config={}, amount_media=5, is_using_all_media=False,
                                   total_pagination=0, total_media_pagination=5):
    username, password = cfg.instagram['username'], cfg.instagram['password']
    print(f'instagram account => username: {username} || password: {password}')
    ig = InstagramUtility(username, password)
    client = ig.client
    for user_list in user_search:
        user = user_list[1]
        location = user_list[0]
        user_id = client.user_id_from_username(user)
        user_detail = client.user_info_by_username(user).dict()
        print(f'self ID : {user_id}')
        file_location = ig.setup_file_location(location)
        amount_media = user_detail['media_count'] if is_using_all_media else amount_media

        if total_pagination != 0:
            end_cursor = None
            medias_list = []
            for page in range(total_pagination if total_pagination <= 10 else 10):
                medias, end_cursor = client.user_medias_paginated(user_id, total_media_pagination,
                                                                  end_cursor=end_cursor)
                medias_list.append(medias)
            jobs = []

            for medias in medias_list:
                job = threading.Thread(target=ig.collecting_data, args=[instagram_config, file_location, medias])
                jobs.append(job)
                job.start()
            for job in jobs:
                job.join()

        else:
            maximum_medias = 100
            medias = client.user_medias(user_id, amount_media if amount_media < maximum_medias else maximum_medias)
            print(f'total medias : \n {len(medias)}')
            ig.collecting_data(instagram_config=instagram_config, file_location=file_location, medias=medias)


if __name__ == "__main__":
    # username, password = cfg.instagram['username'], cfg.instagram['password']
    # ig = InstagramUtility(username, password)
    # self = ig.self
    # user_id = self.user_id_from_username('tfrnews')
    # print(print(json.dumps(self.user_info_by_username('tfrnews').dict(), indent=2, default=str)))
    start_time = time.time()
    print(f'time start is {start_time}')
    # init_instagram_data_collection(['maimelali'],
    #                                {'feed': 50, 'video': 50, 'reels': 50, 'igtv': 50, 'albums': 50},
    #                                is_using_all_media=True, total_pagination=5, total_media_pagination=10)
    init_instagram_data_collection(['maimelali'],
                                   {'feed': 50, 'video': 50, 'reels': 50, 'igtv': 50, 'albums': 50},
                                   is_using_all_media=False, amount_media=50)
    end_time = time.time()
    print(f'total time spend to collect {5*10} data is: {round(end_time - start_time)}')
# ig.download_video('https://www.instagram.com/p/CGgDsi7JQdS/')
