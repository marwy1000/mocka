"""
Utilities for loading and validating schema/config inputs.
"""

import os
import sys
import json
import logging
import tkinter as tk
import pyperclip
from .generator import resolve_all_refs

logger = logging.getLogger(__name__)


def load_schema(schema_source: str = None):
    logger.debug("Running function load_schema")

    if schema_source:
        try:
            with open(schema_source, "r", encoding="utf-8") as file:
                schema_dict = json.load(file)
                return resolve_all_refs(schema_dict)

        except FileNotFoundError:
            logger.error("Schema file not found: %s", schema_source)

        except json.JSONDecodeError as err:
            logger.error(
                "Invalid JSON in schema file %s: %s (line %d, column %d)",
                schema_source,
                err.msg,
                err.lineno,
                err.colno,
            )

        except PermissionError:
            logger.error("Permission denied for schema file: %s", schema_source)

        except OSError as err:
            logger.error(
                "OS error accessing schema file %s: %s: %s",
                schema_source,
                type(err).__name__,
                str(err),
            )

        except Exception as err:
            logger.error(
                "Unexpected error reading schema file %s: %s: %s",
                schema_source,
                type(err).__name__,
                str(err),
            )

        sys.exit(1)

    # Fallback: read schema from clipboard
    try:
        clipboard_content = read_clipboard()
        schema_dict = json.loads(clipboard_content)

    except json.JSONDecodeError as err:
        logger.error(
            "Clipboard JSON invalid: %s (line %d, column %d)",
            err.msg,
            err.lineno,
            err.colno,
        )
        sys.exit(1)

    except Exception as err:
        logger.error(
            "Error reading schema from clipboard: %s: %s",
            type(err).__name__,
            str(err),
        )
        sys.exit(1)

    if not isinstance(schema_dict, dict):
        logger.error("Clipboard JSON must be an object (dict).")
        sys.exit(1)

    return resolve_all_refs(schema_dict)


def load_config(config_file_path: str):
    config_dict = {}

    if config_file_path:
        if not os.path.isfile(config_file_path):
            logger.error("Config file not found: %s", config_file_path)
            sys.exit(1)

        try:
            with open(config_file_path, "r", encoding="utf-8") as file:
                config_dict = json.load(file)

        except json.JSONDecodeError as err:
            logger.error(
                "Invalid JSON in config file %s: %s (line %d, column %d)",
                config_file_path,
                err.msg,
                err.lineno,
                err.colno,
            )
            sys.exit(1)

        except Exception as err:
            logger.error(
                "Error reading config file %s: %s: %s",
                config_file_path,
                type(err).__name__,
                str(err),
            )
            sys.exit(1)

    return config_dict


def read_clipboard():
    """Retrieve clipboard text with fallback strategies"""
    try:
        pyperclip.set_clipboard("windows")  # Force Windows clipboard backend
        return pyperclip.paste()

    except Exception:
        try:
            tk_root = tk.Tk()
            tk_root.withdraw()
            return tk_root.clipboard_get()
        except Exception as err:
            logger.error("Unable to access clipboard: %s", err)
            sys.exit(1)
