import subprocess

subprocess.run([
    "pyinstaller",
    "--onefile",
    "--name", "mockr",
    "./__main__.py"
])