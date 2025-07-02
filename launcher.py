"""Simple launcher to automate building/pulling and running the Solana Bundler Bot Docker image.

Convert to a standalone Windows executable with:
    pyinstaller --onefile launcher.py

Usage examples (once compiled to launcher.exe):
    launcher.exe build   # build image locally and run
    launcher.exe pull    # pull image from GHCR and run
    launcher.exe stop    # stop running container
"""

import os
import subprocess
import sys
from pathlib import Path

IMAGE_LCL = "solana-bundler-bot:local"
IMAGE_GHCR = "ghcr.io/bearbucksc/solana-bundler-bot:latest"
CONTAINER_NAME = "solana-bundler-bot"
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / ".env"


def run(cmd: str):
    """Run shell command and stream output."""
    print(f"$ {cmd}")
    completed = subprocess.run(cmd, shell=True)
    if completed.returncode != 0:
        sys.exit(completed.returncode)


def stop_container():
    subprocess.run(f"docker rm -f {CONTAINER_NAME}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_and_run():
    run(f"docker build -t {IMAGE_LCL} .")
    stop_container()
    run(
        f"docker run -d --name {CONTAINER_NAME} -p 5000:5000 -p 8765:8765 "
        f"--env-file {ENV_FILE} {IMAGE_LCL}"
    )


def pull_and_run():
    run(f"docker pull {IMAGE_GHCR}")
    stop_container()
    run(
        f"docker run -d --name {CONTAINER_NAME} -p 5000:5000 -p 8765:8765 "
        f"--env-file {ENV_FILE} {IMAGE_GHCR}"
    )


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"build", "pull", "stop"}:
        print("Usage: launcher.py [build|pull|stop]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "build":
        build_and_run()
    elif action == "pull":
        pull_and_run()
    elif action == "stop":
        stop_container()
        print("Container stopped (if it was running).")


if __name__ == "__main__":
    main()
