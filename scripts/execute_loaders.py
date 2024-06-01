import pickle
import glob
import importlib
import io
import json
import os
import sys

LOCALIZATION_LIST = {
    "de": "de",
    "en-us": "en",
    "es": "es",
    "fr": "fr",
    "it": "it",
    "ja": "ja",
    "ko": "ko",
    "ru": "ru",
    "zh": "zh",
}

LOCALIZATION_LOOKUP = [
    "categoryNameID",
    "descriptionID",
    "displayNameID",
    "groupNameID",
    "leaderTypeNameID",
    "nameID",
    "operationNameID",
    "serviceNameID",
    "shortDescriptionID",
    "tooltipDescriptionID",
    "tooltipTitleID",
    "typeNameID",
]

sys.path.append("pyd")
try:
    os.makedirs("json")
except WindowsError:
    pass


def decode_cfsd(key, data, strings):
    data_type = type(data)

    if data_type.__module__ == "cfsd" and data_type.__name__ == "dict":
        return {k: decode_cfsd(k, v, strings) for k, v in data.items()}
    if data_type.__module__.endswith("Loader"):
        return {x: decode_cfsd(x, getattr(data, x), strings) for x in dir(data) if not x.startswith("__")}

    if data_type.__module__ == "cfsd" and data_type.__name__ == "list":
        return [decode_cfsd(None, v, strings) for v in data]
    if isinstance(data, tuple):
        return tuple([decode_cfsd(None, v, strings) for v in data])

    if data_type.__name__.endswith("_vector"):
        # TODO
        return None

    if isinstance(data, int) or data_type.__name__ == "long":
        # In case it is a NameID, look up the name.
        if key is not None and isinstance(key, str) and key in LOCALIZATION_LOOKUP:
            res = {}
            for language in strings:
                if data not in strings[language]:
                    continue
                res[language] = strings[language][data][0]
            return res
        return data
    if isinstance(data, float):
        return data
    if isinstance(data, str):
        return data

    raise ValueError("Unknown type: " + str(type(data)))


# Load all the localizations.
strings = {}
for localization in glob.glob("data/localization_fsd_*.pickle"):
    language = os.path.splitext(os.path.basename(localization))[0].split("_")[-1]
    if language not in LOCALIZATION_LIST:
        continue

    print("Loading '" + LOCALIZATION_LIST[language] + "' ...")
    with open(localization, "rb") as f:
        strings[LOCALIZATION_LIST[language]] = pickle.load(f)[1]

# Convert all available fsdbinary files via their Loader to JSON.
for loader in glob.glob("pyd/*Loader.pyd"):
    loader_name = os.path.splitext(os.path.basename(loader))[0]
    data_name = loader_name.replace("Loader", "").lower() + ".fsdbinary"

    print("Loading '" + data_name + "' with '" + loader_name + "' ...")

    lib = importlib.import_module(loader_name)
    data = lib.load("data/" + data_name)
    data = decode_cfsd(None, data, strings)

    with io.open("json/" + data_name.replace(".fsdbinary", ".json"), "w", encoding="utf-8") as f:
        data = json.dumps(data, f, indent=4, ensure_ascii=False, sort_keys=True)
        # Workaround for Python 2.x, to ensure proper UTF-8 encoding.
        f.write(unicode(data))
