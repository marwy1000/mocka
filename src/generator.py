"""
File should only deal with generating data based on schema
"""

import random

DEFAULT_MAX_ARRAY_LENGTH = 10


def generate_from_schema(
    schema,
    config,
    args,
    faker,
    root_schema=None,
):
    """Generate a full JSON object from the provided schema."""
    result = {}
    properties = schema.get("properties", {})

    for key, prop in properties.items():
        if key not in schema.get("required", []):
            if not args.include_optional:
                continue
        result[key] = generate_value(
            prop,
            args,
            config,
            key_hint=key,
            faker=faker,
            root_schema=root_schema or schema,
        )
    return result


def generate_value(
    prop,
    args,
    config,
    key_hint,
    faker,
    root_schema,
):
    """Generate a value for a given JSON Schema property."""
    # Apply field override if available
    field_overrides = config.get("field_overrides", {})
    blank_mode = args.blank
    infer = args.infer

    if not blank_mode and field_overrides and key_hint in field_overrides:
        return field_overrides[key_hint] if blank_mode else field_overrides[key_hint]

    if "$ref" in prop:
        return resolve_ref_value(prop, args, config, key_hint, faker, root_schema)

    # Handle enums
    if "enum" in prop:
        return handle_enum(prop, blank_mode)

    # Infer type from description if no type is provided
    if not prop.get("type") and infer:
        return generate_faker_value_from_key(
            prop.get("description", ""),
            key_hint or "",
            blank_mode,
            faker,
            config,
        )

    t = prop.get("type")
    fmt = prop.get("format")

    if t == "string":
        if fmt == "uri":
            return "" if blank_mode else faker.uri()
        desc = prop.get("description", "")
        return generate_faker_value_from_key(
            desc, key_hint or "", blank_mode, faker, config
        )

    if t == "integer":
        return 0 if blank_mode else faker.random_int(min=0, max=10000)

    if t == "number":
        return 0.0 if blank_mode else faker.pyfloat(left_digits=2, right_digits=2)

    if t == "boolean":
        return False if blank_mode else faker.boolean()

    if t == "array":
        return generate_array_value(prop, args, config, key_hint, faker, root_schema)

    if t == "object":
        return generate_from_schema(
            prop,
            config,
            args,
            faker,
            root_schema=root_schema,
        )

    return None


def generate_faker_value_from_key(
    description, key_hint, blank_mode, faker, config, infer=False
):
    keyword_faker_map = keyword_faker_map = config.get("keyword_matching", {})

    key_hint = (key_hint or "").lower()
    text = f"{description} {key_hint}".lower()

    # 1. Exact keyword match
    for entry in keyword_faker_map:
        if key_hint in (kw.lower() for kw in entry["keywords"]):
            return generate_faker_value(entry, faker, blank_mode)

    # 2. Partial match in key_hint (e.g. 'enddate' contains 'date')
    for entry in keyword_faker_map:
        if any(kw.lower() in key_hint for kw in entry["keywords"]):
            return generate_faker_value(entry, faker, blank_mode)

    # 3. Optional description+key fuzzy match
    if infer:
        for entry in keyword_faker_map:
            if any(kw.lower() in text for kw in entry["keywords"]):
                return generate_faker_value(entry, faker, blank_mode)

    return "" if blank_mode else faker.word()


def generate_faker_value(entry, faker, blank_mode):
    if blank_mode:
        return ""

    method_name = entry["method"]
    args = entry.get("args", {})
    wrap = entry.get("wrap", None)

    try:
        if hasattr(faker, method_name):
            value = getattr(faker, method_name)(**args)
        else:
            print(f"Unknown method '{method_name}', using fallback.")
            value = faker.word()
    except Exception as e:
        print(f"Error generating value for '{method_name}': {e}")
        value = ""

    return str(value) if wrap == "str" else value


def resolve_ref(root_schema, ref_path):
    """Resolve a $ref like '#/definitions/Thing' into a schema dict."""
    if not ref_path.startswith("#/"):
        raise ValueError(f"Unsupported $ref format: {ref_path}")

    parts = ref_path.lstrip("#/").split("/")
    sub_schema = root_schema
    for part in parts:
        if not isinstance(sub_schema, dict):
            raise ValueError(f"Cannot resolve part '{part}' in $ref path '{ref_path}'")
        sub_schema = sub_schema.get(part)
        if sub_schema is None:
            raise ValueError(f"Could not resolve $ref path: {ref_path}")
    return sub_schema


def resolve_ref_value(prop, args, config, key_hint, faker, root_schema):
    if root_schema is None:
        raise ValueError("Missing root_schema when resolving $ref")
    ref_schema = resolve_ref(root_schema, prop["$ref"])
    if ref_schema.get("type") == "object":
        return generate_from_schema(ref_schema, config, args, faker, root_schema)
    else:
        return generate_value(ref_schema, args, config, key_hint, faker, root_schema)


def handle_enum(prop, blank_mode):
    if not prop["enum"]:
        return get_blank_value(prop.get("type")) if blank_mode else None
    return prop["enum"][0] if blank_mode else random.choice(prop["enum"])


def get_blank_value(t):
    return (
        "" if t == "string" else 0.0 if t == "number" else 0 if t == "integer" else None
    )


def generate_array_value(prop, args, config, key_hint, faker, root_schema):
    items = prop.get("items", {})
    max_array_length = config.get("max_array_length", DEFAULT_MAX_ARRAY_LENGTH)
    array_length = 0 if args.blank else random.randint(1, max_array_length)

    results = []
    if isinstance(items, list):
        for item_schema in items:
            results.append(
                generate_value(item_schema, args, config, key_hint, faker, root_schema)
            )
    else:
        for _ in range(array_length):
            results.append(
                generate_value(items, args, config, key_hint, faker, root_schema)
            )
    return results
