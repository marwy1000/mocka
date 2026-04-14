"""
Functions for loading and validating schema/config inputs.
"""

import os
import sys
import json
import logging
import tkinter as tk
import pyperclip

logger = logging.getLogger(__name__)


class InputLoadError(Exception):
    """Raised when schema/config input cannot be loaded or parsed."""


def load_schema(schema_source: str | None = None) -> dict:
    logger.debug("Loading schema")

    source_label = schema_source or "clipboard"

    try:
        raw = _read_input(schema_source)
        data = _parse_json(raw, source_label)
        _ensure_dict(data, source_label)
        return data

    except InputLoadError as err:
        logger.error(str(err))
        sys.exit(1)


def load_config(config_file_path: str | None = None) -> dict:
    logger.debug("Loading config")

    if not config_file_path:
        return {}

    try:
        raw = _read_file(config_file_path)
        data = _parse_json(raw, config_file_path)
        _ensure_dict(data, config_file_path)
        return data

    except InputLoadError as err:
        logger.error(str(err))
        sys.exit(1)


def _read_input(source: str | None = None) -> str:
    if source:
        return _read_file(source)
    return _read_clipboard()


def _read_file(path: str) -> str:
    if not os.path.isfile(path):
        raise InputLoadError(f"File not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except PermissionError:
        raise InputLoadError(f"Permission denied: {path}")
    except OSError as err:
        raise InputLoadError(f"OS error reading {path}: {type(err).__name__}: {err}")


def _read_clipboard() -> str:
    """Retrieve clipboard text with fallback strategies"""
    try:
        pyperclip.set_clipboard("windows")
        return pyperclip.paste()
    except Exception:
        try:
            root = tk.Tk()
            root.withdraw()
            return root.clipboard_get()
        except Exception as err:
            raise InputLoadError(f"Unable to access clipboard: {err}")


def _parse_json(raw: str, source_label: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        raise InputLoadError(
            f"{source_label} contains invalid JSON: "
            f"{err.msg} (line {err.lineno}, column {err.colno})"
        )


def _ensure_dict(data, source_label: str):
    if not isinstance(data, dict):
        raise InputLoadError(f"{source_label} must be a JSON object (dict)")
