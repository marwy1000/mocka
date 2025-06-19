# Mocka - Generate test data based on a JSON schema
# Copyright (c) - Salih Serdenak
# License: MIT
"""
This main file initiates the cli, reads files and then calls the function to generate the output
"""
__version__ = "0.0.7"

import sys
import json
import logging
from pathlib import Path
import pyperclip
from src.cli import parse_args
from src.generator import generate_from_schema, configure_generator
from src.file_loader import load_schema, load_config
from src.faker_config import configure_faker, app_config

logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )


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
                    f.write(f"    {json.dumps(item)}{comma}\n")
                f.write("  ]")
            else:
                f.write(json.dumps(value))
            comma = "," if key != last_key else ""
            f.write(f"{comma}\n")
        f.write("}\n")


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
                save_custom_json(app_config, "app.config")
            else:
                logger.error("Config file not found: %s", config_path)
                sys.exit(1)

        schema = load_schema(args.schema)
        config = load_config(args.config)
        faker = configure_faker(config, args.seed)
        configure_generator(config, faker)
        result = generate_from_schema(
            schema,
            args,
            root_schema=schema,
        )

        output = json.dumps(result, ensure_ascii=False, indent=2)

        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
            logger.info("JSON written to %s", args.out)
        else:
            pyperclip.copy(output)
            print(output)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
