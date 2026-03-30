"""
Functions for generating data based on a JSON schema
"""

import random
import logging
from datetime import date, datetime, timedelta
import math
import rstr
import isodate

logger = logging.getLogger(__name__)

DEFAULT_MAX_ARRAY_LENGTH = 10


def generate_from_schema(schema, args, root_schema=None, path=None):
    result = {}
    properties = schema.get("properties", {})

    for property_name, property_schema in properties.items():
        if property_name not in schema.get("required", []) and not args.include_optional:
            continue

        result[property_name] = generate_value(
            property_schema,
            args,
            field_name=property_name,
            root_schema=root_schema or schema,
            path=(path or []) + [property_name],
        )

    return result


def generate_value(schema, args, field_name, root_schema, path=None):
    blank_mode = args.blank
    use_key_matching = args.keymatch

    if "$ref" in schema:
        return resolve_ref_value(schema, args, field_name, root_schema)

    if "enum" in schema:
        return handle_enum(schema, blank_mode)

    if "oneOf" in schema:
        return generate_value(random.choice(schema["oneOf"]), args, field_name, root_schema, path)

    if "anyOf" in schema:
        return generate_value(random.choice(schema["anyOf"]), args, field_name, root_schema, path)

    if "allOf" in schema:
        merged_result = {}
        for sub_schema in schema["allOf"]:
            partial = generate_value(sub_schema, args, field_name, root_schema, path)
            if isinstance(partial, dict):
                merged_result.update(partial)
        return merged_result

    schema_type = schema.get("type")
    description = schema.get("description", "")
    title = schema.get("title", "")
    inference_text = f"{description} {title} {field_name}".strip()

    if not schema_type and use_key_matching:
        return generate_value_from_keywords(
            inference_text, field_name, blank_mode, schema_type, use_key_matching, path
        )

    try:
        if schema_type == "string":
            return generate_string(schema, args, field_name)

        if schema_type == "array":
            return generate_array(schema, args, field_name, root_schema)

        if schema_type in ("integer", "number"):
            return generate_number(schema, args)

        if schema_type == "boolean":
            return False if blank_mode else faker.boolean()

        if schema_type == "object":
            return generate_from_schema(schema, args, root_schema, path)

    except ValueError:
        logger.warning(
            'Field "%s" fell back to default generator for type "%s"',
            field_name,
            schema_type,
        )
        return generate_default_value(schema_type)

    return None


def generate_value_from_keywords(
    text, field_name, blank_mode, expected_type, use_key_matching, path=None
):
    keyword_map = config.get("keyword_matching", [])
    field_name = (field_name or "").lower()
    full_text = f"{text} {field_name}".lower()

    def matches_nested_pattern(pattern, path):
        if not isinstance(pattern, dict) or not path:
            return False

        for parent, child in pattern.items():
            parent = parent.lower()

            if isinstance(child, dict):
                for i in range(len(path) - 1):
                    if path[i].lower() == parent and matches_nested_pattern(child, path[i + 1 :]):
                        return True

            elif isinstance(child, str):
                for i in range(len(path) - 1):
                    if path[i].lower() == parent and path[i + 1].lower() == child.lower():
                        return True

        return False

    def matches_entry(entry):
        for keyword in entry.get("keywords", []):
            if isinstance(keyword, str) and keyword.lower() in field_name:
                return True
            if isinstance(keyword, dict) and matches_nested_pattern(keyword, path or []):
                return True
        return False

    for entry in keyword_map:
        if matches_entry(entry):
            return generate_faker_value(entry, blank_mode, expected_type)

    if use_key_matching:
        for entry in keyword_map:
            if any(
                isinstance(k, str) and k.lower() in full_text for k in entry.get("keywords", [])
            ):
                return generate_faker_value(entry, blank_mode, expected_type)

    return "" if blank_mode else generate_default_value(expected_type)


def generate_faker_value(entry, blank_mode, expected_type):
    if blank_mode:
        return ""

    method_name = entry["method"]
    method_args = entry.get("args", {})

    if method_name == "override":
        return method_args.get("value", "")

    try:
        if hasattr(faker, method_name):
            value = getattr(faker, method_name)(**method_args)
        else:
            logger.warning("Unknown faker method '%s', using fallback.", method_name)
            value = faker.word()
    except Exception as err:
        logger.error("Faker error for '%s': %s", method_name, err)
        value = ""

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if expected_type == "string":
        return str(value)

    if expected_type == "integer":
        return int(value) if isinstance(value, (int, float, str)) else 0

    if expected_type == "number":
        return float(value) if isinstance(value, (int, float, str)) else 0.0

    return value


def generate_default_value(expected_type):
    if expected_type == "string":
        return faker.word()
    if expected_type == "integer":
        return faker.random_int(min=0, max=10000)
    if expected_type == "number":
        return faker.pyfloat(left_digits=2, right_digits=2)
    if expected_type == "boolean":
        return faker.boolean()
    return faker.word()


def generate_number(schema, args):
    if args.blank:
        return 0 if schema.get("type") == "integer" else 0.0

    minimum = schema.get("minimum")
    maximum = schema.get("maximum")
    exclusive_min = schema.get("exclusiveMinimum")
    exclusive_max = schema.get("exclusiveMaximum")
    multiple_of = schema.get("multipleOf")

    # Use nextafter to respect exclusive bounds without skipping valid floats
    if exclusive_min is not None:
        min_value = math.nextafter(exclusive_min, float("inf"))
    elif minimum is not None:
        min_value = minimum
    else:
        min_value = 0

    if exclusive_max is not None:
        max_value = math.nextafter(exclusive_max, float("-inf"))
    elif maximum is not None:
        max_value = maximum
    else:
        max_value = min_value + 10000

    if min_value > max_value:
        min_value, max_value = max_value, min_value

    if multiple_of:
        start = math.ceil(min_value / multiple_of)
        end = math.floor(max_value / multiple_of)

        if start > end:
            value = multiple_of * start
        else:
            value = random.randint(start, end) * multiple_of
    else:
        value = random.uniform(min_value, max_value)

    if schema.get("type") == "integer":
        value = int(math.floor(value))

    return value


def generate_string(schema, args, field_name):
    if args.blank:
        return ""

    fmt = schema.get("format")

    if fmt == "date-time":
        return faker.date_time().isoformat()
    if fmt == "date":
        return faker.date()
    if fmt == "time":
        return faker.time()
    if fmt == "duration":
        duration = timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        return isodate.duration_isoformat(duration)
    if fmt == "uri":
        return faker.uri()
    if fmt == "ipv4":
        return faker.ipv4()
    if fmt == "ipv6":
        return faker.ipv6()
    if fmt == "email":
        return faker.email()
    if fmt in ("idn-email", "idn-hostname"):
        return faker.email()
    if fmt == "hostname":
        return faker.hostname()

    pattern = schema.get("pattern")
    if pattern:
        try:
            return rstr.xeger(pattern)
        except Exception as err:
            logger.warning("Pattern generation failed: %s - %s", pattern, err)

    return generate_value_from_keywords(
        f"{schema.get('description', '')} {schema.get('title', '')}",
        field_name,
        args.blank,
        "string",
        args.keymatch,
    )


def resolve_ref(root_schema, ref_path):
    if not ref_path.startswith("#/"):
        raise ValueError("Unsupported $ref format")

    current_schema = root_schema
    for part in ref_path.lstrip("#/").split("/"):
        if not isinstance(current_schema, dict):
            raise ValueError("Invalid $ref path")
        current_schema = current_schema.get(part)
        if current_schema is None:
            raise ValueError("Unresolvable $ref path")

    return current_schema


def resolve_ref_value(schema, args, field_name, root_schema):
    if root_schema is None:
        raise ValueError("Missing root schema for $ref resolution")

    resolved_schema = resolve_ref(root_schema, schema["$ref"])

    if resolved_schema.get("type") == "object":
        return generate_from_schema(resolved_schema, args, root_schema)

    return generate_value(resolved_schema, args, field_name, root_schema)


def handle_enum(schema, blank_mode):
    if not schema["enum"]:
        return get_blank_value(schema.get("type")) if blank_mode else None
    return schema["enum"][0] if blank_mode else random.choice(schema["enum"])


def get_blank_value(schema_type):
    return (
        ""
        if schema_type == "string"
        else 0.0 if schema_type == "number" else 0 if schema_type == "integer" else None
    )


def generate_array(schema, args, field_name, root_schema):
    min_items = schema.get("minItems", 0 if args.blank else 1)
    max_items = schema.get("maxItems", config.get("max_array_length", DEFAULT_MAX_ARRAY_LENGTH))
    max_items = max(max_items, min_items)

    length = 0 if args.blank else random.randint(min_items, max_items)

    items_schema = schema.get("items", {})
    additional_items = schema.get("additionalItems", True)
    unique_items = schema.get("uniqueItems", False)

    results = []

    if isinstance(items_schema, list):
        # Tuple validation: each index has its own schema
        for idx, item_schema in enumerate(items_schema):
            if idx < length:
                results.append(generate_value(item_schema, args, field_name, root_schema))

        if additional_items and length > len(items_schema):
            extra_schema = additional_items if isinstance(additional_items, dict) else {}
            for _ in range(length - len(items_schema)):
                results.append(generate_value(extra_schema, args, field_name, root_schema))
    else:
        for _ in range(length):
            results.append(generate_value(items_schema, args, field_name, root_schema))

    if unique_items:
        seen = set()
        unique_results = []

        for value in results:
            key = repr(value)
            if key not in seen:
                seen.add(key)
                unique_results.append(value)

        # Ensure min_items is satisfied with unique values
        while len(unique_results) < min_items:
            candidate = generate_value(items_schema, args, field_name, root_schema)
            key = repr(candidate)
            if key not in seen:
                seen.add(key)
                unique_results.append(candidate)

        results = unique_results

    return results


def resolve_all_refs(schema, root_schema=None):
    if root_schema is None:
        root_schema = schema

    if isinstance(schema, dict):
        if "$ref" in schema:
            return resolve_all_refs(resolve_ref(root_schema, schema["$ref"]), root_schema)
        return {k: resolve_all_refs(v, root_schema) for k, v in schema.items()}

    if isinstance(schema, list):
        return [resolve_all_refs(item, root_schema) for item in schema]

    return schema


def configure_generator(configuration, faker_instance):
    global config
    global faker
    config = configuration
    faker = faker_instance
