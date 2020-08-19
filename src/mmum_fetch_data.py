import requests
import re
from tqdm import tqdm
from os import path


def download_data():
    print("Download raw data...")
    url = 'https://www.maischemalzundmehr.de'
    page = requests.get(url)
    id_search = re.search('index\\.php\\?id=([0-9]+)', page.text, re.IGNORECASE)
    if id_search:
        max_id = int(id_search.group(1))
        print("Max id is " + str(max_id))
        for i in tqdm(range(1, max_id + 1)):
            json_file_path = path.join(path.dirname(path.abspath(__file__)), '../data/raw/mmum/' + str(i) + '.json')
            if not path.exists(json_file_path):
                page = requests.get("https://www.maischemalzundmehr.de/export.php?id=" + str(i))
                if page.status_code == 200:
                    with open(json_file_path, 'w+') as json_file:
                        json_file.write(page.text)
                        json_file.close()


download_data()
