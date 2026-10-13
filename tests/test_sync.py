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
            "IOTApplicationDesigner", "mqtt-open-hue", ".github",
            "snode.c-idp", "mqtt-bridge-config-ui", "mqttsuite-integrator-rest-api",
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
    def setUp(self):
        self.catalog = yaml.safe_load((ROOT / "catalog.yml").read_text())
        self.metadata = json.loads((ROOT / "profile/github-metadata.json").read_text())
        self.template = (ROOT / "profile/template.md").read_text()
        self.profile = render_profile(self.catalog, self.metadata)

    def test_deterministic_reference_and_navigation_stability(self):
        self.assertEqual(self.profile, render_profile(self.catalog, self.metadata))
        self.assertEqual(self.profile, (ROOT / "profile/README.md").read_text())
        from tools.snodec_sync.navigation import page_headers
        self.assertEqual(page_headers(ROOT, check=True), [])
        self.assertTrue(self.profile.endswith("\n"))

    def test_every_catalog_entry_has_exact_row_coverage(self):
        for entry in self.catalog:
            with self.subTest(name=entry['name']):
                # Count catalog row links, not intentional prose/badge/route links.
                pattern = r"^\| (?:\*\*)?\[[^]]+\]\(https://github.com/SNodeC/" + re.escape(entry['name']) + r"(?=[)#/])"
                expected = 0 if entry.get('tier') == 'install' else 2 if entry.get('tier') == 'product' and entry.get('student') else 1
                self.assertEqual(len(re.findall(pattern, self.profile, re.M)), expected)
                if entry.get('tier') == 'install':
                    self.assertRegex(self.template, r'https://github.com/SNodeC/' + re.escape(entry['name']) + r'(?=[)#/])')

    def test_no_unknown_repository_links(self):
        names = {entry['name'] for entry in self.catalog}
        linked = set(re.findall(r'https://github.com/SNodeC/([^/#?\s)]+)(?=[)#/])', self.profile))
        self.assertEqual(linked - names, set())

    def test_only_verified_product_workflows_and_releases(self):
        for entry in self.catalog:
            if entry.get('tier') != 'product':
                continue
            name = entry['name']
            row = next(line for line in self.profile.splitlines() if line.startswith(f"| **[{entry['title']}]("))
            self.assertEqual('[![CI]' in row, bool(self.metadata[name].get('workflow')))
            self.assertEqual('[Releases]' in row, bool(self.metadata[name].get('release')))
        for key in ['workflow', 'release']:
            self.metadata['snode.c'].pop(key)
        rendered = render_profile(self.catalog, self.metadata)
        row = next(line for line in rendered.splitlines() if line.startswith('| **[SNode.C]('))
        self.assertNotIn('[![CI]', row)
        self.assertNotIn('[Releases]', row)

    def test_repository_navigation_uses_metadata_anchors_only(self):
        for name in ['snode.c', 'mqttsuite', 'AISuite', 'CodexUI']:
            self.assertIn(f'](https://github.com/SNodeC/{name}#project-overview)**', self.profile)
            self.assertNotIn(f'{name}#project-overview/actions/', self.profile)
            self.assertNotIn(f'{name}#project-overview/releases/', self.profile)
        self.metadata['AISuite'].pop('readme_anchor')
        rendered = render_profile(self.catalog, self.metadata)
        row = next(line for line in rendered.splitlines() if line.startswith('| **[AISuite]('))
        self.assertIn('](https://github.com/SNodeC/AISuite)**', row)
        self.assertNotIn('[Quick start]', row)
        self.assertNotIn('[Install]', row)
        self.metadata['AISuite']['readme_anchor'] = 'banner/with space'
        self.assertIn('AISuite#banner%2Fwith%20space)**', render_profile(self.catalog, self.metadata))

    def test_default_branch_comes_from_metadata(self):
        self.metadata['.github']['default_branch'] = 'control/branch'
        self.metadata['snode.c']['default_branch'] = 'framework/branch'
        rendered = render_profile(self.catalog, self.metadata)
        self.assertIn('/blob/control%2Fbranch/', rendered)
        self.assertIn('?branch=framework%2Fbranch', rendered)

    def test_authored_text_cannot_break_table_or_inject_html(self):
        for field in ['title', 'purpose', 'summary']:
            self.catalog[0][field] = '<script> | [unexpected](bad)'
        rendered = render_profile(self.catalog, self.metadata)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn(r'\|', rendered)
        self.assertIn(r'\[unexpected\]', rendered)
        self.assertNotIn('<script>', rendered)
        # Summary sanitising also applies to Learn and collapsed groups.
        for name in ['echo', 'AutoTalk']:
            next(e for e in self.catalog if e['name'] == name)['summary'] = '<script> | [unexpected](bad)'
        self.assertNotIn('<script>', render_profile(self.catalog, self.metadata))

    def test_tier_validation(self):
        for field, value in [('tier', 'unknown'), ('tier', []), ('title', ''), ('title', 'two\nlines'),
                             ('purpose', None), ('purpose', 'two\rlines'), ('student', 'true'), ('student', 1)]:
            with self.subTest(field=field, value=value):
                catalog = copy.deepcopy(self.catalog)
                catalog[0][field] = value
                self.assertTrue(validate(catalog))
        for field in ['title', 'purpose']:
            catalog = copy.deepcopy(self.catalog)
            catalog[0].pop(field)
            self.assertTrue(validate(catalog))
        catalog = copy.deepcopy(self.catalog)
        catalog[0]['kind'] = 'example'
        catalog[0].pop('accent')
        self.assertIn('product tier requires product or app kind', '\n'.join(validate(catalog)))
        catalog[0].update(kind='product', tier='secondary')
        self.assertIn('secondary products require student: true', '\n'.join(validate(catalog)))
        catalog[0]['student'] = True
        self.assertEqual(validate(catalog), [])
        catalog[0].pop('tier')
        self.assertEqual(validate(catalog), [])
        catalog[0]['student'] = False
        self.assertTrue(validate(catalog))

    def test_grouping_and_precedence(self):
        groups = {re.search(r'<b>([^<]+)</b>', block)[1]: block
                  for block in self.profile.split('<details>')[1:]}
        for name, group in [('tiktaktoe', 'Examples'), ('IOTApplicationDesigner', 'Student projects'),
                            ('mqtt-bridge-config-ui', 'Student projects'), ('mqttsuite-integrator-rest-api', 'Student projects'),
                            ('snode.c-idp', 'Student projects'), ('AutoTalk', 'Standalone applications'),
                            ('DistributionPackages', 'Infrastructure'), ('CLI11', 'Upstream forks'), ('OpenWRT', 'Archive')]:
            self.assertIn(f'| [{name}](', groups[group])
        for name in ['snode.c', 'mqttsuite', 'AISuite', 'CodexUI', 'echo', 'Packages']:
            self.assertNotIn(f'| [{name}](', '\n'.join(groups.values()))
        entry = next(e for e in self.catalog if e['name'] == 'mqtt-bridge-config-ui')
        entry.update(status='retiring', kind='example')
        rendered = render_profile(self.catalog, self.metadata)
        visible, archive = rendered.split('<summary><b>Archive</b>')
        self.assertNotIn('| [mqtt-bridge-config-ui](', visible)
        self.assertIn('| [mqtt-bridge-config-ui](', archive)
        self.assertIn('Graphical editor for MQTTBridge configurations · retiring', archive)
        entry['status'] = 'active'
        rendered = render_profile(self.catalog, self.metadata)
        student = rendered.split('<summary><b>Student projects</b>')[1].split('</details>')[0]
        self.assertIn('| [mqtt-bridge-config-ui](', student)
        examples = rendered.split('<summary><b>Examples</b>')[1].split('</details>')[0]
        self.assertNotIn('| [mqtt-bridge-config-ui](', examples)
        # Empty groups are omitted rather than rendered as empty tables.
        catalog = [e for e in self.catalog if e['kind'] != 'example' or e.get('tier') == 'learn']
        self.assertNotIn('<summary><b>Examples</b>', render_profile(catalog, self.metadata))

    def test_template_markers_are_exactly_once_and_standalone(self):
        for name in ['products', 'learn', 'more']:
            marker = f'<!-- profile:{name} -->'
            for template in [self.template.replace(marker, ''), self.template + marker,
                             self.template.replace(marker, 'prefix ' + marker)]:
                with self.subTest(marker=marker, template=template[-40:]):
                    with self.assertRaisesRegex(ValueError, 'exactly one standalone'):
                        render_profile(self.catalog, self.metadata, template)

    def test_relative_media_paths_exist(self):
        paths = re.findall(r'(?:src|srcset)="(media/[^"\s]+)"', self.profile)
        self.assertTrue(paths)
        for path in paths:
            self.assertTrue((ROOT / 'profile' / path).is_file(), path)

    def test_metadata_is_separate_and_complete(self):
        self.assertEqual(set(self.metadata), {e['name'] for e in self.catalog})
        for name, info in self.metadata.items():
            self.assertIsInstance(info['default_branch'], str)
            self.assertTrue(info['default_branch'])
            if name != '.github':
                self.assertRegex(info['source_commit'], r'^[a-f0-9]{40}$')
            if 'workflow' in info:
                self.assertRegex(info['workflow'], r'^\.github/workflows/[^/]+\.ya?ml$')
            if 'release' in info:
                self.assertIsInstance(info['release']['tag'], str)
                self.assertIsInstance(info['release']['prerelease'], bool)
