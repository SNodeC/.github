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
            self.assertTrue(output.is_file())


class ProfileTests(unittest.TestCase):
    def test_retired_has_no_ci_but_retiring_keeps_it(self):
        catalog = yaml.safe_load((ROOT / 'catalog.yml').read_text())
        metadata = json.loads((ROOT / 'profile/github-metadata.json').read_text())
        rendered = render_profile(catalog, metadata)
        for name in ['OpenWRT', 'SNode.C-Landingpages']:
            workflow = Path(metadata[name]['workflow']).name
            present = f'https://github.com/SNodeC/{name}/actions/workflows/{workflow}/badge.svg' in rendered
            self.assertEqual(present, name != 'OpenWRT')
        self.assertIn('_Retired_', rendered)


    def setUp(self):
        self.catalog = yaml.safe_load((ROOT / "catalog.yml").read_text())
        self.metadata = json.loads((ROOT / "profile/github-metadata.json").read_text())
        self.profile = render_profile(self.catalog, self.metadata)

    def test_deterministic_and_no_drift(self):
        self.assertEqual(self.profile, render_profile(self.catalog, self.metadata))


    def test_install_scope_follows_catalog(self):
        catalog = [dict(entry) for entry in self.catalog]
        next(entry for entry in catalog if entry["name"] == "AISuite")["packaged"] = True
        next(entry for entry in catalog if entry["name"] == "snode.c")["status"] = "retired"
        install = next(line for line in render_profile(catalog, self.metadata).splitlines() if "**Install signed packages:**" in line)
        self.assertTrue(install.endswith("mqttsuite · AISuite"))
        for entry in catalog:
            entry["packaged"] = False
        install = next(line for line in render_profile(catalog, self.metadata).splitlines() if "**Install signed packages:**" in line)
        self.assertTrue(install.endswith("[Packages](https://github.com/SNodeC/Packages)"))

    def test_every_repository_once_and_archived_separately(self):
        for entry in self.catalog:
            self.assertEqual(self.profile.replace("&#8203;", "").count(f"| [{entry['name']}]("), 1)
        visible, archive = self.profile.replace("&#8203;", "").split("<summary>Archive</summary>")
        for entry in self.catalog:
            row = f"| [{entry['name']}]("
            if entry["status"] != "active":
                self.assertNotIn(row, visible)
                self.assertIn(row, archive)
        forks = visible.split("<summary>Upstream forks</summary>")[1]
        for entry in self.catalog:
            if entry["kind"] == "fork":
                self.assertIn(f"| [{entry['name']}](", forks)
                self.assertIn("https://github.com/" + entry["upstream"], forks)

    def test_only_verified_workflows_and_releases(self):
        for entry in self.catalog:
            name = entry["name"]
            row = next(line for line in self.profile.replace("&#8203;", "").splitlines() if line.startswith(f"| [{name}]("))
            self.assertEqual("[![CI]" in row, "workflow" in self.metadata[name] and entry["status"] != "retired")
            self.assertEqual("/releases/tag/" in row, "release" in self.metadata[name])
        for entry in self.catalog:
            row = next(line for line in self.profile.replace("&#8203;", "").splitlines() if line.startswith(f"| [{entry['name']}]("))
            self.assertIn(f"<br>{entry['kind']} |", row)
            self.assertEqual("Depends on:" in row, bool(entry["depends_on"]))
            for dep in entry["depends_on"]:
                self.assertIn(f"[{dep}](https://github.com/SNodeC/{dep}" + (f"#{self.metadata[dep]['readme_anchor']}" if self.metadata[dep].get("readme_anchor") else "") + ")", row)
        self.assertIn("[v2.0.0]", self.profile)
        self.assertIn("[v1.0.2]", self.profile)

    def test_repository_navigation_uses_verified_banner_anchors_only(self):
        for name in ("snode.c", "mqttsuite", "AISuite", "CodexUI"):
            with self.subTest(name=name):
                self.assertEqual(self.metadata[name]["readme_anchor"], "project-overview")
                destinations = re.findall(r"\]\((https://github.com/SNodeC/" + re.escape(name) + r"(?:#[^)]*)?)\)", self.profile)
                self.assertTrue(destinations)
                self.assertEqual(set(destinations), {f"https://github.com/SNodeC/{name}#project-overview"})
                self.assertNotIn(f"{name}#project-overview/actions/", self.profile)
                self.assertNotIn(f"{name}#project-overview/releases/", self.profile)
        self.assertIn("[Packages](https://github.com/SNodeC/Packages)", self.profile)
        self.metadata["AISuite"].pop("readme_anchor")
        result = render_profile(self.catalog, self.metadata)
        self.assertIn("[AISuite](https://github.com/SNodeC/AISuite)<br>product", result.replace("&#8203;", ""))
        self.metadata["AISuite"]["readme_anchor"] = "banner/with space"
        result = render_profile(self.catalog, self.metadata)
        self.assertIn("[AISuite](https://github.com/SNodeC/AISuite#banner%2Fwith%20space)", result.replace("&#8203;", ""))




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
