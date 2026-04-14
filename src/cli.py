"""
Provides command-line argument parsing for the Mocka tool.
"""

import argparse


def parse_args():
    """
    Parse command-line arguments for the Mocka JSON generation tool.
    """
    parser = argparse.ArgumentParser(description="Generate JSON from schema.")
    parser.add_argument("schema", nargs="?", help="Path to schema file (defaults to clipboard)")
    parser.add_argument("--version", "-v", action="store_true", help="Show version and exit")
    parser.add_argument("--debug", "-d", action="store_true", help="Print debug info")
    parser.add_argument(
        "--config",
        "-c",
        default="app.config",
        help="Mocka config file (will create and use the default if no input given).",
    )
    parser.add_argument(
        "--out-file", "-of",
        help="Output to file.",
        action="store_true"
    )
    parser.add_argument(
        "--out-clip", "-oc",
        help="Output to the clipboard.",
        action="store_true"
    )
    parser.add_argument(
        "--no-console", "-nc",
        help="Do not output to console.",
        action="store_false",
        default=True
    )
    parser.add_argument(
        "--seed",
        "-s",
        type=int,
        help="Random seed (optional), overrides config. 0 is random",
    )
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
        "--keymatch",
        "-k",
        action="store_false",
        help="Match keywords towards the key only, instead of key, description and title",
    )
    parser.add_argument(
        "--blank",
        "-b",
        action="store_true",
        help="Generate blank values (empty strings, 0s, false, first enum, etc.)",
    )
    return parser.parse_args()
