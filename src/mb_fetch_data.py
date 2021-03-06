import requests
import re
from tqdm import tqdm
from os import path


def download_data():
    print("Download raw data...")
    url = 'https://braureka.de/wp-admin/admin-ajax.php?order[0][column]=0&order[0][dir]=asc&start=0&length=99999&action=wpcm_get_recipe_datatable&public=1'
    page = requests.get(url)
    ids = []
    for match in re.finditer('\\["([0-9]+)"', page.text, re.IGNORECASE):
        ids.append(int(match.group(1)))

    print("Found {} ids".format(len(ids)))
    for i in tqdm(ids):
        json_file_path = path.join(path.dirname(path.abspath(__file__)), '../data/raw/mb/' + str(i) + '.json')
        if not path.exists(json_file_path):
            page = requests.get("https://braureka.de/rezept-export/?format=mmum&id=" + str(i))
            if page.status_code == 200:
                json_search = re.search('export content">(.*)</textarea>', page.text, re.IGNORECASE | re.DOTALL)
                if json_search:
                    with open(json_file_path, 'w+') as json_file:
                        json_file.write(json_search.group(1).strip())
                        json_file.close()


download_data()
