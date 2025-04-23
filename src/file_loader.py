"""
Module for loading and verifying loaded files
"""

import json
import sys
import tkinter as tk
import pyperclip


def load_schema(source=None):
    if source:
        with open(source, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        clipboard = get_clipboard_fallback()
        try:
            parsed = json.loads(clipboard)
        except json.JSONDecodeError:
            print("Error: Clipboard does not contain valid JSON.")
            sys.exit(1)

        if not isinstance(parsed, dict):
            print("Error: Clipboard JSON is not an object.")
            sys.exit(1)

        return parsed


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
            print("Failed to access clipboard:", e)
            sys.exit(1)
