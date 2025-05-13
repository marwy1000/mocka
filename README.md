<!-- Keywords: json schema, mockr, data generator, data faker, fake data, mock data, test data, synthetic data, offline, generator -->

# Mockr

This Python CLI tool generates JSON data based on a provided JSON Schema. The input is taken from a scheme file path or your clipboard. Output is copied to your clipboard, the console and can be saved to a file. You can optionally supply a file with predefined values for specific fields if you want to define what type of data it defines.

## LICENSE and COPYRIGHT

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Copyright (C) 2025 Salih Serdenak

## Features

- Generate data based on a JSON Schema
- Define how data is generated
- Override specific values with a fixed value
- Take input from the clipboard or a file
- Output to console, clipboard or file

## Requirements

- Python 3.8 or higher

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
python .\__main__.py --help
python .\__main__.py .\\path_to_schema.json
```

### Build an exe

From the cloned directory:

```powershell
python generate_build.py
```

Then verify it and try it out:

```powershell
cd dist
.\mockr.exe --version
.\mockr.exe .\\path_to_schema.json
```

## Help

```powershell
.\mockr.exe --help
```

```powershell
usage: .\mockr.exe [-h] [--version] [--debug] [--out OUT] [--config CONFIG] [--seed SEED]
                   [--include-optional | --no-optional] [--infer] [--blank]
                   [schema]

Generate fake JSON from schema.

positional arguments:
  schema                Path to schema file (defaults to clipboard)

options:
  -h, --help            show this help message and exit
  --version, -v         Show version and exit
  --debug, -d           Print debug info
  --out OUT, -o OUT     Output file (optional), instead of console and clipboard.
  --config CONFIG, -c CONFIG
                        Mockr config file (will create and use the default if no input given).
  --seed SEED, -s SEED  Random seed (optional), overrides config. 0 is random
  --include-optional, -io
                        Include optional fields (default)
  --no-optional, -no    Don't include optional fields
  --infer, -i           Infer type from description and title if provided
  --blank, -b           Generate blank values (empty strings, 0s, false, first enum, etc.)
```

## Config File Example

Just run the script or exe once, pointing to a schema to generate the config file.

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

max_array_length: The maximum items in generated arrays. Default is 10.

```json
  "max_array_length": 10
```

keyword_matching: This is an array that contains objects describing what keys to match to what faker methods and with what arguments. The matching is done from top to bottom.

The object inside of the array contains a key called keywords. It is an array that can be one or more strings that checks if the keys in the schema contains one of the words, allowing for partial matching, without case sensitivity.

```json
  { "keywords": ["age", "years", "maturity", "duration"], "method": "random_int", "args": { "min": 0, "max": 100 }},
```

In addition to the built in faker methods you can also use the method override where you provide which static value you want to override with.

```json
  { "keywords": ["age"], "method": "override", "args": { "value": 1 }},
```

It is also possible to make the matching more fine grained by matching the parent keys. This is done by providing a JSON object instead of a string, where the value is the final key that is being looke for. This matching doesn't allow for partial matches, and is also case insensitive.

```json
  {"keywords": [{"parent": {"child": "age"}}], "method": "override", "args": {"value": 1}},
```

# Development

Be sure to run and fix issues found by these commands before checking in code:

```powershell
black .\src .\__main__.py
pylint .\src .\__main__.py  
```

## TODO

* ntegrate a JSON Schema Resolver: Use a library like jsonschema to handle $ref resolution comprehensively, including external references.
* Improve error handling: By catch user errors in the config file and by verifing the schema clear error messages can be given to the user.
* Implement Additional Schema Keywords: Extend the code to support oneOf, anyOf, allOf, and not, enabling the handling of more complex schemas.
* Support Array Constraints: Modify the array generation logic to respect minItems and maxItems constraints specified in the schema.
* Enhance Configuration Options: Allow users to define patterns, and other constraints directly in the configuration file to customize data generation further.
* Code Comments and Documentation: Enhance inline comments and provide comprehensive documentation to assist future contributors and users in understanding the codebase.
