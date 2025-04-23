import subprocess
import sys

def build():
    print("🔨 Building mockr executable...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--disable-windowed-traceback",
        "--optimize", "2",
        "--name", "mockr",
        "./__main__.py"
    ]

    if sys.platform != "win32":
        cmd.append("--strip")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("✅ Build successful.")
    else:
        print("❌ Build failed with exit code", result.returncode)
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
