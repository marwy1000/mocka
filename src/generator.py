"""
File should only deal with generating data based on schema
"""

import random
from datetime import date, datetime

DEFAULT_MAX_ARRAY_LENGTH = 10


def generate_from_schema(
    schema,
    config,
    args,
    faker,
    root_schema=None,
    key_path=None,
):
    result = {}
    properties = schema.get("properties", {})
    for key, prop in properties.items():
        if key not in schema.get("required", []) and not args.include_optional:
            continue
        result[key] = generate_value(
            prop,
            args,
            config,
            key_hint=key,
            faker=faker,
            root_schema=root_schema or schema,
            key_path=(key_path or []) + [key],
        )
    return result


def generate_value(prop, args, config, key_hint, faker, root_schema, key_path=None):
    blank_mode = args.blank
    infer = args.infer

    # No field_overrides anymore, handled through keyword_matching with "override"

    if "$ref" in prop:
        return resolve_ref_value(prop, args, config, key_hint, faker, root_schema)

    if "enum" in prop:
        return handle_enum(prop, blank_mode)

    t = prop.get("type")
    fmt = prop.get("format")
    desc = prop.get("description", "")
    title = prop.get("title", "")

    infer_text = f"{desc} {title} {key_hint}".strip()

    if not t and infer:
        return generate_faker_value_from_key(
            infer_text, key_hint, blank_mode, faker, config, t, infer, key_path=key_path
        )

    try:
        if t == "string":
            if fmt == "uri":
                return "" if blank_mode else faker.uri()
            return generate_faker_value_from_key(
                infer_text, key_hint, blank_mode, faker, config, t, infer, key_path
            )

        if t == "integer":
            val = generate_faker_value_from_key(
                infer_text, key_hint, blank_mode, faker, config, t, infer, key_path
            )
            return 0 if blank_mode else int(val)

        if t == "number":
            val = generate_faker_value_from_key(
                infer_text, key_hint, blank_mode, faker, config, t, infer, key_path
            )
            return 0.0 if blank_mode else float(val)

        if t == "boolean":
            return False if blank_mode else faker.boolean()

        if t == "array":
            return generate_array_value(
                prop, args, config, key_hint, faker, root_schema
            )

        if t == "object":
            return generate_from_schema(
                prop, config, args, faker, root_schema, key_path
            )

    except ValueError:
        print(
            f'Key "{key_hint}" matched with "none-{t}" method. Setting generic {t} value'
        )
        return generate_faker_value_default(faker, t)

    return None


def generate_faker_value_from_key(
    description,
    key_hint,
    blank_mode,
    faker,
    config,
    expected_type,
    infer,
    key_path=None,
):
    keyword_faker_map = config.get("keyword_matching", [])
    key_hint = (key_hint or "").lower()
    text = f"{description} {key_hint}".lower()

    def match_nested_dict(pattern_dict, path):
        if not isinstance(pattern_dict, dict) or not path:
            return False

        for parent, child in pattern_dict.items():
            parent = parent.lower()
            if isinstance(child, dict):
                for i in range(len(path) - 1):
                    if path[i].lower() == parent and match_nested_dict(
                        child, path[i + 1 :]
                    ):
                        return True
            elif isinstance(child, str):
                for i in range(len(path) - 1):
                    if (
                        path[i].lower() == parent
                        and path[i + 1].lower() == child.lower()
                    ):
                        return True
        return False

    def match_entry(entry):
        for kw in entry.get("keywords", []):
            if isinstance(kw, str) and kw.lower() in key_hint:
                return True
            elif isinstance(kw, dict) and match_nested_dict(kw, key_path or []):
                return True
        return False

    for entry in keyword_faker_map:
        if match_entry(entry):
            return generate_faker_value(entry, faker, blank_mode, expected_type)

    if infer:
        for entry in keyword_faker_map:
            if any(
                isinstance(kw, str) and kw.lower() in text
                for kw in entry.get("keywords", [])
            ):
                return generate_faker_value(entry, faker, blank_mode, expected_type)

    return "" if blank_mode else generate_faker_value_default(faker, expected_type)


def generate_faker_value(entry, faker, blank_mode, expected_type):
    if blank_mode:
        return ""

    method_name = entry["method"]
    args = entry.get("args", {})

    if method_name == "override":
        return args.get("value", "")

    try:
        if hasattr(faker, method_name):
            value = getattr(faker, method_name)(**args)
        else:
            print(f"Unknown method '{method_name}', using fallback.")
            value = faker.word()
    except Exception as e:
        print(f"Error generating value for '{method_name}': {e}")
        value = ""

    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if expected_type == "string":
        return str(value)
    if expected_type == "integer":
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    if expected_type == "number":
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    return value


def generate_faker_value_default(faker, expected_type):
    if expected_type == "string":
        return faker.word()
    if expected_type == "integer":
        return faker.random_int(min=0, max=10000)
    if expected_type == "number":
        return faker.pyfloat(left_digits=2, right_digits=2)
    if expected_type == "boolean":
        return faker.boolean()
    return faker.word()


def resolve_ref(root_schema, ref_path):
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

# used when loading the schema
def resolve_all_refs(schema, root_schema=None):
    if root_schema is None:
        root_schema = schema

    if isinstance(schema, dict):
        if "$ref" in schema:
            resolved = resolve_ref(root_schema, schema["$ref"])
            return resolve_all_refs(resolved, root_schema)
        return {
            k: resolve_all_refs(v, root_schema)
            for k, v in schema.items()
        }
    elif isinstance(schema, list):
        return [resolve_all_refs(item, root_schema) for item in schema]

    return schema