"""Build and check. With --push, commit site changes and push without force."""
import argparse
import subprocess
from pathlib import Path
from build import build
from check import check

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8").stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true", help="Commit website changes and push to origin/main")
    parser.add_argument("--message", default="Update learning notes")
    args = parser.parse_args()
    build()
    check()
    if not args.push:
        print("Local preview ready. Use --push only when publication is requested.")
        return
    if git("branch", "--show-current") != "main":
        raise ValueError("Publication requires the main branch")
    if not git("remote", "get-url", "origin").endswith("Shengzhiruchu/EnglishLearning.git"):
        raise ValueError("Unexpected origin repository")
    if git("diff", "--cached", "--name-only"):
        raise ValueError("Existing staged changes: review them before publishing")
    git("add", "--", "site.json", "content", "templates", "assets", "docs")
    if not git("diff", "--cached", "--name-only"):
        print("No website changes to publish")
        return
    git("commit", "-m", args.message)
    git("push", "origin", "main")
    print("Pushed successfully. GitHub Pages deployment may take several minutes.")


if __name__ == "__main__":
    main()
