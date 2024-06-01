import os
import requests
import sys

# Only download the loaders that are published by the SDE.
LOADER_LIST = [
    "agentsInSpace",
    "ancestries",
    "bloodlines",
    "categories",
    "contrabandTypes",
    "controlTowerResources",
    "corporationActivities",
    "dogmaAttributeCategories",
    "dogmaAttributes",
    "dogmaEffects",
    "factions",
    "graphicIDs",
    "groups",
    "iconIDs",
    "marketGroups",
    "metaGroups",
    "npcCharacters",
    "npcCorporationDivisions",
    "npcCorporations",
    "races",
    "schematics",
    "stationOperations",
    "stationServices",
    "typeDogma",
    "typeMaterials",
    "types",
]
STATIC_LIST = [
    "blueprints",
    "skinLicenses",
    "skinMaterials",
    "skins",
]

try:
    os.makedirs("pyd")
except:
    # Ignore if folder already exists.
    pass
try:
    os.makedirs("data")
except:
    # Ignore if folder already exists.
    pass

session = requests.Session()

if len(sys.argv) == 1:
    # Find the latest installer listing.
    latest = session.get("https://binaries.eveonline.com/eveclient_TQ.json").json()
    build = latest["build"]
else:
    build = sys.argv[1]

print("Downloading files for build " + build + " ...")

with open("data/build-number.txt", "w") as f:
    f.write("tranquility-" + build)

installer = session.get("https://binaries.eveonline.com/eveonline_" + build + ".txt").text

# Download all the loaders.
resfileindex = None
for line in installer.split("\n"):
    if not line:
        continue

    res, path, _, _, _, _ = line.split(",")
    if res == "app:/resfileindex.txt":
        resfileindex = line.split(",")[1]

    if not res.startswith("app:/bin64") or not res.endswith("Loader.pyd"):
        continue
    loader = res.split("/")[-1][:-10]
    if loader not in LOADER_LIST:
        continue

    local_path = "pyd/" + res.split("/")[-1]

    print("Downloading " + local_path + " ...")

    with open(local_path, "wb") as f:
        f.write(session.get("https://binaries.eveonline.com/" + path).content)

if resfileindex is None:
    raise Exception("resfileindex not found")

# Download all the fsdbinary files.
resfile = requests.get("https://binaries.eveonline.com/" + resfileindex).text
for line in resfile.split("\n"):
    if not line:
        continue

    res, path, _, _, _ = line.split(",")
    if (
        not res.startswith("res:/staticdata/") or (not res.endswith(".fsdbinary") and not res.endswith(".static"))
    ) and not res.startswith("res:/localizationfsd/localization_fsd_"):
        continue
    loader = res.split("/")[-1][:-10]
    for loader_list_entry in LOADER_LIST:
        if loader == loader_list_entry.lower():
            break
    else:
        static = res.split("/")[-1][:-7]
        for static_list_entry in STATIC_LIST:
            if static == static_list_entry.lower():
                break
        else:
            if not res.startswith("res:/localizationfsd/localization_fsd_"):
                continue

    local_path = "data/" + res.split("/")[-1]

    print("Downloading " + local_path + " ...")

    with open(local_path, "wb") as f:
        f.write(session.get("https://resources.eveonline.com/" + path).content)
