import argparse
import pyperclip
import json

def parse_args():
    parser = argparse.ArgumentParser(description="Generate fake JSON from schema.")
    parser.add_argument("schema", nargs="?", help="Path to schema file (defaults to clipboard)")
    parser.add_argument("--out", "-o", help="Output file (optional)")
    parser.add_argument("--data", "-d", help="Optional fixed value choices")
    parser.add_argument("--seed", "-s", type=int, help="Random seed (optional)")
    parser.add_argument("--debug", "-v", action="store_true", help="Print debug info")
    parser.add_argument("--include-optional", "-io", action="store_true", default=True, help="Include optional fields (default: true)")
    parser.add_argument("--no-optional", "-no", dest="include_optional", action="store_false", help="Don't include optional fields")
    parser.add_argument("--infer-from-descriptions", "-i", action="store_true", default=False, help="Infer type from description if not provided")
    parser.add_argument('--blank', '-b', action='store_true', help='Generate blank values (empty strings, 0s, false, first enum, etc.)')

    return parser.parse_args()
