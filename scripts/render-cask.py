#!/usr/bin/env python3
"""Render an installable Homebrew Cask only from an existing release DMG.

This script DOES NOT publish a release, notarize, sign, upload, install or mutate macOS services.
It computes SHA-256 from the exact DMG bytes passed by the release operator.
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "sidelinker.rb.in"
DEFAULT_OUTPUT = ROOT / "Casks" / "sidelinker.rb"

def render(version: str, url: str, dmg: Path) -> str:
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}(?:[-.][0-9A-Za-z.-]+)?", version):
        raise ValueError("Invalid version; use a release version (e.g. 1.1.0)")
    parsed = urlparse(url)
    expected_prefix = "https://github.com/wberry9813/SideLinker/releases/download/"
    if parsed.scheme != "https" or parsed.netloc != "github.com" or not url.startswith(expected_prefix):
        raise ValueError("URL must point to a public SideLinker GitHub release asset")
    if parsed.query or parsed.fragment or not parsed.path.lower().endswith(".dmg"):
        raise ValueError("Expected a direct .dmg release asset URL without query/fragment")
    parts = parsed.path.split("/")
    if len(parts) != 7 or parts[4] != "download" or not parts[5] or not parts[6]:
        raise ValueError("Expected /releases/download/TAG/FILENAME.dmg")
    tag = unquote(parts[5])
    if tag not in (version, "v" + version):
        raise ValueError("Release tag must match the supplied version")
    filename = unquote(parts[6])
    if not filename.startswith("SideLinker-Mac-" + version + "-") or not filename.endswith(".dmg"):
        raise ValueError("DMG release filename must match SideLinker-Mac-VERSION-BUILD.dmg")
    if not dmg.is_file() or not dmg.name.endswith(".dmg"):
        raise ValueError("Provide the actual published DMG as a local .dmg file")
    digest = hashlib.sha256()
    with dmg.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    ruby = TEMPLATE.read_text(encoding="utf-8")
    for key, value in {"__VERSION__": version, "__SHA256__": digest.hexdigest(), "__URL__": url}.items():
        ruby = ruby.replace(key, value)
    return ruby

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--dmg", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        content = render(args.version, args.url, args.dmg)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f"Rendered {args.output}; SHA-256 derived from {args.dmg}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
