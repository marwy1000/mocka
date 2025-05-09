# Mockr - Generate test data based on a JSON schema
# Copyright (c) - Salih Serdenak
# License: MIT
"""
Mockr is an app that generates a json with testing data based on a JSON schema. 
This main file initiates the cli, reads files and then calls the function to generate the output
"""
__version__ = "0.0.4"

import json
from pathlib import Path
import pyperclip
from src.cli import parse_args
from src.generator import generate_from_schema
from src.file_loader import load_schema, load_config
from src.faker_config import configure_faker, app_config


import json

def save_custom_json(data: dict, filepath: str):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("{\n")
        last_key = list(data.keys())[-1]
        for key, value in data.items():
            f.write(f'  "{key}": ')
            if isinstance(value, list):
                f.write("[\n")
                for i, item in enumerate(value):
                    comma = "," if i < len(value) - 1 else ""
                    f.write(f'    {json.dumps(item)}{comma}\n')
                f.write("  ]")
            else:
                f.write(json.dumps(value))
            comma = "," if key != last_key else ""
            f.write(f"{comma}\n")
        f.write("}\n")

def main():
    try:
        args = parse_args()

        if args.version:
            print(f"{__version__}")
            return

        config_path = Path(args.config)
        if not config_path.exists():
            # Save default app_config to app.config
            # config_path.write_text(json.dumps(app_config, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")

            save_custom_json(app_config, "app.config")
            print('Generated the config file app.config')


        schema = load_schema(args.schema)
        config = load_config(args.config)
        faker = configure_faker(config, args.seed)
        result = generate_from_schema(
            schema,
            config,
            args,
            faker,
            root_schema=schema,
        )

        output = json.dumps(result, ensure_ascii=False, indent=2)

        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
            print(f"JSON written to {args.out}")
        else:
            pyperclip.copy(output)
            print(output)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
