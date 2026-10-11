import copy
import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

from tools.snodec_sync import render_header
from tools.snodec_sync.navigation import ROOT, NS, ARROW, page_headers, validate_plan, _menu_svg
from tests.test_sync import contrast


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.plan = yaml.safe_load((ROOT / 'navigation/plan.yml').read_text())
        self.menu_labels = self.plan.pop('menu_labels', {})
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def fixture(self, name):
        repo = Path(self.temp.name) / name
        repo.mkdir()
        (repo / 'README.md').write_text('<a id="project-overview"></a>\n# Root\n\n'
                                      '<a href="docs/README.md#page-overview"><img src="docs/media/menu/build.svg" alt="Build" width="274" height="28"></a>\n')
        menu = repo / 'docs/media/menu'
        menu.mkdir(parents=True)
        (menu / 'build.svg').write_text(_menu_svg('Build', 274, 'right'))
        for page in self.plan[name]['pages']:
            if page.get('deleted') or page['old'] is None:
                continue
            path = repo / page['new']
            path.parent.mkdir(parents=True, exist_ok=True)
            title = page['title'] if page['title'] != '(generated)' else 'Recorded package status'
            body = ('<!-- published identity comment -->\n'
                    '<!-- snodec:begin page-header -->\n<a id="page-overview"></a>\n'
                    '<p><img src="old-page-banner.svg"></p>\n<!-- snodec:end page-header -->\n\n'
                    '<a id="historic-anchor"></a>\n\n'
                    f'# {title}\n\nOne physical prose paragraph.\n\n```sh\necho unchanged\n```\n')
            if page['new'] == 'docs/installation/debian.md':
                body += ('\n<a href="#quick-install" title="Install"><img src="../media/menu/install.svg" alt="Install" width="133" height="28"></a>\n'
                         '\n## Quick install\n')
                (menu / 'install.svg').write_text(_menu_svg('Install', 133))
            if page['new'] == 'status/snodec.md':
                body += '\n<a href="README.md#page-overview"><img src="menu/all-projects.svg" alt="All projects" width="133" height="28"></a>\n'
                body += '\n<a href="../README.md#install"><img src="../docs/media/menu/install.svg" alt="Install" width="133" height="28"></a>\n'
                (menu / 'install.svg').write_text(_menu_svg('Install', 133))
                m = repo / 'status/menu';m.mkdir(exist_ok=True)
                (m / 'all-projects.svg').write_text(_menu_svg('All projects', 133))
            path.write_text(body)
        return repo

    def hashes(self, repo):
        return {str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in repo.rglob('*') if p.is_file()}

    def test_plan_chains_and_label_limit(self):
        validate_plan(self.plan)
        invalid = copy.deepcopy(self.plan)
        invalid['snode.c']['pages'][0]['up_label'] = 'A' * 15
        with self.assertRaisesRegex(ValueError, '14'):
            validate_plan(invalid)
        invalid = copy.deepcopy(self.plan)
        invalid['snode.c']['pages'][0]['up'] = 'docs/README.md'
        with self.assertRaisesRegex(ValueError, 'chain'):
            validate_plan(invalid)
        invalid = copy.deepcopy(self.plan)
        invalid['snode.c']['pages'][0]['new'] = '../outside.md'
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            validate_plan(invalid)

    def test_all_generated_links_and_assets_resolve(self):
        for name, config in self.plan.items():
            with self.subTest(repo=name):
                repo = self.fixture(name)
                before_root = (repo / 'README.md').read_text()
                page_headers(repo)
                self.assertNotIn('page-header', (repo / 'README.md').read_text())
                self.assertEqual(re.findall(r'href="[^"]+"', before_root),
                                 re.findall(r'href="[^"]+"', (repo / 'README.md').read_text()))
                for page in config['pages']:
                    if page.get('deleted'):
                        continue
                    text = (repo / page['new']).read_text()
                    if page.get('excluded'):
                        self.assertNotIn('snodec:begin page-header', text)
                        continue
                    header = render_header(name, page['new'])
                    self.assertIn(header + '\n\n# ', text)
                    self.assertNotIn('<a href=', header.split('<p>')[1].split('</p>')[0])
                    self.assertEqual(header.count('<picture>'), 3)
                    self.assertEqual(header.count('align="right"'), 2)
                    self.assertIn('<br clear="all">', header)
                    for target in re.findall(r'(?:href|src|srcset)="([^"]+)"', header):
                        if target.startswith('https:'):
                            self.assertEqual(target, 'https://github.com/SNodeC')
                            continue
                        file, _, fragment = target.partition('#')
                        destination = (repo / page['new']).parent / file
                        self.assertTrue(destination.is_file(), target)
                        if fragment:
                            self.assertIn(f'id="{fragment}"', destination.read_text(), target)
                    svg = ET.parse(repo / 'docs/media/nav' / ('banner-' + re.sub('[^a-z0-9]+', '-', page['label'].lower()).strip('-') + '.svg')).getroot()
                    self.assertEqual(svg.attrib['viewBox'], '0 0 1280 56')
                self.assertIn('width="328"', (repo / 'README.md').read_text())
                baseline = self.hashes(repo)
                self.assertEqual(page_headers(repo, check=True), [])
                self.assertEqual(self.hashes(repo), baseline)
                page_headers(repo)
                self.assertEqual(self.hashes(repo), baseline)

    def test_order_duplicate_destinations_and_no_side_effects(self):
        repo = self.fixture('Packages')
        before = self.hashes(repo)
        text = render_header(repo, 'keys/README.md')
        self.assertEqual(self.hashes(repo), before)
        self.assertLess(text.index('up-packages-'), text.index('organization-dark'))
        self.assertLess(text.index('organization-dark'), text.index('repository-dark'))
        self.assertLess(text.index('repository-dark'), text.index('<br clear="all">'))
        self.assertEqual(text.count('href="../README.md#project-overview"'), 2)
        self.assertNotIn('Back', text)
        # Section lists use actual H1s and the declared Up chain, not a filesystem guess.
        page_headers(repo)
        listing = (repo / 'docs/README.md').read_text().split('snodec:begin section-pages')[1]
        self.assertIn('[Catalogs](catalogs/README.md#page-overview)', listing)
        self.assertNotIn('[Recorded package status](status.md', listing)
        self.assertIn(self.plan['Packages']['pages'][0]['intro'], (repo / 'docs/README.md').read_text())

    def test_project_registry_extension_inherits_generated_policy(self):
        text = render_header('Packages', 'status/third-project.md')
        self.assertIn('href="README.md#page-overview"', text)
        self.assertIn('banner-package-status.svg', text)
        with self.assertRaises(ValueError):
            render_header('Packages', 'docs/unplanned.md')
        with self.assertRaises(ValueError):
            render_header('snode.c', 'README.md')
        with self.assertRaises(ValueError):
            render_header('CodexUI', 'docs/media/README.md')

    def test_menu_changes_and_protected_body(self):
        repo = self.fixture('Packages')
        page_headers(repo)
        text = (repo / 'docs/installation/debian.md').read_text()
        self.assertIn('menu-quick-install.svg', text)
        self.assertIn('alt="Quick install"', text)
        self.assertNotIn('alt="All projects"', (repo / 'status/snodec.md').read_text())
        self.assertIn('href="../README.md#install"', (repo / 'status/snodec.md').read_text())
        self.assertIn('alt="Install"', (repo / 'status/snodec.md').read_text())
        for p in repo.rglob('*.md'):
            if p.name == 'README.md' or p.read_text().startswith('# Root'):
                continue
            self.assertIn('One physical prose paragraph.', p.read_text())
            self.assertIn('```sh\necho unchanged\n```', p.read_text())
            self.assertIn('id="historic-anchor"', p.read_text())
        section = (repo / 'docs/installation/README.md').read_text()
        self.assertIn('[Debian](debian.md#page-overview)', section)
        self.assertNotIn('install-snodec.md', section)

    def test_read_only_check_and_cli(self):
        repo = self.fixture('AISuite')
        before = self.hashes(repo)
        drift = page_headers(repo, check=True)
        self.assertTrue(drift)
        self.assertEqual(before, self.hashes(repo))
        for args, code in [(['--check'], 1), ([], 0), (['--check'], 0)]:
            result = subprocess.run([sys.executable, str(ROOT / 'tools/snodec_sync'), 'page-headers', '--repo', str(repo)] + args,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, code, result.stderr)

    def test_assets_styles_contrast_and_own_graphics(self):
        tokens = yaml.safe_load((ROOT / 'brand/tokens.yml').read_text())
        catalog = {e['name']:e for e in yaml.safe_load((ROOT / 'catalog.yml').read_text())}
        for name, config in self.plan.items():
            repo = self.fixture(name);page_headers(repo)
            entry = catalog[name]
            accent = tokens['accents'][entry.get('accent', tokens['area_accents'][entry['area']])]
            for svg_path in (repo / 'docs/media/nav').glob('*.svg'):
                svg = ET.parse(svg_path).getroot()
                if svg_path.name.startswith('banner-'):
                    for text in svg.findall(NS + 'text'):
                        for background in ['#101f35', '#172f47']:
                            self.assertGreaterEqual(contrast(text.attrib['fill'], background), 4.5)
                    self.assertEqual(svg.findall(NS + 'text')[0].text, config['display'])
                    self.assertEqual(svg.findall(NS + 'text')[1].attrib['fill'], accent['dark']['text'])
                    mark = ET.parse(ROOT / f'brand/navigation/marks/{name}.svg').getroot()
                    for node in mark.iter(NS + 'path'):
                        self.assertTrue(any(p.attrib.get('d') == node.attrib.get('d') for p in svg.iter(NS + 'path')))
                else:
                    self.assertEqual(svg.attrib['viewBox'], '0 0 160 28')
                    text = svg.find(NS + 'text');rect = svg.find(NS + 'rect')
                    self.assertGreaterEqual(contrast(text.attrib['fill'], rect.attrib['fill']), 4.5)
                    self.assertEqual(text.attrib['font-size'], '15')
                    self.assertEqual(text.attrib['font-weight'], '600')
                    self.assertIn('Permission is hereby granted', svg_path.read_text())
            menu = ET.parse(repo / 'docs/media/menu/build.svg').getroot()
            self.assertEqual(menu.attrib['width'], '328')
            self.assertEqual(menu.find(NS + 'path').attrib['d'], ARROW)
            self.assertGreaterEqual(contrast('#ffffff', '#203440'), 4.5)

    def test_no_moves_deletions_or_state_mutation(self):
        repo = self.fixture('Packages')
        for name in ['status.json', 'retention.json', 'install.sh', 'build.json']:
            (repo / name).write_text('protected bytes\n')
        before = {name:(repo / name).read_bytes() for name in ['status.json','retention.json','install.sh','build.json']}
        page_headers(repo)
        for name, body in before.items():
            self.assertEqual((repo / name).read_bytes(), body)
        deleted = repo / 'docs/setup.md';deleted.write_text('# Still present\n')
        with self.assertRaisesRegex(ValueError, 'git rm'):
            page_headers(repo)
        self.assertTrue(deleted.exists())

    def test_short_labels_do_not_change_accessible_destination(self):
        repo = self.fixture('Packages')
        button = repo / 'docs/media/menu/selected.svg'
        button.write_text(_menu_svg('Selected packages', 179, 'right'))
        page = repo / 'docs/installation/debian.md'
        page.write_text(page.read_text() + '\n<a href="#selected" title="Selected packages"><img src="../media/menu/selected.svg" alt="Selected packages" width="179" height="28"></a>\n')
        page_headers(repo)
        svg = ET.parse(button).getroot()
        self.assertEqual(svg.find(NS + 'text').text, 'Selected')
        self.assertEqual(svg.find(NS + 'title').text, 'Selected packages')
        self.assertIn('href="#selected" title="Selected packages"', page.read_text())
        self.assertIn('alt="Selected packages" width="160"', page.read_text())
        self.assertEqual(svg.find(NS + 'path').attrib['d'], ARROW)
        self.assertEqual(page_headers(repo, check=True), [])
