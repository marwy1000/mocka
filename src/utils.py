import random
from faker import Faker
import importlib
import json
import os

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

DEFAULT_KEYWORD_FAKER_MAP = [
    {
        "keywords": ["email", "e-mail", "mail"],
        "method": "email",
        "args": {},
        "wrap": "str"
    },
    {
        "keywords": ["date", "datum"],
        "method": "date_of_birth",  # Example: could be `date_of_birth` or something else depending on your needs
        "args": {},
        "wrap": "str"
    },
    {
        "keywords": ["name", "title", "namn"],
        "method": "name",
        "args": {},
        "wrap": "str"
    },
    {
        "keywords": ["number", "nummer", "amount"],
        "method": "random_int",
        "args": {"min": 0, "max": 10000},
        "wrap": "str"  # Wrap to string for consistency
    },
    {
        "keywords": ["address", "location", "street"],
        "method": "address",
        "args": {},
        "wrap": "str"
    },
    {
        "keywords": ["company", "firm", "organization"],
        "method": "company",
        "args": {},
        "wrap": "str"
    },
    {
        "keywords": ["ssn", "social security"],
        "method": "ssn",
        "args": {},
        "wrap": "str"
    },
    {
        "keywords": ["birthdate", "dob", "date of birth"],
        "method": "date_of_birth",  # Example: could be any other relevant Faker method
        "args": {},
        "wrap": "str"
    }
]

def load_keyword_faker_map():
    """
    Load the custom keyword-to-faker method mappings from a JSON file.
    If the file is not provided or cannot be found, it will return a default map.
    """
    file_name = '.\\mockr.config'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        # Return the default map if no file or if file doesn't exist
        return DEFAULT_KEYWORD_FAKER_MAP