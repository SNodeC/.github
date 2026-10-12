import copy
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.snodec_sync.docs_audit import _document, docs_audit
from tools.snodec_sync.navigation import validate_plan, _config, _banner
from tools.snodec_sync.__main__ import ROOT, render_profile
import json


class DocsAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'checkout'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('remote', 'add', 'origin', 'git@github.com:SNodeC/snode.c.git')
        self.plan = Path(self.temp.name) / 'plan.yml'
        self.config = {'snode.c': {'pages': [], 'sections': {}}}
        self.write('README.md', '# Root\n')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True)

    def write(self, path, text, tracked=True):
        p = self.repo / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        if tracked:
            self.git('add', path)

    def audit(self):
        self.plan.write_text(yaml.safe_dump(self.config))
        return docs_audit(self.repo, self.plan)

    def declare(self, path, **fields):
        page = dict(old=path, new=path, label='Docs', up='README.md', up_label='Root')
        self.config['snode.c']['pages'].append(page | fields)

    def test_clean_root_and_untracked_files(self):
        self.write('docs/untracked.md', '[missing](no.md)', tracked=False)
        self.assertEqual(self.audit(), [])

    def test_existing_untracked_target_is_still_broken(self):
        self.write('README.md', '[![button](button.svg)](src/page.md)')
        self.write('button.svg', '<svg/>', tracked=False)
        self.write('src/page.md', '# Page', tracked=False)
        errors = self.audit()
        self.assertEqual(sum('broken-link' in error for error in errors), 2)

    def test_all_violations_collected_deterministically_without_writes(self):
        self.write('README.md', '# Root\n[planned](docs/README.md#absent)\n[missing](missing.md)\n![missing](img.svg)\n')
        self.write('docs/README.md', '# Docs\n')
        self.declare('docs/README.md')
        self.config['snode.c']['sections']['docs'] = 'Docs'
        self.write('docs/unknown.md', '# Unknown\n')
        before = self.git('diff', '--cached')
        errors = self.audit()
        self.assertEqual(errors, sorted(errors))
        for kind in ['unplanned-page', 'unreachable-page', 'broken-link', 'missing-anchor', 'missing-generated-block']:
            self.assertTrue(any(kind in error for error in errors), kind)
        self.assertEqual(errors, self.audit())
        self.assertEqual(before, self.git('diff', '--cached'))
        self.assertTrue(any('section-pages' in error for error in errors))

    def test_reachable_but_unplanned_page_is_not_hidden(self):
        self.write('README.md', '[notes](docs/notes.md)')
        self.write('docs/notes.md', '# Notes')
        self.assertEqual(self.audit(), ['docs/notes.md: unplanned-page: not declared in navigation/plan.yml'])

    def test_unreachable_root_and_source_notes(self):
        self.write('AGENTS.md', '# Instructions')
        self.write('src/README.md', '# Source')
        errors = self.audit()
        self.assertEqual(len(errors), 2)
        self.assertTrue(all('unreachable-page' in error for error in errors))
        self.write('README.md', '[agents](AGENTS.md)\n[source](src/README.md)')
        self.assertEqual(self.audit(), [])

    def test_graph_cycles_do_not_make_pages_reachable(self):
        self.write('src/a.md', '[b](b.md)')
        self.write('src/b.md', '[a](a.md)')
        self.assertEqual(len(self.audit()), 2)
        self.write('README.md', '[a](src/a.md)')
        self.assertEqual(self.audit(), [])

    def test_same_repo_blob_tree_and_slash_branch(self):
        self.write('README.md', '[notes](https://github.com/SNodeC/snode.c/blob/feature/nested/src/note.md#héllo-world)\n[folder](https://github.com/SNodeC/snode.c/tree/master/extra)')
        self.write('src/note.md', '# Héllo World')
        self.write('extra/note.md', '# Extra')
        self.assertEqual(self.audit(), [])

    def test_remote_slash_branch_root_links_resolve_to_readme(self):
        self.git('config', 'user.name', 'Audit fixture')
        self.git('config', 'user.email', 'audit@example.invalid')
        self.git('-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture')
        self.git('update-ref', 'refs/remotes/origin/review/nested/branch', 'HEAD')
        self.write('README.md', '[review](https://github.com/SNodeC/snode.c/tree/review/nested/branch)')
        self.assertEqual(self.audit(), [])
        self.write('README.md', '[missing](https://github.com/SNodeC/snode.c/tree/review/nested/branch/missing)')
        self.assertTrue(any('broken-link' in e for e in self.audit()))

    def test_published_targets_do_not_exempt_authored_source_pages(self):
        self.git('remote', 'set-url', 'origin', 'git@github.com:SNodeC/DistributionPackages.git')
        self.config = {'DistributionPackages': {'pages': [], 'sections': {}, 'exempt': [
            {'path': 'site/status/**', 'reason': 'Resolves in published Packages.'},
            {'path': 'site/fedora/**', 'reason': 'Resolves in published Packages.'}]}}
        self.write('README.md', '[output](site/status/project.md#page-overview)\n[feed](site/fedora/)\n[bad](site/docs/missing.md)')
        self.write('site/status/authored.md', '[broken](../docs/absent.md)')
        errors = self.audit()
        self.assertFalse(any('project.md' in e for e in errors))
        self.assertTrue(any('site/docs/missing.md' in e for e in errors))
        self.assertTrue(any('site/status/authored.md: unreachable-page' in e for e in errors))
        self.assertTrue(any('site/status/authored.md: broken-link' in e for e in errors))
        for name, path in [('snode.c', 'site/status/**'), ('DistributionPackages', 'docs/status/**'), ('DistributionPackages', 'site/**'), ('DistributionPackages', 'site/docs/**')]:
            with self.subTest(name=name, path=path):
                with self.assertRaises(ValueError):
                    validate_plan({name: {'pages': [], 'sections': {}, 'exempt': [
                        {'path': path, 'reason': 'Resolves in published Packages.'}]}})

    def test_commit_pinned_and_other_repository_links_are_not_head_checks(self):
        self.write('README.md', '[historic](https://github.com/SNodeC/snode.c/blob/'+'a'*40+'/gone.md#old)\n[other](https://github.com/SNodeC/mqttsuite/blob/master/elsewhere.md#unknown)')
        self.assertEqual(self.audit(), [])
        self.write('README.md', '[bad](https://github.com/SNodeC/mqttsuite/blob/master)')
        self.assertTrue(any('malformed SNodeC URL' in e for e in self.audit()))

    def test_html_picture_reference_links_and_escaped_paths(self):
        self.write('README.md', '<a href="src/note.md#named">Read</a><picture><source srcset="a.svg, b.svg 2x"><img src="a.svg"></picture>\n![note][note]\n[note]: src/note.md#named "Title"\n[space](src/space%20name.md)\n[paren](src/a(b).md)')
        self.write('src/note.md', '<a name="named"></a>\n# Note')
        self.write('src/space name.md', '# Space')
        self.write('src/a(b).md', '# Parentheses')
        for path in ['a.svg', 'b.svg']:
            self.write(path, '<svg/>')
        self.assertEqual(self.audit(), [])

    def test_nested_list_navigation_is_not_indented_code(self):
        self.write('README.md', '- A group\n    [child](src/child.md)\n\n    - Nested group\n        [second](src/second.md)\n\n          [code example](not-tracked.md)')
        self.write('src/child.md', '# Child')
        self.write('src/second.md', '# Second')
        self.assertEqual(self.audit(), [])

    def test_code_and_comments_are_not_navigation(self):
        self.write('README.md', '# Root\n`[link](gone.md)`\n<!-- [link](gone.md) -->\n```md\n[link](gone.md)\n```\n~~~md\n[link](gone.md)\n~~~\n    [link](gone.md)')
        self.assertEqual(self.audit(), [])

    def test_github_slugs_duplicate_unicode_setext_and_explicit_ids(self):
        _, anchors = _document('# Hello, world!\n## Hello, world!\n## hello-world-1\n## `CMake` & **SDK**\n## 日本語\nSetext title\n===\n<a id="specific"></a>')
        self.assertTrue({'hello-world', 'hello-world-1', 'hello-world-1-1', 'cmake--sdk', '日本語', 'setext-title', 'specific'} <= anchors)

    def test_heading_reference_links_and_underscore_emphasis(self):
        _, anchors = _document('# _Italic_ and __bold__ with snake_case [API][reference]\n[reference]: https://example.invalid')
        self.assertIn('italic-and-bold-with-snake_case-api', anchors)
        self.write('README.md', '<pre>[not a link](missing.md)</pre>\n<code>[not a link](missing.md)</code>')
        self.assertEqual(self.audit(), [])

    def test_fragment_links_and_query_strings(self):
        self.write('README.md', '# Root\n[ok](#root)\n[asset](file.txt?raw=true)\n[bad](#missing)')
        self.write('file.txt', 'text')
        self.assertEqual(self.audit(), ['README.md: missing-anchor: #missing (target README.md)'])

    def test_exemptions_are_narrow_and_do_not_hide_agent_notes(self):
        self.config['snode.c']['exempt'] = [{'path': 'vendor/**', 'reason': 'Vendored third-party library.'}, {'path': 'tests/generated/**', 'reason': 'Generated test fixture Markdown.'}]
        for p in ['vendor/README.md', 'tests/generated/page.md', 'node_modules/lib/README.md', '.github/PULL_REQUEST_TEMPLATE.md']:
            self.write(p, '[bad](gone.md)')
        self.write('AGENTS.md', '# Agents')
        self.assertEqual(self.audit(), ['AGENTS.md: unreachable-page: no route from README.md'])
        for entry in [{'path': '**', 'reason': 'Asset notes'}, {'path': '../outside', 'reason': 'Vendored dependency'}, {'path': 'vendor/**', 'reason': 'Vendored\nsecond line'}]:
            with self.subTest(entry=entry):
                bad = copy.deepcopy(self.config)
                bad['snode.c']['exempt'] = [entry]
                with self.assertRaises(ValueError):
                    validate_plan(bad)

    def test_excluded_asset_note_is_still_audited_and_must_be_reachable(self):
        self.write('docs/media/README.md', '# Media')
        self.declare('docs/media/README.md', excluded=True)
        self.assertEqual(self.audit(), ['docs/media/README.md: unreachable-page: no route from README.md'])

    def test_unenrolled_repository_keeps_graph_checks_without_page_planning(self):
        self.git('remote', 'set-url', 'origin', 'git@github.com:SNodeC/AutoTalk.git')
        self.write('README.md', '[guide](docs/USER_GUIDE.md)')
        self.write('docs/USER_GUIDE.md', '# Guide')
        self.assertEqual(self.audit(), [])
        self.write('docs/unlinked.md', '[broken](absent.md)')
        errors = self.audit()
        self.assertTrue(any('broken-link' in e for e in errors))
        self.assertTrue(any('unreachable-page' in e for e in errors))
        self.assertFalse(any('unplanned-page' in e for e in errors))

    def test_all_requested_unplanned_roots(self):
        for p in ['docs/a.md', 'status/a.md', 'keys/a.md', 'web/a.md', 'packages/sdk/a.md']:
            self.write(p, '# Page')
        self.assertEqual(sum('unplanned-page' in e for e in self.audit()), 5)

    def test_missing_planned_page_and_partial_blocks(self):
        self.declare('docs/missing.md')
        self.write('docs/incomplete.md', '<!-- snodec:begin page-header -->\n# Incomplete')
        self.declare('docs/incomplete.md')
        self.assertEqual(sum('missing-generated-block' in e for e in self.audit()), 2)

    def test_cli_requires_repo_and_exit_status(self):
        self.git('remote', 'set-url', 'origin', 'git@github.com:SNodeC/AutoTalk.git')
        python = __import__('sys').executable
        for args in [[], ['--repo', str(self.repo)]]:
            result = subprocess.run([python, str(ROOT / 'tools/snodec_sync'), 'docs-audit', *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1 if not args else 0)
        self.write('src/bad.md', '# Unreachable')
        result = subprocess.run([python, str(ROOT / 'tools/snodec_sync'), 'docs-audit', '--repo', str(self.repo)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('unreachable-page', (result.stdout + result.stderr))

    def test_distribution_source_and_site_have_separate_policies(self):
        self.git('remote', 'set-url', 'origin', 'git@github.com:SNodeC/DistributionPackages.git')
        self.assertEqual(_config(self.repo)[0], 'DistributionPackages')
        site = self.repo / 'site'
        site.mkdir()
        self.assertEqual(_config(site)[0], 'Packages')
        self.assertIn('DistributionPackages', _banner('DistributionPackages', 'DistributionPackages', 'Documentation', '#ffffff'))


    def test_image_buttons_are_allowed_only_inside_navigation_blocks(self):
        self.write('docs/menu/go.svg', '<svg/>')
        self.write('README.md', '# Root\n[![Go](docs/menu/go.svg)](#root)\n')
        self.assertTrue(any('button-outside-navigation' in e for e in self.audit()))
        self.write('README.md', '# Root\n<!-- snodec:begin menu -->\n[![Go](docs/menu/go.svg)](#root)\n<!-- snodec:end menu -->\n')
        self.assertEqual(self.audit(), [])

    def test_parent_requires_downward_link(self):
        self.declare('docs/page.md')
        self.write('docs/page.md', '<!-- snodec:begin page-header -->\n<a id="page-overview"></a>\n<!-- snodec:end page-header -->\n# Page\n')
        self.assertTrue(any('missing-backlink' in e for e in self.audit()))
        self.write('README.md', '# Root\n[Page](docs/page.md#page-overview)\n')
        self.assertEqual(self.audit(), [])

    def test_page_size_information_and_violation(self):
        self.write('README.md', '# Root\n' + 'x' * (101 * 1024))
        self.plan.write_text(yaml.safe_dump(self.config))
        info = []
        self.assertEqual(docs_audit(self.repo, self.plan, info), [])
        self.assertEqual(len(info), 1)
        self.write('README.md', '# Root\n' + 'x' * (301 * 1024))
        self.assertTrue(any('page-too-large' in e for e in self.audit()))

    def test_section_list_opt_out_uses_existing_project_table(self):
        self.config['snode.c']['sections']['docs'] = 'Docs'
        self.declare('docs/README.md', section_list=False)
        self.write('README.md', '# Root\n[Index](docs/README.md#page-overview)\n')
        self.write('docs/README.md', '<!-- snodec:begin page-header -->\n<a id="page-overview"></a>\n<!-- snodec:end page-header -->\n# Index\n')
        self.assertEqual(self.audit(), [])
