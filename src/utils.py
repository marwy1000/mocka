import random

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
