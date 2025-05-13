"""
Module for loading and verifying loaded files
"""

import json
import sys
import tkinter as tk
import pyperclip
import logging
logger = logging.getLogger(__name__)
from .generator import resolve_all_refs


def load_schema(source=None):
    logger.debug("Running function loadschema")

    if source:
        try:
            with open(source, "r", encoding="utf-8") as f:
                parsed_schema = json.load(f)
                return resolve_all_refs(parsed_schema)
        except FileNotFoundError:
            logger.error(f"Schema file not found: {source}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in schema: {e}")
        except PermissionError:
            logger.error(f"Permission denied when accessing the schema file: {source}")
        except OSError as e:
            logger.error(f"OS error occurred: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    else:
        try:
            clipboard = get_clipboard_fallback()
            parsed_schema = json.loads(clipboard)
        except json.JSONDecodeError:
            logger.error("Error: Clipboard does not contain valid JSON.")
            sys.exit(1)

        if not isinstance(parsed_schema, dict):
            logger.error("Error: Clipboard JSON is not an object.")
            sys.exit(1)
        return resolve_all_refs(parsed_schema)


def load_config(config_path):
    config = {}
    if config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
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
            logger.error("Failed to access clipboard:", e)
            sys.exit(1)
