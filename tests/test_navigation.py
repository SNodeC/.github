import copy
import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.snodec_sync import render_header
from tools.snodec_sync.navigation import ROOT, page_headers, validate_plan, _menu_svg


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
        if name == '.github':
            root = repo / 'README.md'
            root.write_text('<!-- snodec:begin organization -->\n'
                            '<p><a href="https://github.com/SNodeC">SNode.C</a></p>\n'
                            '<!-- snodec:end organization -->\n\n' + root.read_text())
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

    def test_control_repository_uses_declared_navigation(self):
        repo = self.fixture('.github')
        page_headers(repo)
        guide = (repo / 'docs/workflow-graph.md').read_text()
        self.assertIn(render_header('.github', 'docs/workflow-graph.md'), guide)
        self.assertIn('One physical prose paragraph.', guide)
        self.assertIn('Up to SNode.C', guide)
        self.assertIn('SNode.C repository', guide)
        self.assertIn('up-snodec-light.svg', guide)
        self.assertFalse((repo / 'docs/media/nav/up-snode-c-light.svg').exists())
        self.assertIn('SNode.C', (repo / 'docs/media/nav/up-snodec-light.svg').read_text())
        self.assertEqual(page_headers(repo, check=True), [])

    def test_absolute_profile_menu_keeps_local_generation_and_url(self):
        repo = self.fixture('.github')
        asset = repo / 'profile/media/menu/products.svg'
        asset.parent.mkdir(parents=True)
        asset.write_text(_menu_svg('Products', 274))
        url = 'https://raw.githubusercontent.com/SNodeC/.github/refs/heads/main/profile/media/menu/products.svg'
        foreign = 'https://example.com/menu.svg'
        profile = repo / 'profile/README.md'
        profile.write_text(f'# Organization\n\n<a href="#products"><img src="{url}" width="274" height="28"></a>\n'
                           f'<img src="{foreign}" width="274" height="28">\n')
        page_headers(repo)
        self.assertIn('width="160" height="28"', asset.read_text())
        self.assertIn(f'src="{url}" width="160" height="28"', profile.read_text())
        self.assertIn(f'src="{foreign}" width="274" height="28"', profile.read_text())
        self.assertEqual(page_headers(repo, check=True), [])

    def test_plan_chains_and_label_limit(self):
        validate_plan(self.plan)
        invalid = copy.deepcopy(self.plan)
        invalid['snode.c']['pages'][0]['up_label'] = 'A' * 16
        with self.assertRaisesRegex(ValueError, '15'):
            validate_plan(invalid)
        invalid = copy.deepcopy(self.plan)
        invalid['snode.c']['pages'][0]['up'] = 'docs/README.md'
        with self.assertRaisesRegex(ValueError, 'chain'):
            validate_plan(invalid)
        invalid = copy.deepcopy(self.plan)
        invalid['snode.c']['pages'][0]['new'] = '../outside.md'
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            validate_plan(invalid)

    def test_sections_block_precedes_authored_sections_and_is_idempotent(self):
        repo = self.fixture('snode.c')
        page = repo / 'docs/README.md'
        page.write_text(page.read_text() + '\n## Authored section\n\nPreserved authored paragraph.\n')
        page_headers(repo)
        text = page.read_text()
        self.assertEqual(text.count('## Sections'), 1)
        self.assertLess(text.index('## Sections'), text.index('## Authored section'))
        self.assertIn('Preserved authored paragraph.', text)
        self.assertEqual(page_headers(repo, check=True), [])

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
                    for target in re.findall(r'(?:href|src|srcset)="([^"]+)"', header):
                        if target.startswith('https:'):
                            self.assertEqual(target, 'https://github.com/SNodeC')
                            continue
                        file, _, fragment = target.partition('#')
                        destination = (repo / page['new']).parent / file
                        self.assertTrue(destination.is_file(), target)
                        if fragment:
                            self.assertIn(f'id="{fragment}"', destination.read_text(), target)
                baseline = self.hashes(repo)
                self.assertEqual(page_headers(repo, check=True), [])
                self.assertEqual(self.hashes(repo), baseline)
                page_headers(repo)
                self.assertEqual(self.hashes(repo), baseline)


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

    def test_section_list_opt_out_preserves_project_table_and_detects_menu_drift(self):
        repo = self.fixture('Packages')
        page = repo / 'status/README.md'
        table = '| Project | Latest release | Status |\n| --- | --- | --- |\n| Third | — | [Third](third.md) |'
        page.write_text(page.read_text() + '\n' + table + '\n')
        page_headers(repo)
        self.assertIn(table, page.read_text())
        self.assertNotIn('section-pages', page.read_text())
        self.assertEqual(page_headers(repo, check=True), [])
        asset = repo / 'docs/media/menu/build.svg'
        asset.write_text(asset.read_text().replace('font-size="15"', 'font-size="12"'))
        self.assertIn('docs/media/menu/build.svg', page_headers(repo, check=True))

    def test_mobile_sources_intrinsic_sizes_and_shared_font_spec(self):
        import xml.etree.ElementTree as ET
        from tools.snodec_sync.navigation import _header_button, FONT
        header = render_header('snode.c', 'docs/guides/README.md')
        self.assertLess(header.index('SNode.C organization'), header.index('SNode.C repository'))
        self.assertEqual(header.count('(max-width: 640px) and (prefers-color-scheme: dark)'), 2)
        self.assertEqual(header.count('width="160" height="28"'), 1)
        for width in (36, 160):
            svg = ET.fromstring(_header_button('Repository', 'Repository', 'repo', '#075985', 'light', width))
            self.assertEqual((svg.attrib['width'], svg.attrib['height']), (str(width), '28'))
            text = list(svg.iter('{http://www.w3.org/2000/svg}text'))
            self.assertEqual(len(text), int(width == 160))
            if text:
                self.assertEqual(text[0].attrib['font-size'], '15')
                self.assertEqual(text[0].attrib['font-weight'], '600')
                self.assertEqual(text[0].attrib['font-family'], FONT.replace('&quot;', '"'))

    def test_companion_root_organization_is_generated_without_page_enrollment(self):
        repo = Path(self.temp.name) / 'SNode.C-Book-Companion'
        repo.mkdir()
        (repo / 'README.md').write_text('# Companion\n\nPreserved reader text.\n')
        page_headers(repo)
        text = (repo / 'README.md').read_text()
        self.assertIn('snodec:begin organization', text)
        self.assertNotIn('snodec:begin page-header', text)
        self.assertIn('Preserved reader text.', text)
        self.assertLess(text.index('snodec:begin organization'), text.index('# Companion'))
        self.assertTrue((repo / 'docs/media/nav/organization-light.svg').is_file())
        self.assertFalse((repo / 'docs/media/nav/repository-light.svg').exists())
        self.assertEqual(page_headers(repo, check=True), [])
