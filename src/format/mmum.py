import json
import re
from json import JSONDecodeError
from math import ceil


class IgnoreRecipeError(Exception):
    pass


def is_infusion(data: object) -> bool:
    return data.get('Maischform', '') == 'infusion' or data.get('Infusion_Hauptguss', '') == ''


def parse_source_json_file(file: str) -> object:
    parsed_data = {}
    with open(file) as fileHandle:
        try:
            json_data = json.loads(fileHandle.read())
        except JSONDecodeError:
            raise IgnoreRecipeError("Cannot decode JSON")

        if json_data['Name'] == '':
            raise IgnoreRecipeError("Ignore empty recipe")

        if is_infusion(json_data):
            raise IgnoreRecipeError("Ignore non-infusion recipe")

        parsed_data['name'] = json_data['Name']
        parsed_data['style'] = json_data['Sorte']

        parsed_data['efficiency'] = float(json_data['Sudhausausbeute'])
        parsed_data['original_extract'] = float(json_data['Stammwuerze'])

        alc = json_data.get('Alkohol', '')
        if alc != '' and alc is not None:
            parsed_data['alc'] = float(alc)

        parsed_data['mash_water'] = float(json_data['Infusion_Hauptguss'])
        parsed_data['sparge_water'] = float(json_data['Nachguss'])
        # parsed_data['cast_out_wort'] = float(json_data['Ausschlagswuerze'])
        parsed_data['boiling_time'] = ceil(float(json_data['Kochzeit_Wuerze']))

        parsed_data['malts'] = parse_malts_data(json_data)
        parsed_data['hops'] = parse_hops_data(json_data)

        yeast = json_data.get('Hefe', '')
        if yeast != '':
            parsed_data['yeast'] = yeast

        fileHandle.close()
        return parsed_data


def parse_hops_data(data: object) -> list:
    total_amount = 0
    hops = []
    i: int = 1
    while "Hopfen_%d_Sorte" % i in data:
        kind = data["Hopfen_%d_Sorte" % i].strip().lower()
        alpha = None
        amount = None
        boiling_time = None

        # Clean data
        kind = kind.replace("®", "")
        kind = kind.replace("huell", "hüll")
        kind = re.sub("\\s+", " ", kind)
        kind = kind.strip()

        if "Hopfen_%d_alpha" % i in data:
            alpha = float(data["Hopfen_%d_alpha" % i])
        if "Hopfen_%d_Menge" % i in data:
            amount = float(data["Hopfen_%d_Menge" % i])
            total_amount += amount
        if "Hopfen_%d_Kochzeit" % i in data:
            boiling_time = data["Hopfen_%d_Kochzeit" % i]
            if boiling_time == "Whirlpool":
                boiling_time = 0
            else:
                boiling_time = ceil(float(boiling_time))

        hops.append({
            'kind': kind,
            'alpha': alpha,
            'amount': amount,
            'boiling_time': boiling_time
        })
        i += 1

    if total_amount == 0:
        raise IgnoreRecipeError("Unknown amount of hops used")

    for hop in hops:
        hop['amount_percent'] = hop['amount'] / total_amount * 100

    return hops


def parse_malts_data(data: object) -> list:
    total_amount = 0
    malts = []
    i: int = 1
    while "Malz%d" % i in data:
        kind = data["Malz%d" % i].lower()
        amount = None

        # Clean data
        kind = kind.replace("pilsener", "pilsner")
        kind = kind.replace("münchener", "münchner")
        kind = kind.replace("®", "")
        kind = re.sub("malz\\b", " ", kind)
        kind = re.sub("\\bmalz", " ", kind)
        kind = re.sub("cara\\s*([a-z])", lambda match: 'cara{}'.format(match.group(1).lower()), kind)
        kind = re.sub("\\s+", " ", kind)
        kind = kind.strip()

        if "Malz%d_Menge" % i in data:
            amount = float(data["Malz%d_Menge" % i])
            if "Malz%d_Einheit" % i in data and data["Malz%d_Einheit" % i] == 'kg':
                amount *= 1000
            total_amount += amount

        malts.append({
            'kind': kind,
            'amount': amount,
        })
        i += 1

    if total_amount == 0:
        raise IgnoreRecipeError("Unknown amount of malt used")

    for malt in malts:
        malt['amount_percent'] = malt['amount'] / total_amount * 100

    return malts
