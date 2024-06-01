import sys
import yaml

filename = sys.argv[1]

with open(filename) as f:
    data = yaml.load(f, Loader=yaml.CSafeLoader)

with open(filename, "w") as f:
    yaml.dump(data, f, allow_unicode=True, indent=2, sort_keys=True, width=80, Dumper=yaml.CSafeDumper)
