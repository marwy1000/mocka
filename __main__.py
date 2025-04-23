# Mockr - Generate test data based on a JSON schema
# Copyright (c) - Salih Serdenak
# License: MIT
__version__ = "0.0.2"

import json
from pathlib import Path
import pyperclip
from src.cli import parse_args
from src.generator import generate_from_schema
from src.file_loader import load_schema, load_config
from src.faker_config import configure_faker


def main():
    args = parse_args()
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

    output = json.dumps(result, indent=2)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"JSON written to {args.out}")
    else:
        print(output)

    pyperclip.copy(output)


if __name__ == "__main__":
    main()
