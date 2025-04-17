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
## Run 
To get started and get help, in cloned directory:
```bash
python .\__main__.py -h
```

## Config
You can create a file where the keys can be used to match against your data values. The file is provided as the option --data and should be a file that contain a json like: 
```json
{
  "firstName": ["Alice", "Bob", "Charlie"],
  "age": [25, 30, 35],
  "email": ["test@example.com", "hello@world.com"],
  "Descr": ["My description", "Another one of my descriptions"]
}
```

## Build an exe
From the cloned directory:
```bash
pyinstaller --onefile --name mockr ./__main__.py
cd dist
mockr.exe -h
```

## TODO
Add a config file, which can be used to configure keys and descriptions to decide how they are generated.
Improved debug
