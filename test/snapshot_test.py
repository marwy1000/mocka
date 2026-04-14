import os
import subprocess
import sys
import time
import hashlib
import json
import itertools


CONFIG_FILE = "test.config"


# ----------------------------
# Config
# ----------------------------
def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = ("mocka_script_path", "directory_to_scan")
    missing = [k for k in required if k not in cfg]

    if missing:
        raise KeyError(f"Missing config keys: {missing}")

    return cfg


# ----------------------------
# File discovery (faster + simpler)
# ----------------------------
def list_json_files(directory):
    return sorted(
        os.path.join(root, f)
        for root, _, files in os.walk(directory)
        for f in files
        if f.endswith(".json")
    )


# ----------------------------
# Hashing (optimized: no extra function calls)
# ----------------------------
def hash_text(text: str) -> str:
    return hashlib.sha256(
        text.replace("\r\n", "\n").strip().encode("utf-8")
    ).hexdigest()


def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):  # larger buffer = faster
            h.update(chunk)
    return h.hexdigest()


# ----------------------------
# Core execution
# ----------------------------
def run(json_files, script_path, config_file, base_dir):
    results = []
    total = len(json_files)

    for i, file in enumerate(json_files, 1):
        # inline progress (no thread, no spinner overhead)
        print(f"\rProcessing {i}/{total}", end="", flush=True)

        cmd = [
            sys.executable,  # avoids hardcoding "python"
            script_path,
            "--config",
            config_file,
            file
        ]

        try:
            out = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            ).stdout

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed: {file}")
            print(e.stderr)
            sys.exit(1)

        rel = os.path.relpath(file, base_dir)
        results.append(f"{rel}|{hash_text(out)}")

    print()  # newline after progress
    return results


# ----------------------------
# Main
# ----------------------------
def main():
    start = time.time()

    cfg = load_config(CONFIG_FILE)

    script_path = cfg["mocka_script_path"]
    base_dir = cfg["directory_to_scan"]
    config_file = cfg.get("config_file", "app.config")
    out_file = cfg.get("baseline_file", "hash_output_test.txt")

    print(f"Scanning {base_dir}")

    files = list_json_files(base_dir)
    if not files:
        print("⚠️ No JSON files found.")
        return

    results = run(files, script_path, config_file, base_dir)

    # single write (fast + atomic-ish behavior)
    with open(out_file, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(results) + "\n")

    final_hash = hash_file(out_file)

    print(f"Baseline: {out_file}")
    print(f"Hash: {final_hash}")
    print(f"Time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()