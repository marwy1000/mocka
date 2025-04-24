"""
Provides command-line argument parsing for the mockr tool.
"""

import argparse


def parse_args():
    """
    Parse command-line arguments for the mockr JSON generation tool.
    """
    parser = argparse.ArgumentParser(description="Generate fake JSON from schema.")
    parser.add_argument(
        "schema", nargs="?", help="Path to schema file (defaults to clipboard)"
    )
    parser.add_argument("--out", "-o", help="Output file (optional)")
    parser.add_argument("--config", "-c", help="Python Faker Config")
    parser.add_argument("--seed", "-s", type=int, help="Random seed (optional), overrides config. 0 is random")
    parser.add_argument("--debug", "-d", action="store_true", help="Print debug info")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--include-optional",
        "-io",
        action="store_true",
        dest="include_optional",
        help="Include optional fields (default)",
    )
    group.add_argument(
        "--no-optional",
        "-no",
        action="store_false",
        dest="include_optional",
        help="Don't include optional fields",
    )
    parser.set_defaults(include_optional=True)
    parser.add_argument(
        "--infer",
        "-i",
        action="store_true",
        default=False,
        help="Infer type from description if not provided",
    )
    parser.add_argument(
        "--blank",
        "-b",
        action="store_true",
        help="Generate blank values (empty strings, 0s, false, first enum, etc.)",
    )

    return parser.parse_args()
