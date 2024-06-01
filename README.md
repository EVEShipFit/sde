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
For example, most files are created with "indent=2", but some with "indent=4".
And of course, the latter is done on one of the bigger files, making the whole SDE 10% bigger on disk than it has to.
That for some useless whitespace.
But also, some files do not export the Korean translation, where others do.
There are also some inaccuracies with floats, fields that are sometimes there and sometimes not, etc.
All small stuff, but it adds up over time.

In result, more than a few 3rd-party developers work around this problem, either by augmenting the SDE with information from ESI (which on its own is incomplete and hard to use) or by using techniques similar to this repository (read: using the EVE Client data-files).

This repository tries to correct that, by making a suggestion to CCP how to deal with the SDE, in a way that is easier to process for 3rd-party tooling.
In short:
- This repository fully automated the job of creating an SDE (from the EVE client data-files); so it is always up-to-date.
- A simple [mapping file](./mapping.yaml) instructs how the conversion should be done, so it is easy to maintain for anyone.
- It corrects a few of the weirdness the current SDE has, like indent, floating precision, Korean translation, etc.
- It publishes the "latest SDE", but also a delta since the last. This is not a "diff", but a list of entries that changed, with their latest content.
  When using a database as backend, it is sufficient to process this delta to make your database up-to-date with the latest SDE.

### Going forward

I really hope that CCP adjusts an approach similar to this repository for releasing their SDE.
Being up-to-date with current state is really important for tools like [EVEShip.fit](https://eveship.fit) (and many others, I imagine).
And being able to quickly see the delta is invaluable to know when a new release of your tool is required, or to more easily update your database.

Additionally, something maybe worth considering:

Split up the SDE into three blobs:
- `bsd` - although interesting for some tools, not so interesting for others.
  And this updates is less like to change a lot over time.
- `fsd/universe` - similar to `bsd`, and possibly it could be merged together.
  Especially the amount of files makes the current SDE a bit annoying to work with.
- `fsd` - the information provided by this repository.

By splitting up the SDE like this, we make the `fsd` part much smaller (~15MB), and much more manageable.
It is also for that reason, this repository only does this `fsd` part, and not the rest.

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
If this is the official SDE, make sure to clean it up first (see below).

### Step ??? - Profit

You now have an up-to-date SDE.
Enjoy.

### Cleanup official SDE

There are a few things with the official SDE, that makes it hard to compare this SDE and the official:
- Keys are sorted, most of the time. Except once.
- Indent can be either 4 or 2.
To make comparing easier, one can run:

```bash
for i in $(ls sde/fsd/*.yaml); do python3 scripts/cleanup_yaml.py ${i}; done
```

This will convert the official SDE to a form that is easier to compare against.

## Releases

Every hour, and between 11:05 and 11:30 every 5 minutes, this repository automatically checks if there is a new EVE client release.
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
