import glob
import json
import re


class IgnoreRecipeError(Exception):
    pass


def get_source_file_list() -> list:
    return glob.glob("../raw_data/mmum/*.json")


def parse_source_json_file(file: str) -> object:
    parsed_data = {}
    with open(file) as fileHandle:
        json_data = json.loads(fileHandle.read())
        if json_data['Maischform'] != 'infusion':
            raise IgnoreRecipeError("Ignore non-infusion recipe")

        parsed_data['name'] = json_data['Name']
        parsed_data['style'] = json_data['Sorte']

        parsed_data['efficiency'] = float(json_data['Sudhausausbeute'])
        parsed_data['original_extract'] = float(json_data['Stammwuerze'])
        parsed_data['alc'] = float(json_data['Alkohol'])

        parsed_data['mash_water'] = float(json_data['Infusion_Hauptguss'])
        parsed_data['sparge_water'] = float(json_data['Nachguss'])
        parsed_data['cast_out_wort'] = float(json_data['Ausschlagswuerze'])
        parsed_data['boiling_time'] = int(json_data['Kochzeit_Wuerze'])

        parsed_data['malts'] = parse_malts_data(json_data)
        parsed_data['hops'] = parse_hops_data(json_data)
        parsed_data['yeast'] = json_data['Hefe']

        fileHandle.close()
        return parsed_data


def parse_hops_data(data: object) -> list:
    hops = []
    i: int = 1
    while "Hopfen_%d_Sorte" % i in data:
        kind = data["Hopfen_%d_Sorte" % i].strip().lower()
        alpha = None
        amount = None
        boiling_time = None

        if "Hopfen_%d_alpha" % i in data:
            alpha = float(data["Hopfen_%d_alpha" % i])
        if "Hopfen_%d_Menge" % i in data:
            amount = float(data["Hopfen_%d_Menge" % i])
        if "Hopfen_%d_Kochzeit" % i in data:
            boiling_time = data["Hopfen_%d_Kochzeit" % i]
            if boiling_time == "Whirlpool":
                boiling_time = 0
            else:
                boiling_time = int(boiling_time)

        hops.append({
            'kind': kind,
            'alpha': alpha,
            'amount': amount,
            'boiling_time': boiling_time
        })
        i += 1

    return hops


def parse_malts_data(data: object) -> list:
    total_malt_amount = 0
    malts = []
    i: int = 1
    while "Malz%d" % i in data:
        kind = data["Malz%d" % i].lower()
        amount = None

        # Clean data
        kind = kind.replace("pilsener", "pilsner")
        kind = kind.replace("münchener", "münchner")
        kind = kind.replace("®", "")
        kind = re.sub("\\bmalz\\b", " ", kind)
        kind = re.sub("malz\\b", " ", kind)
        kind = re.sub("\\bmalz", " ", kind)
        kind = re.sub("cara\\s*([a-z])", lambda match: 'cara{}'.format(match.group(1).lower()), kind)
        kind = re.sub("\\s+", " ", kind)
        kind = kind.strip()

        if "Malz%d_Menge" % i in data:
            amount = float(data["Malz%d_Menge" % i])
            if "Malz%d_Einheit" % i in data and data["Malz%d_Einheit" % i] == 'kg':
                amount *= 1000
            total_malt_amount += amount

        malts.append({
            'kind': kind,
            'amount': amount,
        })
        i += 1

    for malt in malts:
        malt['amount_percent'] = malt['amount'] / total_malt_amount * 100

    return malts


def aggregate_data():
    aggregated_data = []
    files = get_source_file_list()
    for file in files:
        try:
            parsed_data = parse_source_json_file(file)
            aggregated_data.append(parsed_data)
        except (ValueError, KeyError) as err:
            print("Cannot parse file %s because of error: %s" % (file, err))
        except IgnoreRecipeError:
            pass

    with open('../data/mmum.json', 'w') as outFile:
        json.dump(aggregated_data, outFile, indent=4)
        outFile.close()


aggregate_data()
