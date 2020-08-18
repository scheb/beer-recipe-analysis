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
            if not path.exists('../raw_data/mmum/' + str(i) + '.json'):
                page = requests.get("https://www.maischemalzundmehr.de/export.php?id=" + str(i))
                if len(page.text) > 500:
                    with open('../raw_data/mmum/' + str(i) + '.json', 'w') as jsonFile:
                        jsonFile.write(page.text)
                        jsonFile.close()


download_data()
