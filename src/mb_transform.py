import glob
import json
from os import path
from tqdm import tqdm
from format.mmum import parse_source_json_file, IgnoreRecipeError


def get_source_file_list() -> list:
    data_path = path.join(path.dirname(path.abspath(__file__)), "../data/raw/mb/*.json")
    return glob.glob(data_path)


def aggregate_data():
    print("Aggregate raw data...")
    aggregated_data = []
    files = get_source_file_list()
    i = 0
    for file in tqdm(files):
        i += 1
        try:
            parsed_data = parse_source_json_file(file)
            parsed_data['uid'] = "mb:" + str(i)
            aggregated_data.append(parsed_data)
        except (ValueError, KeyError, TypeError) as err:
            print("Cannot parse file %s because of %s: %s" % (file, type(err), err))
        except IgnoreRecipeError:
            pass

    out_file_path = path.join(path.dirname(path.abspath(__file__)), '../data/processed/mb.json')
    with open(out_file_path, 'w+') as out_file:
        json.dump(aggregated_data, out_file, indent=4)
        out_file.close()


aggregate_data()
