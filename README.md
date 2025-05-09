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
- Copy result to clipboard automatically
- Output to console or file

## Requirements
- Python 3.8 or higher

## Installation

1. Clone the repository or copy the script files.

2. Install required packages
```bash
pip install -r requirements.txt
```
## Usage 
### Call the script without building and executable file
Verify it and try it out. From the cloned directory:
```bash
python .\__main__.py --help
python .\__main__.py .\\path_to_schema.json
```

### Build an exe
From the cloned directory:
```bash
python generate_build.py
```

Then verify it and try it out:
```bash
cd dist
.\mockr.exe --help
.\mockr.exe .\\path_to_schema.json
```

## Config File Example
Just run the script or exe once, pointing to a schema to generate the config file.

### Config File Options:
locale: A list of locales to be used for generating data. If multiple locales are provided, one will be chosen randomly each time the tool runs. You can specify any valid locale supported by the Faker library (e.g., en_US, sv_SE, it_IT, ja_JP).

```bash
  "locale": [
    "sv_SE", 
    "en_US"
  ]
```

seed: A fixed random seed for reproducible results. This ensures that the generated data will be the same each time you run the tool with the same seed value. 0 sets it back to random. Is useful as options input overrides the config file.

```bash
  "seed": 0
```

providers: A list of [Faker](https://pypi.org/project/Faker) providers to include for generating data. In this example, the internet, address, and company providers are included. You can add or remove providers depending on your needs. For more providers, refer to the Faker documentation.

```bash
  "providers": [
    "internet",
    "address",
    "company"
  ]
```

max_array_length: The maximum items in generated arrays. Default is 10.
```bash
  "max_array_length": 10
```

keyword_matching: This is an array that contains objects describing what keys to match to what faker methods and with what arguments. The matching is done from top to bottom. 

The object inside of the array contains a key called keywords. It is an array that can be one or more strings that checks if the keys in the schema contains one of the words, allowing for partial matching, without case sensitivity. 

```bash
  { "keywords": ["age", "years", "maturity", "duration"], "method": "random_int", "args": { "min": 0, "max": 100 }},
```

In addition to the built in faker methods you can also use the method override where you provide which static value you want to override with. 
```bash
  { "keywords": ["age"], "method": "override", "args": { "value": 1 }},
```

It is also possible to make the matching more fine grained by matching the parent keys. This is done by providing a JSON object instead of a string, where the value is the final key that is being looke for. This matching doesn't allow for partial matches, and is also case insensitive.
```bash
  {"keywords": [{"parent": {"child": "age"}}], "method": "override", "args": {"value": 1}},
```

# Development
Be sure to run and fix issues found by these commands before checking in code:
```bash
black .\src .\__main__.py
pylint .\src .\__main__.py  
```