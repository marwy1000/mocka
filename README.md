<!-- Keywords: json schema, mocka, data generator, data faker, fake data, mock data, test data, synthetic data, offline, generator -->

# Mocka

Mocka is a Python CLI tool that generates JSON data based on a JSON Schema. The input is taken as an CLI option or your clipboard. Output is copied to your clipboard, the console and can be saved to a file. Mocka detects what kind of data it should generate and how for each field and can be further extended by you.

## LICENSE and COPYRIGHT

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Copyright (C) 2025 Salih Serdenak

## Requirements

- Python 3.12.9 or higher

## Installation

1. Clone the repository or copy the script files.
2. Install required packages

```powershell
pip install -r requirements.txt
```

## Usage

### Call the script without building and executable file

Verify it and try it out. From the cloned directory:

```powershell
python .\mocka.py dist\generalSchemaExample.json
```

### Build an exe

From the cloned directory:

```powershell
python create_build.py 1
```

If you don't give 1 as an input, you will get an menu with different options, where by the exefile can end up in a different directory.

Then verify it and try it out:

```powershell
cd dist\mocka
.\mocka.exe --version
.\mocka.exe ..\generalSchemaExample.json
```

## Help

```powershell
.\mocka.exe --help
```

```powershell
usage: .\mocka.exe [-h] [--version] [--debug] [--out OUT] [--config CONFIG] [--seed SEED]
                   [--include-optional | --no-optional] [--keymatch] [--blank]
                   [schema]

Generate JSON from schema.

positional arguments:
  schema                Path to schema file (defaults to clipboard)

options:
  -h, --help            show this help message and exit
  --version, -v         Show version and exit
  --debug, -d           Print debug info
  --out OUT, -o OUT     Output file (optional), instead of console and clipboard.
  --config CONFIG, -c CONFIG
                        Mocka config file (will create and use the default if no input given).
  --seed SEED, -s SEED  Random seed (optional), overrides config. 0 is random
  --include-optional, -io
                        Include optional fields (default)
  --no-optional, -no    Don't include optional fields
  --keymatch, -k        Match keywords towards the key only, instead of key, description and title
  --blank, -b           Generate blank values (empty strings, 0s, false, first enum, etc.)
```

## Config File Example

Just run the script or exe once, pointing to a schema to generate the config file. It will be named app.config by default.

### Config File Options:

locale: A list of locales to be used for generating data. If multiple locales are provided, one will be chosen randomly each time the tool runs. You can specify any valid locale supported by the Faker library (e.g., en_US, sv_SE, it_IT, ja_JP).

```json
  "locale": [
    "sv_SE", 
    "en_US"
  ]
```

seed: A fixed random seed for reproducible results. This ensures that the generated data will be the same each time you run the tool with the same seed value. 0 sets it back to random. Is useful as options input overrides the config file.

```json
  "seed": 0
```

providers: A list of [Faker](https://pypi.org/project/Faker) providers to include for generating data. In this example, the internet, address, and company providers are included. You can add or remove providers depending on your needs. For more providers, refer to the Faker documentation.

```json
  "providers": [
    "internet",
    "address",
    "company"
  ]
```

max_array_length: The maximum items in generated arrays. Default is 10. The lowest value takes priority if maxItems is defined.

```json
  "max_array_length": 10
```

keyword_matching: This is an array that contains objects describing what keys to match to what faker methods and with what arguments. The matching is done from top to bottom.

An example of an object can be seen below. It contains keywords that are checked against keys in the schema to see if the key contains the one of the keywords, allowing for partial matching, without case sensitivity.

```json
  { "keywords": ["age", "years", "maturity", "duration"], 
    "method": "random_int",
    "args": { "min": 0, "max": 100 }
  },
```

In addition to the built in faker methods you can also use the method override where you provide which static value you want to override with.

```json
  { "keywords": ["age"], "method": "override", "args": { "value": 1 }},
```

It is also possible to make the matching more fine grained by matching the parent keys. This is done by providing a JSON object instead of a string, where the value is the final key that is being looked for. This matching doesn't allow for partial matches, and is also case insensitive.

```json
  {"keywords": [{"parent": {"child": "age"}}], "method": "override", "args": {"value": 1}},
```

# Release Notes

## Version 0.0.7

* New build options with much improved speed
  * Option 1 - uses onedir, which is superfast, but has an underlying folder and the built file ends up in dist\mocka
* Updated packages and python requirement
* Renamed \_\_main\_\_ file to mocka.py
* Added support for strings with formatting of date-time, date, time, duration, uri, ipv4, ipv6, email, idn-email, hostname, idn-hostname 
* Arrays support for arrays with additionalItems, minItems, maxItems, uniqueItems and extended support for items
* Added support for numbers with minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf
* Split the testschemas to several files

# TODO
* Decide if formatting should have precedence over the app.config
* Add more formatting support
* Add more CLI options to override the app.config

# Development

Be sure to run and fix issues found by these commands before checking in code:

```powershell
black .\src .\mocka.py
pylint .\src .\mocka.py
python release.py <version> "Some comment"  
```
