import glob
import json
from tqdm import tqdm
from format.mmum import parse_source_json_file, IgnoreRecipeError


def get_source_file_list() -> list:
    return glob.glob("../data/processed/*.json")


def aggregate_data():
    print("Aggregate data...")
    aggregated_data = []
    files = get_source_file_list()
    for file in tqdm(files):
        print(file)
        with open(file) as infile:
            aggregated_data += json.load(infile)

    with open('../data/recipes.json', 'w') as outFile:
        json.dump(aggregated_data, outFile, indent=4)
        outFile.close()


aggregate_data()
