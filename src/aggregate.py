import glob
import json
from tqdm import tqdm
from os import path


def get_source_file_list() -> list:
    data_path = path.join(path.dirname(path.abspath(__file__)), '../data/processed/*.json')
    return glob.glob(data_path)


def aggregate_data():
    print("Aggregate data...")
    aggregated_data = []
    files = get_source_file_list()
    for file in tqdm(files):
        print(file)
        with open(file) as infile:
            aggregated_data += json.load(infile)

    out_file_path = path.join(path.dirname(path.abspath(__file__)), '../data/recipes.json')
    with open(out_file_path, 'w+') as out_file:
        json.dump(aggregated_data, out_file, indent=4)
        out_file.close()


aggregate_data()
