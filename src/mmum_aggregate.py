import glob
import json
from tqdm import tqdm
from format.mmum import parse_source_json_file, IgnoreRecipeError


def get_source_file_list() -> list:
    return glob.glob("../data/raw/mmum/*.json")


def aggregate_data():
    print("Aggregate raw data...")
    aggregated_data = []
    files = get_source_file_list()
    for file in tqdm(files):
        try:
            parsed_data = parse_source_json_file(file)
            aggregated_data.append(parsed_data)
        except (ValueError, KeyError) as err:
            print("Cannot parse file %s because of %s: %s" % (file, type(err), err))
        except IgnoreRecipeError:
            pass

    with open('../data/mmum.json', 'w') as outFile:
        json.dump(aggregated_data, outFile, indent=4)
        outFile.close()


aggregate_data()
