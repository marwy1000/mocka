<!-- Keywords: json schema, mockr, data generator, data faker, fake data, mock data, test data, synthetic data, offline, generator -->

# Mockr
This Python CLI tool generates JSON data based on a provided JSON Schema. The input is taken from a scheme file path or your clipboard. Output is copied to your clipboard, the console and can be saved to a file. You can optionally supply a file with predefined values for specific fields if you want to define what type of data it defines. 

## LICENSE and COPYRIGHT
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Copyright (C) 2025 Salih Serdenak

## Features
- Generate data based on a JSON Schema
- Override specific field values with a predefined list
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
python .\__main__.py --config .\\dist\\app.config .\\path_to_schema.json
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
.\mockr.exe --config app.config .\\path_to_schema.json
```

## Config File Example
You can configure the behavior of the app by providing a JSON based configuration file. You can find an example in the path .\dist\app.config where the executable will be created. 

### Configuration Options:
locale: A list of locales to be used for generating data. If multiple locales are provided, one will be chosen randomly each time the tool runs. You can specify any valid locale supported by the Faker library (e.g., en_US, sv_SE, it_IT, ja_JP).

seed: A fixed random seed for reproducible results. This ensures that the generated data will be the same each time you run the tool with the same seed value. 0 sets it back to random. Is useful as options input overrides the config file.

providers: A list of [Faker](https://pypi.org/project/Faker) providers to include for generating data. In this example, the internet, address, and company providers are included. You can add or remove providers depending on your needs. For more providers, refer to the Faker documentation.

max_array_length: The maximum length for arrays that are generated. This controls how many items are included in arrays (e.g., lists of objects). Default is 10.

field_overrides: A dictionary of field names with custom values. This allows you to specify custom values for specific fields in the generated data. In the example the key "keytoreplacewithdata" will have its data replaced with the string "replacement made".
