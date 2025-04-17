# mockr - Generate fake JSON data from a schema
# Copyright (c) - Salih Serdenak
# License: MIT
__version__ = "0.0.1"


from src.cli import parse_args
from src.schema_loader import load_schema, load_data_options
from src.generator import generate_from_schema
import json
import pyperclip
from pathlib import Path
import random
from faker import Faker

def main():
    args = parse_args()
    faker = Faker()
    seed = args.seed if args.seed else random.randint(1, 999999)
    random.seed(seed)
    faker.seed_instance(seed)


    if args.debug:
        print(f"[DEBUG] Seed used: {seed}")

    schema = load_schema(args.schema)

    data_options = load_data_options(args.data)

    result = generate_from_schema(
        schema,
        data_options,
        faker,
        include_optional=args.include_optional,
        infer_from_description=args.infer_from_descriptions,
        blank_mode=args.blank,
        root_schema=schema
    )

    output = json.dumps(result, indent=2)

    if args.out:
        Path(args.out).write_text(output)
        print(f"JSON written to {args.out}")
    else:
        print(output)

    pyperclip.copy(output)


if __name__ == "__main__":
    main()
