# Mocka - Generate test data based on a JSON schema
# Copyright (c) - Salih Serdenak
# License: MIT
"""
This main file initiates the cli, reads files and then calls the function to generate the output
"""
__version__ = "0.0.8"

import sys
import json
import logging
from pathlib import Path
import pyperclip
from src.cli import parse_args
from src.generator import SchemaGenerator
from src.file_loader import load_schema, load_config
from src.faker_config import configure_faker, app_config

logger = logging.getLogger(__name__)


def main():
    try:
        args = parse_args()

        setup_logging(args.debug)

        if args.version:
            print(f"{__version__}")
            return

        config_path = Path(args.config)
        if not config_path.exists():
            if args.config == "app.config":
                logger.info("Generated the config file app.config")
                save_app_config(app_config, "app.config")
            else:
                logger.error("Config file not found: %s", config_path)
                sys.exit(1)

        config = load_config(args.config)
        faker = configure_faker(config, args.seed)
        generator = SchemaGenerator(config, faker)
        schema = load_schema(args.schema)

        # Optionally resolve $ref first
        schema = generator.prepare_schema(schema)

        result = generator.generate(schema, args)

        output = json.dumps(result, ensure_ascii=False, indent=2)

        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
            logger.info("JSON written to %s", args.out)
        else:
            pyperclip.copy(output)
            print(output)

    except Exception as e:
        print(e)


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def save_app_config(json_obj: dict, output_path: str):
    """Saves a json with the custom formatting of lists contents taking one per line"""
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("{\n")
        last_key_name = list(json_obj.keys())[-1]
        for current_key, current_value in json_obj.items():
            file.write(f'  "{current_key}": ')
            if isinstance(current_value, list):
                file.write("[\n")
                for index, list_item in enumerate(current_value):
                    trailing_comma = "," if index < len(current_value) - 1 else ""
                    file.write(f"    {json.dumps(list_item)}{trailing_comma}\n")
                file.write("  ]")
            else:
                file.write(json.dumps(current_value))

            trailing_comma = "," if current_key != last_key_name else ""
            file.write(f"{trailing_comma}\n")

        file.write("}\n")


if __name__ == "__main__":
    main()
