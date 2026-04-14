import os
import subprocess
import sys
import time
import json

CONFIG_FILE = "test.config"

def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = ["mocka_script_path", "directory_to_scan"]
    missing = [k for k in required if k not in cfg]

    if missing:
        raise KeyError(f"Missing config keys: {missing}")

    return cfg


def list_json_files(directory):
    return [
        os.path.join(root, f)
        for root, _, files in os.walk(directory)
        for f in files
        if f.endswith(".json")
    ]


def run_mocka_on_files(json_files, script_path, config_file):
    for _, file in enumerate(json_files, 1):

        cmd = [
            sys.executable,
            script_path,
            "--config",
            config_file,
            file
        ]

        try:
            subprocess.run(cmd, check=True)

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error while processing: {file}")
            print(e)
            sys.exit(1)

    print()


def main():
    start_time = time.time()

    cfg = load_config(CONFIG_FILE)

    script_path = cfg["mocka_script_path"]
    directory_to_scan = cfg["directory_to_scan"]
    config_file = cfg.get("config_file", "app.config")

    print(f"🔍 Scanning {directory_to_scan}")

    json_files = list_json_files(directory_to_scan)

    if not json_files:
        print("⚠️ No JSON files found.")
        return

    run_mocka_on_files(json_files, script_path, config_file)

    print(f"\n✅ Done. Total runtime: {time.time() - start_time:.2f} seconds.")


if __name__ == "__main__":
    main()