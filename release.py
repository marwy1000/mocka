import subprocess
import sys

def run(cmd):
    print(f"▶️ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)

def release(version, message=""):
    if not version.startswith("v"):
        version = f"v{version}"

    print(f"🚀 Releasing {version}...")

    run("git add .")
    run(f'git commit -m "{message or f"Release {version}"}"')
    run(f'git tag -a {version} -m "{message or f"Release {version}"}"')
    run("git push origin main")
    run(f"git push origin {version}")
    # Optional GitHub CLI release
    run(f'gh release create {version} --title "{version}" --notes "{message or version}"')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python release.py <version> [message]")
        sys.exit(1)
    release(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
