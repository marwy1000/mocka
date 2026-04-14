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


class SchemaGenerator:
    def __init__(self, config, faker_instance):
        self.config = config
        self.faker = faker_instance

        # Type dispatch map
        self.type_handlers = {
            "string": self._generate_string,
            "integer": self._generate_number,
            "number": self._generate_number,
            "boolean": self._generate_boolean,
            "array": self._generate_array,
            "object": self._generate_object,
        }

        # Format handlers for strings
        self.format_handlers = {
            "date-time": lambda: self.faker.date_time().isoformat(),
            "date": lambda: self.faker.date(),
            "time": lambda: self.faker.time(),
            "duration": self._generate_duration_iso,
            "uri": lambda: self.faker.uri(),
            "ipv4": lambda: self.faker.ipv4(),
            "ipv6": lambda: self.faker.ipv6(),
            "email": lambda: self.faker.email(),
            "idn-email": lambda: self.faker.email(),
            "idn-hostname": lambda: self.faker.email(),
            "hostname": lambda: self.faker.hostname(),
        }

    def prepare_schema(self, schema):
        """
        Resolve all $ref in the schema recursively before generation.
        """
        return self.resolve_all_refs(schema)

    def generate(self, schema, args):
        return self._generate_from_schema(schema, args, root_schema=schema, path=[])

    def _generate_from_schema(self, schema, args, root_schema, path):
        result = {}
        properties = schema.get("properties", {})

        for prop_name, prop_schema in properties.items():
            if prop_name not in schema.get("required", []) and not args.include_optional:
                continue

            result[prop_name] = self._generate_value(
                prop_schema, args, prop_name, root_schema, path + [prop_name]
            )

        return result

    def _generate_value(self, schema, args, field_name, root_schema, path):
        if "enum" in schema:
            return self._handle_enum(schema, args.blank)

        # Handle combinators
        for key in ("oneOf", "anyOf"):
            if key in schema:
                return self._generate_value(
                    random.choice(schema[key]), args, field_name, root_schema, path
                )

        if "allOf" in schema:
            merged = {}
            for sub_schema in schema["allOf"]:
                val = self._generate_value(sub_schema, args, field_name, root_schema, path)
                if isinstance(val, dict):
                    merged.update(val)
            return merged

        schema_type = schema.get("type")
        if not schema_type and args.keymatch:
            return self._generate_from_keywords(schema, field_name, args.blank, path)

        handler = self.type_handlers.get(schema_type)
        if handler:
            try:
                return handler(schema, args, field_name, root_schema, path)
            except Exception as e:
                logger.warning('Field "%s" fallback for type "%s": %s', field_name, schema_type, e)
                return self._default_value(schema_type)

        return None

    def _generate_object(self, schema, args, field_name, root_schema, path):
        return self._generate_from_schema(schema, args, root_schema, path)

    def _generate_boolean(self, schema, args, field_name, root_schema, path):
        return False if args.blank else self.faker.boolean()

    def _generate_number(self, schema, args, field_name, root_schema=None, path=None):
        if args.blank:
            return 0 if schema.get("type") == "integer" else 0.0

        min_val, max_val = self._compute_numeric_bounds(schema)
        multiple_of = schema.get("multipleOf")

        if multiple_of:
            start = math.ceil(min_val / multiple_of)
            end = math.floor(max_val / multiple_of)
            value = multiple_of * random.randint(start, max(end, start))
        else:
            value = random.uniform(min_val, max_val)

        if schema.get("type") == "integer":
            value = int(math.floor(value))

        return value

    def _compute_numeric_bounds(self, schema):
        if "exclusiveMinimum" in schema:
            min_val = math.nextafter(schema["exclusiveMinimum"], float("inf"))
        elif "minimum" in schema:
            min_val = schema["minimum"]
        else:
            min_val = 0

        if "exclusiveMaximum" in schema:
            max_val = math.nextafter(schema["exclusiveMaximum"], float("-inf"))
        elif "maximum" in schema:
            max_val = schema["maximum"]
        else:
            max_val = min_val + 10000

        if min_val > max_val:
            min_val, max_val = max_val, min_val
        return min_val, max_val

    def _generate_string(self, schema, args, field_name, root_schema=None, path=None):
        if args.blank:
            return ""

        fmt = schema.get("format")
        if fmt in self.format_handlers:
            try:
                return self.format_handlers[fmt]()
            except Exception as e:
                logger.warning("Format handler failed: %s - %s", fmt, e)

        pattern = schema.get("pattern")
        if pattern:
            try:
                return rstr.xeger(pattern)
            except Exception as e:
                logger.warning("Pattern generation failed: %s - %s", pattern, e)

        return self._generate_from_keywords(schema, field_name, args.blank, path)

    def _generate_duration_iso(self):
        duration = timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        return isodate.duration_isoformat(duration)

    def _generate_array(self, schema, args, field_name, root_schema, path):
        min_items = schema.get("minItems", 0 if args.blank else 1)
        max_items = schema.get(
            "maxItems", self.config.get("max_array_length", DEFAULT_MAX_ARRAY_LENGTH)
        )
        length = 0 if args.blank else random.randint(min_items, max_items)

        items_schema = schema.get("items", {})
        additional_items = schema.get("additionalItems", True)
        unique_items = schema.get("uniqueItems", False)

        results = []

        if isinstance(items_schema, list):
            for idx, item_schema in enumerate(items_schema):
                if idx < length:
                    results.append(
                        self._generate_value(item_schema, args, field_name, root_schema, path)
                    )
            if additional_items and length > len(items_schema):
                extra_schema = additional_items if isinstance(additional_items, dict) else {}
                for _ in range(length - len(items_schema)):
                    results.append(
                        self._generate_value(extra_schema, args, field_name, root_schema, path)
                    )
        else:
            for _ in range(length):
                results.append(
                    self._generate_value(items_schema, args, field_name, root_schema, path)
                )

        if unique_items:
            results = self._ensure_unique(
                results,
                min_items,
                lambda: self._generate_value(items_schema, args, field_name, root_schema, path),
            )

        return results

    def _ensure_unique(self, items, min_items, generate_func):
        seen = set()
        unique_results = []

        for v in items:
            key = repr(v)
            if key not in seen:
                seen.add(key)
                unique_results.append(v)

        while len(unique_results) < min_items:
            candidate = generate_func()
            key = repr(candidate)
            if key not in seen:
                seen.add(key)
                unique_results.append(candidate)

        return unique_results

    def _generate_from_keywords(self, schema, field_name, blank_mode, path=None):
        text = f"{schema.get('description', '')} {schema.get('title', '')} {field_name}".strip()
        keyword_map = self.config.get("keyword_matching", [])
        field_name_lower = (field_name or "").lower()
        full_text = text.lower()

        def matches(entry):
            for kw in entry.get("keywords", []):
                if isinstance(kw, str) and kw.lower() in field_name_lower:
                    return True
                if isinstance(kw, dict) and self._matches_nested_pattern(kw, path or []):
                    return True
            return False

        for entry in keyword_map:
            if matches(entry):
                return self._faker_from_entry(entry, blank_mode, "string")

        if any(
            isinstance(k, str) and k.lower() in full_text
            for entry in keyword_map
            for k in entry.get("keywords", [])
        ):
            return self._faker_from_entry(entry, blank_mode, "string")

        return "" if blank_mode else self._default_value("string")

    def _matches_nested_pattern(self, pattern, path):
        if not isinstance(pattern, dict) or not path:
            return False

        for parent, child in pattern.items():
            parent = parent.lower()
            if isinstance(child, dict):
                for i in range(len(path) - 1):
                    if path[i].lower() == parent and self._matches_nested_pattern(
                        child, path[i + 1 :]
                    ):
                        return True
            elif isinstance(child, str):
                for i in range(len(path) - 1):
                    if path[i].lower() == parent and path[i + 1].lower() == child.lower():
                        return True
        return False

    def _faker_from_entry(self, entry, blank_mode, expected_type):
        if blank_mode:
            return ""
        method_name = entry["method"]
        args = entry.get("args", {})
        try:
            if method_name == "override":
                value = args.get("value", "")
            elif hasattr(self.faker, method_name):
                value = getattr(self.faker, method_name)(**args)
            else:
                logger.warning("Unknown faker method '%s'", method_name)
                value = self.faker.word()
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

    def _handle_enum(self, schema, blank_mode):
        enum_values = schema.get("enum", [])
        if not enum_values:
            return self._default_value(schema.get("type")) if blank_mode else None
        return enum_values[0] if blank_mode else random.choice(enum_values)

    def _default_value(self, expected_type):
        if expected_type == "string":
            return self.faker.word()
        if expected_type == "integer":
            return self.faker.random_int(min=0, max=10000)
        if expected_type == "number":
            return self.faker.pyfloat(left_digits=2, right_digits=2)
        if expected_type == "boolean":
            return self.faker.boolean()
        return self.faker.word()

    def _resolve_ref(self, ref_path, root_schema):
        if not ref_path.startswith("#/"):
            raise ValueError("Unsupported $ref format")
        current = root_schema
        for part in ref_path.lstrip("#/").split("/"):
            if not isinstance(current, dict):
                raise ValueError("Invalid $ref path")
            current = current.get(part)
            if current is None:
                raise ValueError("Unresolvable $ref path")
        return current

    def resolve_all_refs(self, schema, root_schema=None):
        root_schema = root_schema or schema

        if isinstance(schema, dict):
            if "$ref" in schema:
                resolved = self._resolve_ref(schema["$ref"], root_schema)
                return self.resolve_all_refs(resolved, root_schema)
            return {k: self.resolve_all_refs(v, root_schema) for k, v in schema.items()}

        if isinstance(schema, list):
            return [self.resolve_all_refs(item, root_schema) for item in schema]

        return schema
