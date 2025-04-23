"""
Functions for initiating and configuring Faker
"""

import importlib
import random
from faker import Faker


DEFAULT_KEYWORD_FAKER_MAP = [
    {
        "keywords": ["email", "e-mail", "mail"],
        "method": "email",
        "args": {},
        "wrap": "str",
    },
    {
        "keywords": ["date", "datum"],
        "method": "date_of_birth",
        "args": {},
        "wrap": "str",
    },
    {"keywords": ["name", "namn"], "method": "name", "args": {}, "wrap": "str"},
    {
        "keywords": ["number", "nummer", "amount"],
        "method": "random_int",
        "args": {"min": 0, "max": 10000},
        "wrap": "str",
    },
    {
        "keywords": ["address", "location", "street", "adress"],
        "method": "address",
        "args": {},
        "wrap": "str",
    },
    {
        "keywords": ["company", "firm", "organization"],
        "method": "company",
        "args": {},
        "wrap": "str",
    },
    {
        "keywords": ["ssn", "social security"],
        "method": "ssn",
        "args": {},
        "wrap": "str",
    },
    {
        "keywords": ["birthdate", "dob", "date of birth"],
        "method": "date_of_birth",
        "args": {},
        "wrap": "str",
    },
]


def get_keyword_faker_map(config):
    keyword_faker_map = config.get("keyword_matching", DEFAULT_KEYWORD_FAKER_MAP)
    return keyword_faker_map


def configure_faker(config: dict = None, args_seed=None):
    """Configure and return a Faker instance based on the given config."""
    config = config or {}

    # Handle locale
    locale = config.get("locale")
    if isinstance(locale, list):
        # If locale is a list, randomly choose one from the list
        locale = random.choice(locale)
    elif isinstance(locale, str):
        # If locale is a string, use it directly
        pass
    else:
        # Default locale if none is provided
        locale = "en_US"

    # Create the Faker instance using the chosen locale
    faker = Faker(locale)

    # Seed from CLI arg or config
    seed = args_seed if args_seed is not None else config.get("seed")
    if seed is None:
        seed = random.randint(1, 999999)
    faker.seed_instance(seed)
    random.seed(seed)

    # Add providers (only if NOT in multi-locale mode)
    if not isinstance(locale, list):
        for provider in config.get("providers", []):
            try:
                module_path = f"faker.providers.{provider}"
                module = importlib.import_module(module_path)
                faker.add_provider(module.Provider)
            except (ImportError, AttributeError, ModuleNotFoundError):
                print(f"Warning: Faker provider '{provider}' not found. Skipping.")

    return faker
