#!/usr/bin/env python3
"""Offline release-cask renderer contract checks (no Brew or network needed)."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from importlib.machinery import SourceFileLoader
render_module = SourceFileLoader("render_cask", str(ROOT / "scripts/render-cask.py")).load_module()

class CaskTests(unittest.TestCase):
    def test_renders_from_real_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            artifact = pathlib.Path(folder) / "SideLinker-Mac-1.1.0-21.dmg"
            artifact.write_bytes(b"fixture: not a release")
            uri = "https://github.com/wberry9813/SideLinker/releases/download/v1.1.0/SideLinker-Mac-1.1.0-21.dmg"
            content = render_module.render("1.1.0", uri, artifact)
            self.assertIn('app "SideLinker Mac.app"', content)
            import hashlib
            self.assertIn(hashlib.sha256(artifact.read_bytes()).hexdigest(), content)
            self.assertNotIn("__SHA256__", content)
            self.assertNotIn("\n  zap ", content)

    def test_rejects_mismatched_tag_and_nonpublic_url(self):
        with tempfile.TemporaryDirectory() as folder:
            artifact = pathlib.Path(folder) / "demo.dmg"
            artifact.write_bytes(b"fixture")
            with self.assertRaises(ValueError):
                render_module.render("1.1.0", "https://github.com/wberry9813/SideLinker/releases/download/v2.0/SideLinker-Mac-1.1.0-21.dmg", artifact)
            with self.assertRaises(ValueError):
                render_module.render("1.1.0", "https://example.com/release.dmg", artifact)

    def test_active_cask_never_contains_placeholders(self):
        active = ROOT / "Casks" / "sidelinker.rb"
        if active.exists():
            text = active.read_text(encoding="utf-8")
            self.assertNotIn("__SHA256__", text)
            self.assertNotIn("__URL__", text)
            self.assertNotIn("__VERSION__", text)
        self.assertTrue((ROOT / "templates" / "sidelinker.rb.in").exists())

if __name__ == "__main__":
    unittest.main()
