# An up-to-date EVE SDE

This repository automates the process of creating an SDE from the EVE client data-files.

## Rational (or: why not use CCP's SDE?)

There are more than a few reasons why the official SDE is far from practical in the day-to-day use.

First, the biggest issue: CCP mentioned on the EVE Discord that their intent is to release a new SDE "every month".
In the current reality, this is more like four times a year.
In result, a lot of tooling, like [EVEShip.fit](https://eveship.fit), can't handle new items or ships that has been released since the last released SDE.
This results into user-complaints to third-party developers, which increases the burden on those developers.

Second, it is really hard to know what has changed between SDEs.
Which means the best way to approach the SDE, is to reimport all data into your own application; even if that would be totally wasteful.

Lastly, there are a few weird things with the SDE.
There are some inaccuracies with floats, fields that are sometimes there and sometimes not, etc.
All small stuff, but it adds up over time.

In result, more than a few 3rd-party developers work around this problem, either by augmenting the SDE with information from ESI (which on its own is incomplete and hard to use) or by using techniques similar to this repository (read: using the EVE Client data-files).

This repository is yet-another-fix to the same problem:
- This repository has fully automated the job of creating an SDE (from the EVE client data-files); so it is always up-to-date.
- A simple [mapping file](./mapping.yaml) instructs how the conversion should be done, so it is easy to maintain for anyone.
- It corrects a few of the weirdness the current SDE has, like floating precision, etc.
- It publishes the "latest SDE", but also a delta since the last. This is not a "diff", but a list of entries that changed, with their latest content.
  When using a database as backend, it is sufficient to process this delta to make your database up-to-date with the latest SDE.

## Additional data

The official SDE is missing some information crucial for correctly doing things like accurate ship statistics in all situations.
For example, the "warfare IDs" are nowhere to be found in the SDE.
This SDE does add those files.
Currently they are:

- `dbuffCollections.yaml`: contains all the Warfare IDs.

## Missing data

Not all information that is in the official SDE is actually included in the EVE client data-files.
So creating an SDE this way does miss a few files / fields:

- `characterAttributes.yaml`: is not available as a data-file.
- `tournamentRuleSets.yaml`: is not available as a data-file.
- `translationLanguages.yaml`: is not available as a data-file.
- `certificates.yaml`: is available, but uses a custom format.
  Possibly it could be added, but currently isn't.
- `iconIDs.yaml`: the `description` field is missing.
- `graphicIDs.yaml`: the `description` field is missing.
- `typeIDs.yaml`: the `sofFactionName`, `sofMaterialSetID`, `traits`, and `masteries` fields are missing.
- `bsd`: I never used it, so I didn't look into this.
  Possibly it could be added, but currently isn't.
- `universe` / `landmarks`: I never used it, so I didn't look into this.
  Possibly it could be added, but currently isn't.

If anyone actually misses those files / fields, do create an issue.
For the first four files, it would be trivial to just copy them from the latest official SDE, as they are unlikely to change often.
The last two simply needs someone looking into it.
The others are more complicated, and more likely needs a bit of assistance from CCP to find their source.

## Usage

This repository uses both Python3 (either on Linux or Windows) and Python2 (has to be Windows).
Additionally, you need two dependencies installed for Python3: `pyyaml` and `requests`.
The Python2 script does not have any dependencies.

### Step 1 - Downloading

```bash
python3 scripts/download_loders.py [<build-number>]
```

This will download the latest data (`data` folder) and loaders (`pyd` folder).
If no `build-number` is given, the latest will be used.

(this script is also Python2 compatible)

### Step 2 - Extraction

```bash
python2.exe scripts/execute_loaders.py
```

This will use the Loaders the EVE client uses to extract the binary blobs.
It is important this is run on Windows, and with Python2.
As the loaders are `pyd` files, which are DLLs.

### Step 3 - Conversion

```bash
python3 scripts/convert_to_yaml.py
```

This converts all the data into an SDE, and stores them in the `yaml` folder.

### Step 4 - Create deltas

```bash
python3 scripts/create_delta.py <sde-compare-folder>
```

This creates the deltas for all YAML files, and stores them in the `delta` folder.
The `sde-compare-folder` is the older SDE to compare against.

### Step ??? - Profit

You now have an up-to-date SDE.
Enjoy.

## Releases

Every hour this repository automatically checks if there is a new EVE client release.
If there is, it will automatically publish a new release based on the build-number.
It will contain:
- The full SDE.
- The delta against the last SDE.
- The delta against the last official SDE (slightly modified to fix some inconsistencies in content / whitespace / ordering).

If you apply all the deltas between your SDE version and the latest, in (numeric) order, you will have the exact same information as when you would download the latest SDE in full.

### I see tags without a release; is something broken?

No.

For every new EVE build released by CCP, this repository checks if it has any impact on the SDE.
If it does, a new tag+release is created, and a new SDE is attached to the release.
If it does not, only a new tag is created, without a new release (as nothing changed).

The new tag is needed for administrative purposes; this way scripting knows that the build number is checked, and doesn't need checking again.
