import json
import os
import shutil
import sqlite3
import yaml


def convert_value(value, column, options):
    if type(value) == dict:
        # Allow dicts that are a string in different languages. But all other need column definitions.
        if "en" not in value.keys():
            raise Exception("Define nested objects with 'columns'")

        # Sometimes localization is empty (or resolved to an invalid key); delete those keys.
        new_value = {}
        for language, v in list(value.items()):
            if v != "" and not v.startswith("EVE/Evetypes/Types/Descriptions"):
                new_value[language] = v
        # If the key is now empty, delete it.
        if not new_value:
            return None
        # Some files have empty language entries if the rest is present. Others
        # do not mention empty languages.
        if column.get("ignore-empty"):
            value = new_value

    if "type" in column:
        if column["type"] == "bool":
            value = bool(value)

    # This is an estimation, which fixes most rounding issues. Not all.
    # This can simply be explained that the original source is human-written,
    # and the source for this scripting is a Python float.
    if type(value) == float and column.get("round", True):
        value = round(value, ndigits=column.get("precision", 6))

    if "condition" in column:
        if column["condition"] == "if-true":
            if value is False:
                return None
        elif column["condition"] == "if-not-zero":
            if value == 0:
                return None
        elif column["condition"] == "if-not-zero-or-one":
            if value == 0 or value == 1:
                return None

    return value


def convert_object(json_value, columns, options):
    yaml_value = {}
    for yaml_name, column in columns.items():
        if column is None:
            column = {}

        json_fields = column.get("json", yaml_name).split(".")
        value = json_value
        for json_field in json_fields:
            if value is None:
                break
            value = value.get(json_field)
        if value is None:
            if column.get("condition") == "if-set":
                return None
            continue

        if column.get("type") == "number-dict":
            if "columns" in column:
                value = {int(k): convert_object(v, column["columns"], options) for k, v in value.items()}
            else:
                value = {int(k): convert_value(v, column, options) for k, v in value.items()}
        elif type(value) == list:
            yaml_v = []
            for v in value:
                if "columns" in column:
                    yaml_v.append(convert_object(v, column["columns"], options))
                else:
                    yaml_v.append(convert_value(v, column, options))
            value = yaml_v
        elif "columns" in column:
            value = convert_object(value, column["columns"], options)
        else:
            value = convert_value(value, column, options)

        if value is None:
            continue

        yaml_value[yaml_name] = value

    return yaml_value


def main():
    os.makedirs("yaml", exist_ok=True)
    shutil.copy("data/build-number.txt", "yaml/build-number.txt")

    with open("mapping.yaml") as f:
        mapping = yaml.safe_load(f)

    for yaml_filename, yaml_config in mapping.items():
        print(f"Creating {yaml_filename}.yaml ...")

        if yaml_config.get("sqlite"):
            con = sqlite3.connect(f"data/{yaml_config['sqlite']}")
            cur = con.cursor()
            res = cur.execute(f"SELECT * FROM cache")

            json_data = {}
            for row in res:
                json_data[row[0]] = json.loads(row[1])
        else:
            with open(f"json/{yaml_config['json']}", encoding="utf-8") as f:
                json_data = json.load(f)

        options = yaml_config.get("options", {})

        yaml_data = {}
        for json_key, json_value in json_data.items():
            yaml_value = convert_object(json_value, yaml_config["columns"], options)
            if yaml_value is None:
                continue

            if options.get("key-type", "int") == "int":
                json_key = int(json_key)

            yaml_data[json_key] = yaml_value

        with open(f"yaml/{yaml_filename}.yaml", "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, allow_unicode=True, indent=2, sort_keys=True, width=80, Dumper=yaml.CSafeDumper)


main()
