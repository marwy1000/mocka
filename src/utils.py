import random
from faker import Faker
import importlib
import json

def infer_type_from_description(description):
    """Infer data type from a description or key."""
    if "email" in description.lower():
        return random.choice(["test@example.com", "user@domain.com"])
    elif "date" in description.lower():
        return random.choice(["2023-04-15", "2024-01-01"])
    elif "address" in description.lower():
        return "123 Main St"
    elif "name" in description.lower():
        return random.choice(["Alice", "Bob", "Charlie"])
    elif "number" in description.lower() or "amount" in description.lower():
        return random.randint(1, 100)
    else:
        return "unknown"  # Default type for unrecognized descriptions



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