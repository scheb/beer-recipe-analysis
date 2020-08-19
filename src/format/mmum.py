import json
import re
from json import JSONDecodeError
from math import ceil


class IgnoreRecipeError(Exception):
    pass


def is_infusion(data: object) -> bool:
    return data.get('Maischform', '') == 'infusion' or data.get('Infusion_Hauptguss', '') != ''


def parse_source_json_file(file: str) -> object:
    parsed_data = {}
    with open(file) as fileHandle:
        try:
            json_data = json.loads(fileHandle.read())
        except JSONDecodeError:
            raise IgnoreRecipeError("Cannot decode JSON")

        if json_data['Name'] == '':
            raise IgnoreRecipeError("Ignore empty recipe")

        if not is_infusion(json_data):
            raise IgnoreRecipeError("Ignore non-infusion recipe")

        style = parse_style(json_data)
        parsed_data['style'] = style[0]
        parsed_data['sub_style'] = style[1]
        parsed_data['name'] = json_data['Name']

        parsed_data['efficiency'] = float(json_data['Sudhausausbeute'])
        parsed_data['original_extract'] = float(json_data['Stammwuerze'])

        alc = json_data.get('Alkohol', '')
        if alc != '' and alc is not None:
            parsed_data['alc'] = float(alc)

        parsed_data['mash_water'] = float(json_data['Infusion_Hauptguss'])
        parsed_data['sparge_water'] = float(json_data['Nachguss'])

        cast_out_wort = json_data.get('Ausschlagswuerze', '')
        if cast_out_wort != '' and cast_out_wort is not None:
            parsed_data['cast_out_wort'] = float(cast_out_wort)

        parsed_data['boiling_time'] = ceil(float(json_data['Kochzeit_Wuerze']))

        parsed_data['malts'] = parse_malts_data(json_data)
        parsed_data['hops'] = parse_hops_data(json_data)

        yeast = json_data.get('Hefe', '')
        if yeast != '' and yeast is not None:
            parsed_data['yeast'] = yeast

        fileHandle.close()
        return parsed_data


def parse_style(data: object):
    style = data.get('Sorte', '')
    if style == '' or style is None:
        style = 'unbekannt'

    # Cleanup
    style = style.strip().lower()
    style = re.sub("\\bindia\\s+pale\\s+ale\\b", "ipa", style)
    style = style.replace("pilsener", "pilsner")
    style = style.replace("pilsner", "pils")
    style = style.replace("specialty ipa -", "pils")
    style = style.replace("~ ohne typ ~", "unbekannt")
    style = re.sub("\\s+", " ", style)
    style = style.strip()

    main_style = "unbekannt"

    # Find a main style (if possible)
    if re.search("\\bipa\\b", style):
        main_style = "ipa"
    if re.search("\\bpale\\s+ale\\b", style):
        main_style = "pale ale"
    if re.search("\\bporter\\b", style):
        main_style = "porter"
    if re.search("\\bstout\\b", style):
        main_style = "stout"
    if re.search("\\bpils\\b", style):
        main_style = "pils"
    if re.search("\\bbock", style) or re.search("bock\\b", style):
        main_style = "bock"
    if re.search("\\bblonde\\s+ale\\b", style) or re.search("bock\\b", style):
        main_style = "bock"
    if re.search("\\b(weizenbier|weissbier)\\b", style):
        main_style = "weizenbier"
    if re.search("\\bkellerbier\\b", style):
        main_style = "kellerbier"
    if re.search("\\bred\\s+ale\\b", style):
        main_style = "red ale"
    if re.search("\\bamber\\s+ale\\b", style):
        main_style = "amber ale"
    if re.search("\\bkölsch\\b", style):
        main_style = "kölsch"
    if re.search("\\blager", style):
        main_style = "lager"
    if re.search("\\bexport", style):
        main_style = "export"
    if re.search("\\baltbier\\b", style):
        main_style = "altbier"
    if re.search("\\bbrown\\s+ale\\b", style):
        main_style = "brown ale"
    if re.search("\\bmärzen\\b", style):
        main_style = "märzen"
    if re.search("\\bwitbier\\b", style):
        main_style = "witbier"
    if re.search("\\bsaison\\b", style):
        main_style = "saison"
    if re.search("\\bberliner\\s+weisse\\b", style):
        main_style = "berliner weisse"
    if re.search("\\bmünchner\\s+helles\\b", style):
        main_style = "münchner helles"
    if re.search("\\blambic\\b", style):
        main_style = "belgisches lambic"
    if re.search("\\bblond ale\\b", style):
        main_style = "belgisches blond"
    if re.search("\\bdubbel\\b", style):
        main_style = "belgisches dubbel"
    if re.search("\\btripel\\b", style):
        main_style = "belgisches tripel"

    return main_style, style


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
        kind = kind.replace("hallertauer callista", "callista")
        kind = kind.replace("hallertauer cascade", "cascade")
        kind = kind.replace("hallertauer comet", "comet")
        kind = kind.replace("hallertauer magnum", "magnum")
        kind = re.sub("\\bfuggle\\b", "fuggles", kind)
        kind = re.sub("\\bfrisch\\b", "", kind)
        kind = re.sub("\\b(uk|us|usa|si|nz|slowenien|österreich)\\b", "", kind)
        kind = re.sub("^mt\\W+hood$", "mount hood", kind)
        kind = re.sub("fuggle\\b", "fuggles ", kind)
        kind = re.sub("\\s+", " ", kind)
        kind = kind.strip()

        if re.match("^\\d+\\.\\d+$", kind):
            raise IgnoreRecipeError("Not a valid hop kind, given {}".format(kind))

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
        kind = kind.replace("honey", "honig")
        kind = kind.replace("®", "")
        kind = re.sub("\\b(malz|malt)\\b", "", kind)
        kind = re.sub("cara\\s*([a-z])", lambda match: 'cara{}'.format(match.group(1).lower()), kind)
        kind = re.sub("\\s+", " ", kind)
        kind = kind.strip()

        if re.match("^\\d+\\.\\d+$", kind):
            raise IgnoreRecipeError("Not a valid malt kind, given {}".format(kind))

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
