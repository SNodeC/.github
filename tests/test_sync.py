import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.snodec_sync.__main__ import AREAS, KINDS, ROOT, render_profile, validate


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = yaml.safe_load((ROOT / "catalog.yml").read_text())

    def test_current_catalog(self):
        self.assertEqual(validate(self.catalog), [])
        expected = {
            "snode.c", "mqttsuite", "AISuite", "CodexUI", "AutoTalk", "GpsdOsmViewer",
            "SNode.C-Book-Companion", "talks", "echo", "websocket-echo", "tiktaktoe",
            "ServerClient", "MiniGateway", "INJA-Templatebuilder", "IM510-Project",
            "snodec-forum-webapp", "SnodeCWebForum", "simple-form-snodec",
            "IOTApplicationDesigner", "leiches-masterproject", "mqtt-open-hue", ".github",
            "Packages", "DistributionPackages", "SNode.C-Landingpages", "snode.c-doc",
            "mqttsuite-doc", "OpenWRT", "CLI11", "json-schema-validator", "libucontext",
            "termux-packages", "arduino-LoRa", "iotempower",
        }
        self.assertEqual({e["name"] for e in self.catalog}, expected)

    def test_invalid_catalogs(self):
        cases = [
            ("area", "unknown"), ("area", []), ("kind", "unknown"), ("kind", {}),
            ("status", "archived"), ("name", "../escape"), ("summary", ""),
            ("summary", "two\nlines"), ("depends_on", "snode.c"),
            ("depends_on", ["missing"]), ("depends_on", [3]), ("packaged", "true"),
            ("site", 1), ("pinned", None), ("confirm", "yes"), ("ci", {}),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                entries = copy.deepcopy(self.catalog)
                entries[0][field] = value
                self.assertTrue(validate(entries))

    def test_missing_fields_and_duplicate_names(self):
        for field in ("name", "area", "kind", "summary", "depends_on", "status"):
            with self.subTest(field=field):
                entry = dict(self.catalog[0])
                del entry[field]
                self.assertTrue(validate([entry]))
        self.assertTrue(validate(self.catalog + [self.catalog[0]]))

    def test_accent_only_on_products(self):
        self.catalog[3]["accent"] = "interface-amber"
        self.assertIn("accent is allowed only on products", "\n".join(validate(self.catalog)))

    def test_forks_have_parent_and_stay_active(self):
        for upstream in (None, "", "no-owner", "../repo", 4):
            with self.subTest(upstream=upstream):
                entries = copy.deepcopy(self.catalog)
                entries[-1]["upstream"] = upstream
                self.assertTrue(validate(entries))
        self.catalog[-1]["status"] = "retired"
        self.assertTrue(validate(self.catalog))

    def test_malformed_entries_report_all_errors(self):
        errors = validate([None, {}, {"name": "x", "depends_on": ["absent"]}])
        self.assertGreater(len(errors), 8)
        self.assertIn("entry 3: unknown dependency absent", errors)
        self.assertTrue(validate({}))

    def test_cli_errors_and_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.yml"
            for content in ("[broken", "{}", "- name: invalid"):
                path.write_text(content)
                result = subprocess.run([sys.executable, str(ROOT / "tools/snodec_sync"),
                                         "check", "--catalog", str(path)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
            output = Path(directory) / "profile.md"
            result = subprocess.run([sys.executable, str(ROOT / "tools/snodec_sync"), "profile",
                                     "--output", str(output)], cwd=directory, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), (ROOT / "profile/README.md").read_bytes())


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.catalog = yaml.safe_load((ROOT / "catalog.yml").read_text())
        self.metadata = json.loads((ROOT / "profile/github-metadata.json").read_text())
        self.profile = render_profile(self.catalog, self.metadata)

    def test_deterministic_and_no_drift(self):
        self.assertEqual(self.profile, render_profile(self.catalog, self.metadata))
        self.assertEqual(self.profile, (ROOT / "profile/README.md").read_text())

    def test_area_order_and_navigation(self):
        headings = re.findall(r"^## (.+)$", self.profile, re.M)
        self.assertEqual(headings, ["Start here", *list(AREAS.values())[:-1]])
        self.assertIn("[examples](#learn)", self.profile)
        for name in ("snode.c", "mqttsuite", "SNode.C-Book-Companion", "Packages"):
            self.assertIn("https://github.com/SNodeC/" + name, self.profile)
        self.assertIn('alt="SNode.C mark"', self.profile)
        self.assertIn("[Framework](#framework)", self.profile)
        self.assertIn("[Distribution & infrastructure](#distribution--infrastructure)", self.profile)
        self.assertNotRegex(self.profile, r"\b\d+ (?:projects|repositories)\b")
        self.assertNotIn("2026-10-10", self.profile)

    def test_every_repository_once_and_archived_separately(self):
        for entry in self.catalog:
            self.assertEqual(self.profile.count(f"| [{entry['name']}]("), 1)
        visible, archive = self.profile.split("<summary>Archive</summary>")
        for entry in self.catalog:
            row = f"| [{entry['name']}]("
            if entry["status"] != "active":
                self.assertNotIn(row, visible)
                self.assertIn(row, archive)
        forks = visible.split("<summary>Upstream forks — kept for future work</summary>")[1]
        for entry in self.catalog:
            if entry["kind"] == "fork":
                self.assertIn(f"| [{entry['name']}](", forks)
                self.assertIn("https://github.com/" + entry["upstream"], forks)

    def test_only_verified_workflows_and_releases(self):
        for entry in self.catalog:
            name = entry["name"]
            row = next(line for line in self.profile.splitlines() if line.startswith(f"| [{name}]("))
            self.assertEqual("[![CI]" in row, "workflow" in self.metadata[name])
            self.assertEqual("/releases/tag/" in row, "release" in self.metadata[name])
        for entry in self.catalog:
            row = next(line for line in self.profile.splitlines() if line.startswith(f"| [{entry['name']}]("))
            self.assertIn(f" · {entry['kind']} |", row)
            self.assertEqual("Depends on:" in row, bool(entry["depends_on"]))
            for dep in entry["depends_on"]:
                self.assertIn(f"[{dep}](https://github.com/SNodeC/{dep})", row)
        self.assertIn("[v2.0.0]", self.profile)
        self.assertIn("[v1.0.2]", self.profile)

    def test_notes_and_footer(self):
        self.assertEqual(self.profile.count("Standalone tool, not built on SNode.C"), 2)
        for link in ("CONTRIBUTING.md", "SECURITY.md"):
            self.assertIn(link, self.profile)
            self.assertTrue((ROOT / link).is_file())
        self.assertIn("https://github.com/VolkerChristian", self.profile)

    def test_default_branch_is_metadata_not_constant(self):
        self.metadata[".github"]["default_branch"] = "control/branch"
        self.metadata["snode.c"]["default_branch"] = "framework/branch"
        result = render_profile(self.catalog, self.metadata)
        self.assertIn("/blob/control%2Fbranch/", result)
        self.assertIn("?branch=framework%2Fbranch", result)

    def test_authored_text_cannot_break_table_or_inject_html(self):
        self.catalog[0]["summary"] = "<script> | [unexpected](bad)"
        rendered = render_profile(self.catalog, self.metadata)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn(r"\|", rendered)
        self.assertIn(r"\[unexpected\]", rendered)
        self.assertNotIn("<script>", rendered)

    def test_metadata_is_separate_and_complete(self):
        self.assertEqual(set(self.metadata), {e["name"] for e in self.catalog})
        for name, info in self.metadata.items():
            self.assertIsInstance(info["default_branch"], str)
            self.assertTrue(info["default_branch"])
            if name != ".github":
                self.assertRegex(info["source_commit"], r"^[a-f0-9]{40}$")
            if "workflow" in info:
                self.assertRegex(info["workflow"], r"^\.github/workflows/[^/]+\.ya?ml$")
            if "release" in info:
                self.assertIsInstance(info["release"]["tag"], str)
                self.assertIsInstance(info["release"]["prerelease"], bool)


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class BrandTests(unittest.TestCase):
    def test_wcag_aa_both_themes(self):
        tokens = yaml.safe_load((ROOT / "brand/tokens.yml").read_text())
        self.assertEqual(set(tokens["area_accents"]), set(AREAS))
        self.assertEqual(len(tokens["accents"]), 8)
        for name, themes in tokens["accents"].items():
            self.assertEqual(set(themes), {"light", "dark"})
            for theme, values in themes.items():
                with self.subTest(accent=name, theme=theme):
                    for color in values.values():
                        self.assertRegex(color, r"^#[a-f0-9]{6}$")
                    self.assertGreaterEqual(contrast(values["text"], values["background"]), 4.5)
        catalog = yaml.safe_load((ROOT / "catalog.yml").read_text())
        for entry in catalog:
            self.assertIn(entry.get("accent", tokens["area_accents"][entry["area"]]), tokens["accents"])

    def test_glyph_contract(self):
        import xml.etree.ElementTree as ET
        files = list((ROOT / "brand/glyphs").glob("*.svg"))
        self.assertEqual({p.stem for p in files}, KINDS)
        for path in files:
            svg = ET.parse(path).getroot()
            self.assertEqual(svg.attrib["viewBox"], "0 0 24 24")
            self.assertEqual(svg.attrib["stroke"], "currentColor")
            self.assertEqual(svg.attrib["stroke-width"], "1.5")
            self.assertEqual(svg.attrib["fill"], "none")
            self.assertTrue(svg.find("{http://www.w3.org/2000/svg}title").text)
