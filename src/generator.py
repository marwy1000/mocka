"""
File should only deal with generating data based on schema
"""

import random
import logging
from datetime import date, datetime, timedelta
import math
import rstr
import isodate

logger = logging.getLogger(__name__)

DEFAULT_MAX_ARRAY_LENGTH = 10


def generate_from_schema(
    schema,
    args,
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
            key_hint=key,
            root_schema=root_schema or schema,
            key_path=(key_path or []) + [key],
        )
    return result


def generate_value(prop, args, key_hint, root_schema, key_path=None):
    logger.debug("Running function generate_value")
    blank_mode = args.blank
    keymatch = args.keymatch

    if "$ref" in prop:
        return resolve_ref_value(prop, args, key_hint, root_schema)

    if "enum" in prop:
        return handle_enum(prop, blank_mode)

    # Handle oneOf, anyOf, allOf
    if "oneOf" in prop:
        selected = random.choice(prop["oneOf"])
        return generate_value(selected, args, key_hint, root_schema, key_path)

    if "anyOf" in prop:
        selected = random.choice(prop["anyOf"])
        return generate_value(selected, args, key_hint, root_schema, key_path)

    if "allOf" in prop:
        result = {}
        for subschema in prop["allOf"]:
            part = generate_value(subschema, args, key_hint, root_schema, key_path)
            if isinstance(part, dict):
                result.update(part)
        return result

    t = prop.get("type")
    desc = prop.get("description", "")
    title = prop.get("title", "")
    infer_text = f"{desc} {title} {key_hint}".strip()

    if not t and keymatch:
        return generate_faker_value_from_key(
            infer_text, key_hint, blank_mode, t, keymatch, key_path=key_path
        )

    try:
        if t == "string":
            return generate_string_value(prop, args, key_hint)

        if t == "array":
            return generate_array_value(prop, args, key_hint, root_schema)

        if t in ("integer", "number"):
            return generate_number_value(prop, args)

        if t == "boolean":
            return False if blank_mode else faker.boolean()

        if t == "array":
            return generate_array_value(prop, args, key_hint, root_schema)

        if t == "object":
            return generate_from_schema(prop, args, root_schema, key_path)

    except ValueError:
        logger.warning(
            'Key "%s" matched with "none-%s" method. Setting generic %s value',
            key_hint,
            t,
            t,
        )
        return generate_faker_value_default(t)

    return None


def generate_faker_value_from_key(
    description,
    key_hint,
    blank_mode,
    expected_type,
    keymatch,
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
            if isinstance(kw, dict) and match_nested_dict(kw, key_path or []):
                return True
        return False

    for entry in keyword_faker_map:
        if match_entry(entry):
            return generate_faker_value(entry, blank_mode, expected_type)

    if keymatch:
        for entry in keyword_faker_map:
            if any(
                isinstance(kw, str) and kw.lower() in text
                for kw in entry.get("keywords", [])
            ):
                return generate_faker_value(entry, blank_mode, expected_type)

    return "" if blank_mode else generate_faker_value_default(expected_type)


def generate_faker_value(entry, blank_mode, expected_type):
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
            logger.warning("Unknown method '%s', using fallback.", method_name)
            value = faker.word()
    except Exception as e:
        logger.error("Error generating value for '%s': %s", method_name, e)
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


def generate_faker_value_default(expected_type):
    if expected_type == "string":
        return faker.word()
    if expected_type == "integer":
        return faker.random_int(min=0, max=10000)
    if expected_type == "number":
        return faker.pyfloat(left_digits=2, right_digits=2)
    if expected_type == "boolean":
        return faker.boolean()
    return faker.word()


def generate_number_value(prop, args):
    blank_mode = args.blank

    if blank_mode:
        return 0 if prop.get("type") == "integer" else 0.0

    minimum = prop.get("minimum")
    maximum = prop.get("maximum")
    exclusive_min = prop.get("exclusiveMinimum")
    exclusive_max = prop.get("exclusiveMaximum")
    multiple_of = prop.get("multipleOf")

    # Effective min/max calculation with exclusive bounds handled by nextafter
    if exclusive_min is not None:
        min_val = math.nextafter(exclusive_min, float("inf"))
    elif minimum is not None:
        min_val = minimum
    else:
        min_val = 0

    if exclusive_max is not None:
        max_val = math.nextafter(exclusive_max, float("-inf"))
    elif maximum is not None:
        max_val = maximum
    else:
        max_val = min_val + 10000

    # Safety check: if no valid range, swap to avoid issues
    if min_val > max_val:
        min_val, max_val = max_val, min_val

    if multiple_of:
        start = math.ceil(min_val / multiple_of)
        end = math.floor(max_val / multiple_of)
        if start > end:
            # fallback: pick nearest multiple_of to min_val
            val = multiple_of * start
        else:
            val = random.randint(start, end) * multiple_of
    else:
        val = random.uniform(min_val, max_val)

    if prop.get("type") == "integer":
        val = int(math.floor(val))

    return val


def generate_string_value(prop, args, key_hint):
    blank_mode = args.blank
    fmt = prop.get("format")

    if blank_mode:
        return ""

    if fmt == "date-time":
        return faker.date_time().isoformat()
    if fmt == "date":
        return faker.date()
    if fmt == "time":
        return faker.time()
    if fmt == "duration":
        td = timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        return isodate.duration_isoformat(td)
    if fmt == "uri":
        return faker.uri()
    if fmt == "ipv4":
        return faker.ipv4()
    if fmt == "ipv6":
        return faker.ipv6()
    if fmt == "email":
        return faker.email()
    if fmt == "idn-email":
        return faker.email()  # or custom IDN generation
    if fmt == "hostname":
        return faker.hostname()
    if fmt == "idn-hostname":
        return faker.hostname()  # or custom IDN generation

    pattern = prop.get("pattern")
    if pattern and not blank_mode:
        try:
            return rstr.xeger(pattern)
        except Exception as e:
            logger.warning(f"Pattern generation failed: {pattern} - {e}")

    return generate_faker_value_from_key(
        prop.get("description", "") + " " + prop.get("title", ""),
        key_hint,
        blank_mode,
        "string",
        args.keymatch,
    )


def resolve_ref(root_schema, ref_path):
    if not ref_path.startswith("#/"):
        raise ValueError("Unsupported $ref format: %s", ref_path)

    parts = ref_path.lstrip("#/").split("/")
    sub_schema = root_schema
    for part in parts:
        if not isinstance(sub_schema, dict):
            raise ValueError(
                "Cannot resolve part '%s' in $ref path '%s'", part, ref_path
            )
        sub_schema = sub_schema.get(part)
        if sub_schema is None:
            raise ValueError("Could not resolve $ref path: %s", ref_path)
    return sub_schema


def resolve_ref_value(prop, args, key_hint, root_schema):
    if root_schema is None:
        raise ValueError("Missing root_schema when resolving $ref")
    ref_schema = resolve_ref(root_schema, prop["$ref"])
    if ref_schema.get("type") == "object":
        return generate_from_schema(ref_schema, args, root_schema)
    return generate_value(ref_schema, args, key_hint, root_schema)


def handle_enum(prop, blank_mode):
    if not prop["enum"]:
        return get_blank_value(prop.get("type")) if blank_mode else None
    return prop["enum"][0] if blank_mode else random.choice(prop["enum"])


def get_blank_value(t):
    return (
        "" if t == "string" else 0.0 if t == "number" else 0 if t == "integer" else None
    )


def generate_array_value(prop, args, key_hint, root_schema):
    min_items = prop.get("minItems", 0 if args.blank else 1)
    max_items = prop.get(
        "maxItems", config.get("max_array_length", DEFAULT_MAX_ARRAY_LENGTH)
    )
    max_items = max(max_items, min_items)
    array_length = 0 if args.blank else random.randint(min_items, max_items)

    items = prop.get("items", {})
    additional_items = prop.get("additionalItems", True)
    unique_items = prop.get("uniqueItems", False)

    results = []

    if isinstance(items, list):
        # Tuple validation: fixed schemas per index
        for idx, item_schema in enumerate(items):
            if idx < array_length:
                results.append(generate_value(item_schema, args, key_hint, root_schema))
        # Additional items if allowed
        if additional_items and array_length > len(items):
            extra_schema = (
                additional_items if isinstance(additional_items, dict) else {}
            )
            for _ in range(array_length - len(items)):
                results.append(
                    generate_value(extra_schema, args, key_hint, root_schema)
                )
    else:
        # Single schema for all items
        for _ in range(array_length):
            results.append(generate_value(items, args, key_hint, root_schema))

    if unique_items:
        seen = set()
        unique_results = []
        for v in results:
            k = repr(v)
            if k not in seen:
                seen.add(k)
                unique_results.append(v)
        # Fill up to min_items with unique items if needed
        while len(unique_results) < min_items:
            candidate = generate_value(items, args, key_hint, root_schema)
            k = repr(candidate)
            if k not in seen:
                unique_results.append(candidate)
                seen.add(k)
        results = unique_results

    return results


# used when loading the schema
def resolve_all_refs(schema, root_schema=None):
    if root_schema is None:
        root_schema = schema

    if isinstance(schema, dict):
        if "$ref" in schema:
            resolved = resolve_ref(root_schema, schema["$ref"])
            return resolve_all_refs(resolved, root_schema)
        return {k: resolve_all_refs(v, root_schema) for k, v in schema.items()}
    if isinstance(schema, list):
        return [resolve_all_refs(item, root_schema) for item in schema]

    return schema


def configure_generator(c, f):
    global config
    global faker
    config = c
    faker = f
