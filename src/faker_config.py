"""
Functions for initiating and configuring Faker
"""

import importlib
import random
import logging
from faker import Faker

logger = logging.getLogger(__name__)


def configure_faker(config: dict = None, cli_seed: int = None):
    """Create and configure a Faker instance using config and optional CLI seed."""
    logger.debug("Running function configure_faker")

    config = config or {}

    # Faker does not support multiple locales simultaneously in a single instance.
    # If a list is provided, we pick one randomly to preserve variability.
    locale_config = config.get("locale")

    if isinstance(locale_config, list):
        selected_locale = random.choice(locale_config)
    elif isinstance(locale_config, str):
        selected_locale = locale_config
    else:
        # Fallback option set to US
        selected_locale = "en_US"

    faker_instance = Faker(selected_locale)

    # CLI seed takes precedence to allow reproducible runs from outside config.
    resolved_seed = cli_seed if cli_seed is not None else config.get("seed")

    # Treat 0 as "no seed" and randomize it.
    if resolved_seed in (None, 0):
        resolved_seed = random.randint(1, 999999)

    # Seed both Faker and Python's random to keep all randomness aligned.
    faker_instance.seed_instance(resolved_seed)
    random.seed(resolved_seed)

    # Register additional providers:
    # Only applied when using a single locale, since multi-locale setups
    # can lead to inconsistent provider availability.
    if not isinstance(locale_config, list):
        for provider_name in config.get("providers", []):
            try:
                module_path = f"faker.providers.{provider_name}"
                provider_module = importlib.import_module(module_path)
                faker_instance.add_provider(provider_module.Provider)
            except (ImportError, AttributeError, ModuleNotFoundError):
                logger.warning("Faker provider '%s' not found. Skipping.", provider_name)

    return faker_instance


# fmt: off
app_config = {
  "locale": ["sv_SE"],
  "seed": 0,
  "providers": ["internet", "address", "company"],
  "max_array_length": 10,
  "keyword_matching":
    [
      { "keywords": ["email", "e-mail", "mail"], "method": "email" },
      { "keywords": ["age"], "method": "random_int", "args": { "min": 0, "max": 100 }},
      { "keywords": ["dob", "birthday"],"method": "date_of_birth", "args": { "minimum_age": 18, "maximum_age": 90 } },
      { "keywords": ["date", "datum"], "method": "date" },
      { "keywords": ["currency"], "method": "currency_code" },
      { "keywords": ["languagecode"], "method": "language_code" },
      { "keywords": ["countrydialingcode"], "method": "country_calling_code"},
      { "keywords": ["countrycode", "landskod"], "method": "country_code" },
      { "keywords": ["articlename", "artikelnamn", "productname", "produktnamn", "project"], "method": "bs" },
      { "keywords": [{"project": "name"}, {"application": "name"}], "method": "bs" },
      { "keywords": ["role", "job", {"businessrole": "name"}], "method": "job" },
      { "keywords": ["ssn", "socialsecurity", "personnummer"], "method": "ssn" },
      { "keywords": ["phone", "tel", "mobile"], "method": "phone_number" },
      { "keywords": ["street", "road", "avenue", "gata", "address1", "address2"], "method": "street_name" },
      { "keywords": ["zip", "postcode", "postal", "postnummer"], "method": "postcode" },
      { "keywords": ["city", "town", "stad"], "method": "city" },
      { "keywords": ["address", "location", "adress"], "method": "address" },
      { "keywords": ["country", "countryname", "nation"], "method": "country" },
      { "keywords": ["amount", "count", "antal"], "method": "random_int", "args": { "min": 1, "max": 99 } },
      { "keywords": ["state", "province", "region"], "method": "state" },
      { "keywords": ["url", "uri", "website", "web"], "method": "uri" },
      { "keywords": ["description", "descr", "summary", "text", "comment", "content", "additionalinfo", "info"], "method": "sentence", "args": { "nb_words": 12 } },
      { "keywords": ["number", "nummer"], "method": "random_int", "args": { "min": 0, "max": 10000 } },
      { "keywords": ["company", "nameco", "firm", "organization"], "method": "company" },
      { "keywords": ["username", "user", "login"], "method": "user_name" },
      { "keywords": ["ipv4"], "method": "ipv4" },
      { "keywords": ["ipv6"], "method": "ipv6" },
      { "keywords": ["language", "språk"], "method": "language_name" },
      { "keywords": ["firstname", "förnamn"], "method": "first_name" },
      { "keywords": ["name", "fullname", "title", "namn"], "method": "name" },
      { "keywords": ["color", "colour", "färg"], "method": "color" }
    ]
}
# fmt: on
