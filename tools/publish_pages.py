"""Publish the latest release's download page and compiled manual to gh-pages."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import zipfile

REPO = "impleotv/libmisb-release"
REMOTE = f"https://github.com/{REPO}.git"
ROOT = Path(__file__).resolve().parents[1]


def output(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def publish(tag):
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("Expected a version such as v0.12.0")
    latest = json.loads(output("gh", "api", f"repos/{REPO}/releases/latest"))
    if latest["tag_name"] != tag:
        raise ValueError("Pages must point to the current public release")
    version = tag[1:]
    assets = {a["name"]: a for a in latest["assets"]}
    base = f"https://github.com/{REPO}/releases/download/{tag}"
    html = (ROOT / "site/index.html").read_text(encoding="utf-8")
    html = html.replace("@VERSION@", version).replace("@ASSETS@", base)
    for name in re.findall(re.escape(base) + r'/([^"]+)', html):
        if name not in assets:
            raise ValueError(f"Missing release asset {name}")
    manual = f"libmisb-manual-{version}.zip"
    with tempfile.TemporaryDirectory(prefix="libmisb-pages-") as tmp:
        folder = Path(tmp)
        subprocess.run(["gh", "release", "download", tag, "-R", REPO, "-p", manual, "-D", folder], check=True)
        archive = folder / manual
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if assets[manual]["digest"] != f"sha256:{digest}":
            raise ValueError("Manual digest differs from GitHub's release asset")
        site = folder / "site"
        site.mkdir()

        def git(*args):
            return output("git", *args, cwd=site)

        git("init", "-b", "gh-pages")
        git("remote", "add", "origin", REMOTE)
        if git("ls-remote", "--heads", "origin", "refs/heads/gh-pages"):
            git("fetch", "--depth=1", "origin", "gh-pages")
            git("reset", "--mixed", "FETCH_HEAD")
        with zipfile.ZipFile(archive) as package:
            for member in package.infolist():
                path = PurePosixPath(member.filename)
                if (path.parts[:2] != ("libmisb-release", "manual")
                        or any(part.startswith(".") and part != ".nojekyll" for part in path.parts)
                        or "\\" in member.filename or ":" in member.filename):
                    raise ValueError(f"Unexpected manual ZIP entry {path}")
                dest = site.joinpath(*path.parts[1:])
                if member.is_dir():
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                with package.open(member) as src, dest.open("xb") as dst:
                    shutil.copyfileobj(src, dst)
        if not (site / "manual/docs/getting-started/index.html").is_file():
            raise ValueError("Customer quickstart is missing")
        (site / "index.html").write_text(html, encoding="utf-8")
        (site / ".nojekyll").touch()
        git("-c", "core.autocrlf=false", "add", "-A")
        if git("diff", "--cached", "--name-only"):
            git("commit", "-m", f"Publish libmisb SDK {tag} downloads and manual")
            git("push", "origin", "HEAD:gh-pages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    publish(parser.parse_args().tag)
