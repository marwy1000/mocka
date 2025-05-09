"""
Functions for initiating and configuring Faker
"""

import importlib
import random
from faker import Faker


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
    if seed is None or seed == 0:
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

app_config = {
  "locale": ["sv_SE"],
  "seed": 0,
  "providers": ["internet", "address", "company"],
  "max_array_length": 10,
  "field_overrides": [],
  "keyword_matching":
    [
      { "keywords": ["email", "e-mail", "mail"], "method": "email" },
      { "keywords": ["age"], "method": "random_int", "args": { "min": 0, "max": 100 }},
      { "keywords": ["dob", "birthday"],"method": "date_of_birth", "args": { "minimum_age": 18, "maximum_age": 90 } },
      { "keywords": ["date", "datum"], "method": "date" },
      { "keywords": ["currency"], "method": "currency_code" },
      { "keywords": ["languagecode"], "method": "language_code" },
      { "keywords": ["countrycode"], "method": "country_code" },
      { "keywords": ["articlename", "artikelnamn", "productname", "produktnamn", "application name", "project name"], "method": "bs" },
      { "keywords": ["role", "job"], "method": "job" },
      { "keywords": ["ssn", "socialsecurity", "personnummer"], "method": "ssn" },
      { "keywords": ["phone", "tel", "mobile"], "method": "phone_number" },
      { "keywords": ["street", "road", "avenue", "gata", "address1", "address2"], "method": "street_name" },
      { "keywords": ["zip", "postcode", "postal", "postnummer"], "method": "postcode" },
      { "keywords": ["city", "town", "stad"], "method": "city" },
      { "keywords": ["countrycode", "landskod"], "method": "country_code" },
      { "keywords": ["address", "location", "adress"], "method": "address" },
      { "keywords": ["country", "countryname", "nation"], "method": "country" },
      { "keywords": ["amount", "count", "antal"], "method": "random_int", "args": { "min": 1, "max": 99 } },
      { "keywords": ["state", "province", "region"], "method": "state" },
      { "keywords": ["url", "uri", "website", "web"], "method": "uri" },
      { "keywords": ["description", "descr", "summary", "text", "comment", "content", "additionalinfo", "info"], "method": "sentence", "args": { "nb_words": 12 } },
      { "keywords": ["number", "nummer"], "method": "random_int", "args": { "min": 0, "max": 10000 } },
      { "keywords": ["vat", "vatcode", "vatnumber", "moms", "momsnummer"],"method": "company_vat"},
      { "keywords": ["company", "nameco", "firm", "organization"], "method": "company" },
      { "keywords": ["username", "user", "login"], "method": "user_name" },
      { "keywords": ["ipv4", "ipv6"], "method": "ipv4" },
      { "keywords": ["language", "språk"], "method": "language_name" },
      { "keywords": ["firstname", "förnamn"], "method": "first_name" },
      { "keywords": ["name", "fullname", "title", "namn"], "method": "name" },
      { "keywords": ["color", "colour", "färg"], "method": "color" }
    ]
}