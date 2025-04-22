import random
from faker import Faker

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


def generate_value(prop, keyword_faker_map, key_hint=None, faker=None, include_optional=True,
                   infer_from_description=False, root_schema=None, blank_mode=False):
    """Generate a value for a given JSON Schema property."""

    if "$ref" in prop:
        if root_schema is None:
            raise ValueError("Missing root_schema when resolving $ref")
        ref_schema = resolve_ref(root_schema, prop["$ref"])
        if ref_schema.get("type") == "object":
            return generate_from_schema(
                ref_schema, faker, keyword_faker_map, include_optional, infer_from_description,
                blank_mode=blank_mode, root_schema=root_schema
            )
        else:
            return generate_value(
                ref_schema, keyword_faker_map, key_hint, faker,
                include_optional, infer_from_description,
                root_schema, blank_mode
            )

    # Handle enums
    if "enum" in prop:
        if not prop["enum"]:
            t = prop.get("type")
            if blank_mode:
                return "" if t == "string" else 0.0 if t == "number" else 0 if t == "integer" else None
            else:
                return None
        return prop["enum"][0] if blank_mode else random.choice(prop["enum"])

    # Infer type from description if no type is provided
    if not prop.get("type") and infer_from_description:
        return generate_faker_value_from_key(prop.get("description", ""), key_hint or "", blank_mode, faker, keyword_faker_map)

    t = prop.get("type")
    fmt = prop.get("format")

    if t == "string":
        if fmt == "uri":
            return "" if blank_mode else faker.uri()
        desc = prop.get("description", "")
        return generate_faker_value_from_key(desc, key_hint or "", blank_mode, faker, keyword_faker_map)

    elif t == "integer":
        return 0 if blank_mode else faker.random_int(min=0, max=10000)

    elif t == "number":
        return 0.0 if blank_mode else faker.pyfloat(left_digits=2, right_digits=2)

    elif t == "boolean":
        return False if blank_mode else faker.boolean()

    elif t == "array":
        items = prop.get("items", {})
        results = []
        if isinstance(items, list):
            for item_schema in items:
                results.append(generate_value(
                    item_schema, keyword_faker_map, key_hint, faker, include_optional,
                    infer_from_description, root_schema=root_schema, blank_mode=blank_mode
                ))
        else:
            for _ in range(random.randint(1, 3)):
                results.append(generate_value(
                    items, keyword_faker_map, key_hint, faker, include_optional,
                    infer_from_description, root_schema=root_schema, blank_mode=blank_mode
                ))
        return results

    elif t == "object":
        return generate_from_schema(
            prop, faker, keyword_faker_map, include_optional, infer_from_description, root_schema=root_schema
        )

    return None


def generate_faker_value_from_key(description, key_hint, blank_mode, faker, keyword_faker_map):
    text = f"{description} {key_hint}".lower()

    for entry in keyword_faker_map:
        if any(keyword in text for keyword in entry["keywords"]):
            if blank_mode:
                return ""

            method_name = entry["method"]
            args = entry.get("args", {})
            wrap = entry.get("wrap", None)

            if hasattr(faker, method_name):
                value = getattr(faker, method_name)(**args)
            else:
                value = faker.word()

            return str(value) if wrap == "str" else value

    return "" if blank_mode else faker.word()



def generate_from_schema(schema, faker, keyword_faker_map, include_optional=True,
                         infer_from_description=False, blank_mode=False, root_schema=None):

    """Generate a full JSON object from the provided schema."""
    result = {}
    properties = schema.get("properties", {})

    for key, prop in properties.items():
        if key not in schema.get("required", []):
            if not include_optional:
                continue
        result[key] = generate_value(
            prop, keyword_faker_map, key_hint=key, faker=faker,
            include_optional=include_optional,
            infer_from_description=infer_from_description,
            root_schema=root_schema or schema,
            blank_mode=blank_mode
        )
    return result
