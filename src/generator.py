import random
from faker import Faker
from .utils import infer_type_from_description

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


def generate_value(prop, options, key_hint=None, faker=None, include_optional=True,
                   infer_from_description=False, root_schema=None, blank_mode=False):

    """Generate a random value for a given schema property."""

    if "$ref" in prop:
        if root_schema is None:
            raise ValueError("Missing root_schema when resolving $ref")
        ref_schema = resolve_ref(root_schema, prop["$ref"])
        # If the referenced schema is an object, delegate to generate_from_schema
        if ref_schema.get("type") == "object":
            return generate_from_schema(
                ref_schema, options, faker,
                include_optional, infer_from_description,
                blank_mode=blank_mode, root_schema=root_schema
            )
        else:
            return generate_value(
                ref_schema, options, key_hint, faker,
                include_optional, infer_from_description,
                root_schema, blank_mode
            )


    # Handle enums
    if "enum" in prop:
        if not prop["enum"]:  # Empty enum list
            if blank_mode:
                t = prop.get("type")
                if t == "number":
                    return 0.0
                elif t == "integer":
                    return 0
                elif t == "string":
                    return ""
                else:
                    return None
            else:
                return None  # Or raise an error if you want to enforce enum values
        return prop["enum"][0] if blank_mode else random.choice(prop["enum"])


    # Use custom options if provided
    title = prop.get("title", key_hint)
    if options and title in options:
        return "" if blank_mode else random.choice(options[title])

    # Infer type from description if no type is provided
    if not prop.get("type") and infer_from_description:
        return infer_type_from_description(prop.get("description", ""))

    # Handle standard types
    t = prop.get("type")
    fmt = prop.get("format")

    if t == "string":
        if fmt == "email":
            return "" if blank_mode else faker.email()
        elif fmt == "date":
            return "" if blank_mode else faker.date()
        elif fmt == "uri":
            return "" if blank_mode else faker.uri()
        else:
            desc = prop.get("description", "").lower()
            name = key_hint.lower() if key_hint else ""

            # Heuristics
            if any(x in name or x in desc for x in ["description", "descr", "summary", "text", "comment", "content"]):
                return "" if blank_mode else faker.sentence(nb_words=12)
            elif any(x in name or x in desc for x in ["name", "title", "namn"]):
                return "" if blank_mode else faker.name()
            elif any(x in name or x in desc for x in ["type", "status", "label"]):
                return "" if blank_mode else faker.word()
            elif any(x in name or x in desc for x in ["number", "nummer"]):
                return "0" if blank_mode else str(faker.random_int(min=0, max=10000))
            elif any(x in name or x in desc for x in ["email", "e-mail", "mail"]):
                return "" if blank_mode else faker.email()    
            elif any(x in name or x in desc for x in ["date", "datum"]):
                return "" if blank_mode else faker.date()
            else:
                return "" if blank_mode else faker.word()
    elif t == "integer":
        return 0 if blank_mode else faker.random_int(min=0, max=10000)
    elif t == "number":
        return 0.0 if blank_mode else faker.pyfloat(left_digits=2, right_digits=2)
    elif t == "boolean":
        return false if blank_mode else faker.boolean()
    elif t == "array":
        items = prop.get("items", {})
        results = []

        if isinstance(items, list):
            # Tuple validation: generate one item per schema
            for item_schema in items:
                results.append(generate_value(
                    item_schema,
                    options,
                    key_hint,
                    faker,
                    include_optional,
                    infer_from_description,
                    root_schema=root_schema,
                    blank_mode=blank_mode
                ))
        else:
            # Regular array with a single item schema
            for _ in range(random.randint(1, 3)):
                results.append(generate_value(
                    items,
                    options,
                    key_hint,
                    faker,
                    include_optional,
                    infer_from_description,
                    root_schema=root_schema,
                    blank_mode=blank_mode
                ))

        return results
    elif t == "object":
        return generate_from_schema(
            prop,
            options,
            faker,
            include_optional,
            infer_from_description,
            root_schema=root_schema
        )

    return None

def generate_from_schema(schema, options, faker, include_optional=True,
                         infer_from_description=False, blank_mode=False, root_schema=None):

    """Generate a full JSON object from the provided schema."""
    result = {}
    properties = schema.get("properties", {})

    for key, prop in properties.items():
        if key not in schema.get("required", []):
            if not include_optional:
                continue
        result[key] = generate_value(
            prop, options, key_hint=key, faker=faker,
            include_optional=include_optional,
            infer_from_description=infer_from_description,
            root_schema=root_schema or schema,
            blank_mode=blank_mode
        )
    return result
