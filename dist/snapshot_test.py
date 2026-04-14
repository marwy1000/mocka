import os
import subprocess
import sys
import time
import hashlib
import threading
import itertools
import json

CONFIG_FILE = "test_config.json"


def load_config(config_path):
    """Loads configuration from a JSON file."""
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    required_keys = ["mocka_exe_path", "directory_to_scan"]
    for key in required_keys:
        if key not in config:
            print(f"❌ Missing required configuration key: {key}")
            sys.exit(1)

    return config


def list_json_files(directory):
    """Recursively lists all JSON files in a given directory."""
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return sorted(json_files)


def normalize_text(text: str) -> str:
    """Normalizes text for deterministic hashing."""
    return text.replace("\r\n", "\n").strip()


def compute_text_hash(text: str) -> str:
    """Computes a SHA-256 hash of text."""
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_file_hash(file_path: str) -> str:
    """Computes a SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class Spinner:
    """A simple CLI spinner for visual feedback."""

    def __init__(self, message="Processing"):
        self.spinner = itertools.cycle(["|", "/", "-", "\\"])
        self.stop_running = threading.Event()
        self.thread = None
        self.message = message
        self.counter = 0

    def start(self):
        self.stop_running.clear()
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def _spin(self):
        while not self.stop_running.is_set():
            symbol = next(self.spinner)
            sys.stdout.write(
                f"\r{self.message} {symbol}  Files processed: {self.counter}"
            )
            sys.stdout.flush()
            time.sleep(0.1)

    def update(self):
        """Updates the processed file counter."""
        self.counter += 1

    def stop(self):
        self.stop_running.set()
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()


def run_mocka_on_files(json_files, mocka_exe_path, baseline_path, directory_to_scan, config_file):
    """Runs mocka.exe on each JSON file and stores filename with output hash."""
    results = []
    spinner = Spinner("Generating hashes")
    spinner.start()

    try:
        for json_file in json_files:
            cmd = [
                mocka_exe_path,
                "--config",
                config_file,
                json_file
            ]

            try:
                completed = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                output_hash = compute_text_hash(completed.stdout)
                relative_path = os.path.relpath(json_file, directory_to_scan)
                results.append(f"{relative_path}|{output_hash}")

                spinner.update()

            except subprocess.CalledProcessError as e:
                spinner.stop()
                print(f"\n❌ Error while processing {json_file}")
                print(e.stderr)
                sys.exit(1)

    finally:
        spinner.stop()

    with open(baseline_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(results) + "\n")

    print(f"📝 Baseline file generated: {baseline_path}")


def main():
    start_time = time.time()

    # Load configuration
    config = load_config(CONFIG_FILE)

    mocka_exe_path = config["mocka_exe_path"]
    directory_to_scan = config["directory_to_scan"]
    baseline_file = config.get("baseline_file", "hash_output_test.txt")
    config_file = config.get("config_file", "app.config")

    print(f"🔍 Scanning {directory_to_scan}")
    json_files = list_json_files(directory_to_scan)

    if not json_files:
        print("⚠️ No JSON files found.")
        sys.exit(0)

    run_mocka_on_files(
        json_files,
        mocka_exe_path,
        baseline_file,
        directory_to_scan,
        config_file
    )

    # Compute and display hash of the final baseline file
    final_hash = compute_file_hash(baseline_file)
    print(f"🔐 Hash of '{baseline_file}': {final_hash}")

    total_time = time.time() - start_time
    print(f"✅ Done. Total runtime: {total_time:.2f} seconds.")


if __name__ == "__main__":
    main()