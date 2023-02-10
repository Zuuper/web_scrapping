import base64
import datetime
import os
import requests
import pandas as pd

url = 'http://127.0.0.1:8000/api/secret/bot/scrapping/post'
user_agent = 'JAMAL_Bot v4.0'
encoded_user_agent = base64.b64encode(user_agent.encode()).decode()
headers = {'User-Agent': encoded_user_agent, }


# mendapatkan date
# menyiapkan folder
# mengambil semua data dari file daily berdasarkan date
# menyiapkan request
# mempush request

def get_data_from_folder(folder, date) -> [pd.DataFrame(), str]:
    list_file = os.listdir(folder)
    for file_ in list_file:
        if file_.find(date) != -1:
            df = pd.read_csv(f"{folder}/{file_}")
            name = file_.replace(f"{date}.csv", "").replace("_", " ").lstrip().rstrip()
            return df, name
    return pd.DataFrame(), ''


def write_file(filename, data):
    if os.path.isfile(filename):
        with open(filename, 'a') as f:
            f.write('\n' + data)
    else:
        with open(filename, 'w') as f:
            f.write(data)


def print_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    data = "Current Time = " + current_time
    return data


def main():
    date = datetime.datetime.now().date()
    image_data, _ = get_data_from_folder('data_scraping_images_daily', str(date))
    text_data, filename = get_data_from_folder('data_scraping_daily', str(date))
    total_image_data = image_data.shape[0]
    total_text_data = text_data.shape[0]
    data = {'name': filename, 'type': 'scraping', 'total_text': total_text_data, 'total_file': total_image_data}
    response = requests.post(url=url, data=data, headers=headers)
    write_file('scraping_report.txt', f"{response.status_code} {print_time()}")


if __name__ == "__main__":
    main()
