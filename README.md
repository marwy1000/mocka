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

2. (Optional) Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```
3. Install required packages
```bash
pip install -r requirements.txt
```
## Usage 
### Call the script without building and executable file
To get started and get help, in cloned directory:
```bash
python .\__main__.py -h
```

### Build an exe
From the cloned directory:
```bash
pyinstaller --onefile --name mockr ./__main__.py
cd dist
mockr.exe -h
```

## Config File Example
You can configure the behavior of the app by providing a JSON configuration file. Below is an example of a config.txt file:

```json
{
    "locale": ["sv_SE", "it_IT", "en_US"],
    "seed": 2,
    "providers": ["internet", "address", "company"],
    "custom_words": ["foo", "bar", "baz"],
    "max_array_length": 3,
    "field_overrides": {
        "email": "foo@example.com",
        "Name": "Test Name"
    }
}
```

### Configuration Options:
locale: A list of locales to be used for generating data. If multiple locales are provided, one will be chosen randomly each time the tool runs. You can specify any valid locale supported by the Faker library (e.g., en_US, sv_SE, it_IT, ja_JP).

seed: A fixed random seed for reproducible results. This ensures that the generated data will be the same each time you run the tool with the same seed value.

providers: A list of [Faker](https://pypi.org/project/Faker) providers to include for generating data. In this example, the internet, address, and company providers are included. You can add or remove providers depending on your needs. For more providers, refer to the Faker documentation.

custom_words: A list of custom words that can be used in place of default Faker-generated words. You can extend or modify this list to suit your needs.

max_array_length: The maximum length for arrays that are generated. This controls how many items are included in arrays (e.g., lists of objects).

field_overrides: A dictionary of field names with custom values. This allows you to specify custom values for specific fields in the generated data. For example, the email field will always be set to "foo@example.com" and the Name field will always be "Test Name".

### Usage
```bash
mockr myschema.json --config config.txt
```

## TODO
- Improved debug to cover the whole file, maybe add proper logging.
- Improve built performance. The executable is slow while the script is fast.
- Improve and define clearer how seeding should work. Repeat keys should have different values, but if the same seed is used the values should repeat.
