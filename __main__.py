# Mockr - Generate test data based on a JSON schema
# Copyright (c) - Salih Serdenak
# License: MIT
__version__ = "0.0.2"

import json
from pathlib import Path
import pyperclip
from src.cli import parse_args
from src.schema_loader import load_schema
from src.generator import (
    generate_from_schema,
    set_max_array_length,
    DEFAULT_MAX_ARRAY_LENGTH,
)
from src.utils import configure_faker, DEFAULT_KEYWORD_FAKER_MAP


def main():
    args = parse_args()
    config = {}
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)

    field_overrides = config.get("field_overrides", {})
    max_array_length = config.get("max_array_length", DEFAULT_MAX_ARRAY_LENGTH)
    set_max_array_length(max_array_length)
    faker = configure_faker(config, args.seed)

    schema = load_schema(args.schema)

    keyword_faker_map = config.get("keyword_matching", DEFAULT_KEYWORD_FAKER_MAP)

    result = generate_from_schema(
        schema,
        faker,
        keyword_faker_map,
        field_overrides,
        include_optional=args.include_optional,
        infer_from_description=args.infer_from_descriptions,
        blank_mode=args.blank,
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
