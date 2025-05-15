"""
Module for loading and verifying loaded files
"""

import os
import sys
import json
import logging
import tkinter as tk
import pyperclip
from .generator import resolve_all_refs

logger = logging.getLogger(__name__)


def load_schema(source=None):
    logger.debug("Running function load_schema")

    if source:
        try:
            with open(source, "r", encoding="utf-8") as f:
                parsed_schema = json.load(f)
                return resolve_all_refs(parsed_schema)
        except FileNotFoundError:
            logger.error("Schema file not found: %s", source)
        except json.JSONDecodeError as e:
            logger.error(
                "Invalid JSON format in schema file %s: %s (line %d, column %d)",
                source,
                e.msg,
                e.lineno,
                e.colno,
            )
        except PermissionError:
            logger.error("Permission denied when accessing schema file: %s", source)
        except OSError as e:
            logger.error(
                "OS error while accessing schema file %s: %s: %s",
                source,
                type(e).__name__,
                str(e),
            )
        except Exception as e:
            logger.error(
                "Unexpected error reading schema file %s: %s: %s",
                source,
                type(e).__name__,
                str(e),
            )
        sys.exit(1)

    else:
        try:
            clipboard = get_clipboard_fallback()
            parsed_schema = json.loads(clipboard)
        except json.JSONDecodeError as e:
            logger.error(
                "Clipboard contains invalid JSON: %s (line %d, column %d)",
                e.msg,
                e.lineno,
                e.colno,
            )
            sys.exit(1)
        except Exception as e:
            logger.error(
                "Unexpected error reading schema from clipboard: %s: %s",
                type(e).__name__,
                str(e),
            )
            sys.exit(1)

        if not isinstance(parsed_schema, dict):
            logger.error("Clipboard JSON is not an object.")
            sys.exit(1)

        return resolve_all_refs(parsed_schema)


def load_config(config_path):
    config = {}
    if config_path:
        if not os.path.isfile(config_path):
            logger.error("Config file not found: %s", config_path)
            sys.exit(1)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(
                "Invalid JSON in config file %s: %s (line %d, column %d)",
                config_path,
                e.msg,
                e.lineno,
                e.colno,
            )
            sys.exit(1)
        except Exception as e:
            logger.error(
                "Unexpected error reading config file %s: %s: %s",
                config_path,
                type(e).__name__,
                str(e),
            )
            sys.exit(1)
    return config


def get_clipboard_fallback():
    try:
        pyperclip.set_clipboard("windows")  # Force Windows clipboard backend
        return pyperclip.paste()
    except Exception:
        try:
            r = tk.Tk()
            r.withdraw()
            return r.clipboard_get()
        except Exception as e:
            logger.error("Failed to access clipboard: %s", e)
            sys.exit(1)
