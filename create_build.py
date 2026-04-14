import subprocess
import sys

MENU_OPTIONS = [
    "Optimized (onedir) with PyInstaller",
    "New (onefile) with PyInstaller",
    "Old (onefile) with PyInstaller"
]

BUILD_CONFIGS = {
    1: {
        "mode": "onedir",
        "optimize": "1",
        "extra_flags": ["--distpath", "./dist"]
    },
    2: {
        "mode": "onefile",
        "optimize": "1",
        "extra_flags": []
    },
    3: {
        "mode": "onefile",
        "optimize": "2",
        "extra_flags": ["--clean"]
    }
}


def build(option: int):
    if option not in BUILD_CONFIGS:
        print(f"❌ Invalid option. Please provide a number 1-{len(MENU_OPTIONS)}.")
        sys.exit(1)

    config = BUILD_CONFIGS[option]
    print(f"🔨 Building Mocka executable (Option {option})...")

    cmd = [
        sys.executable, "-m", "PyInstaller",  # use current Python
        f"--{config['mode']}",
        "--noconfirm",
        "--disable-windowed-traceback",
        "--noupx",
        "--optimize", config["optimize"],
        "--name", "mocka",
        "./mocka.py",
    ] + config["extra_flags"]

    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("✅ Build successful.")
    else:
        print("❌ Build failed with exit code", result.returncode)
        sys.exit(result.returncode)


def get_option_from_user() -> int:
    print("Select build type:")
    for i, desc in enumerate(MENU_OPTIONS, start=1):
        print(i, desc)

    try:
        return int(input(f"Enter option [1-{len(MENU_OPTIONS)}]: ").strip())
    except ValueError:
        return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            option = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid option. Please provide a number 1-{len(MENU_OPTIONS)}.")
            sys.exit(1)
    else:
        option = get_option_from_user()

    build(option)