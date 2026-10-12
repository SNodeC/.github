"""Read-only audit of tracked Markdown, navigation coverage and local link graphs."""
import fnmatch
import html
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import unicodedata
from urllib.parse import unquote, urlsplit

import yaml

from .navigation import ROOT, validate_plan


def _git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout.decode('utf-8', errors='surrogateescape')


def _without_code(text):
    lines, fence, list_indent = [], None, None
    for line in text.splitlines():
        indent = len(line) - len(line.lstrip(' '))
        bullet = re.match(r'^ *(?:[-+*]|[0-9]+[.)]) +', line)
        if not fence and bullet and (indent <= 3 or list_indent is not None and indent < list_indent + 4):
            list_indent = bullet.end()
        elif not fence and line.strip() and indent == 0:
            list_indent = None
        content = line[list_indent:] if list_indent is not None and indent >= list_indent else line
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', content)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            lines.append('')
        elif marker:
            fence = marker[1]
            lines.append('')
        else:
            lines.append('' if content.startswith(('    ', '\t')) else content)
    return '\n'.join(lines)


class _Markup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.ids.update(attrs[k] for k in ('id',) if attrs.get(k))
        if tag == 'a' and attrs.get('name'):
            self.ids.add(attrs['name'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])
        if attrs.get('srcset'):
            self.links.extend(item.strip().split()[0] for item in attrs['srcset'].split(',') if item.strip())


def _label(text):
    return ' '.join(text.split()).casefold()


def _document(text):
    text = _without_code(text)
    # Code spans and comments are not links or HTML anchors.
    headings = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'(`+)(?:(?!\1).)*?\1|<(pre|code)\b[^>]*>.*?</\2>', '', headings, flags=re.S)
    markup = _Markup()
    markup.feed(text)
    definitions = {}
    for match in re.finditer(r'^ {0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)', text, re.M):
        definitions[_label(match[1])] = match[2].strip('<>')
    body = re.sub(r'^ {0,3}\[[^\]]+\]:.*$', '', text, flags=re.M)
    links = list(markup.links)
    # Inspect destinations rather than labels: nested linked images yield both URLs.
    for match in re.finditer(r'\]\(\s*(<[^>]+>|(?:\\.|[^\s()]|\([^()]*\))+)(?:\s+[\"\'][^\n]*?[\"\'])?\s*\)', body):
        links.append(match[1].strip('<>'))
    for match in re.finditer(r'!?\[([^\]\n]+)\](?:\[([^\]\n]*)\])?', body):
        target = definitions.get(_label(match[2] or match[1]))
        if target:
            links.append(target)
    links.extend(re.findall(r'<(https?://[^<>\s]+)>', body))
    anchors, used = set(markup.ids), set()
    lines = headings.splitlines()
    for index, line in enumerate(lines):
        heading = re.match(r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+\s*)?$', line)
        value = heading[1] if heading else None
        if value is None and index + 1 < len(lines) and line.strip() and re.match(r'^ {0,3}(?:=+|-+)\s*$', lines[index + 1]):
            value = line.strip()
        if value is None:
            continue
        value = re.sub(r'!?\[([^\]]*)\](?:\([^)]*\)|\[[^\]]*\])', r'\1', value)
        value = html.unescape(re.sub(r'<[^>]+>', '', value)).lower()
        value = re.sub(r'\\([!"#$%&\'()*+,\-./:;<=>?@\[\]^_`{|}~])', r'\1', value)
        value = re.sub(r'(?<!\w)_{1,2}(.+?)_{1,2}(?!\w)', r'\1', value)
        value = re.sub(r'[*`~]', '', value)
        slug = ''.join(c for c in value if c in '-_' or c.isspace() or unicodedata.category(c)[0] in 'LMN').replace(' ', '-')
        candidate, counter = slug, 0
        while candidate in used:
            counter += 1
            candidate = f'{slug}-{counter}'
        used.add(candidate)
        anchors.add(candidate)
    return sorted(set(links)), anchors


def docs_audit(repo, plan_path=None, information=None):
    """Return every violation in deterministic order. Never change the checkout."""
    repo = Path(repo).resolve()
    top = Path(_git(repo, 'rev-parse', '--show-toplevel').strip()).resolve()
    if top != repo:
        raise ValueError('docs-audit requires a repository root, not a subtree')
    tracked = set(_git(repo, 'ls-files', '-z').rstrip('\0').split('\0')) - {''}
    remote = _git(repo, 'remote', 'get-url', 'origin').strip()
    match = re.search(r'(?:github\.com[:/])SNodeC/([^/]+?)(?:\.git)?$', remote)
    if not match:
        raise ValueError('docs-audit requires an SNodeC origin remote')
    name = match[1]
    plan = yaml.safe_load(Path(plan_path or ROOT / 'navigation/plan.yml').read_text())
    validate_plan(plan)
    config = plan.get(name, {'pages': [], 'sections': {}})
    exemptions = [entry['path'] for entry in config.get('exempt', []) if not entry['reason'].lower().startswith('resolves in published packages')]
    refs = set(_git(repo, 'for-each-ref', '--format=%(refname:strip=3)', 'refs/remotes').splitlines())
    excluded = lambda path: '.github' in PurePosixPath(path).parts or 'node_modules' in PurePosixPath(path).parts or any(fnmatch.fnmatchcase(path, glob) for glob in exemptions)
    markdown = sorted(p for p in tracked if p.lower().endswith('.md') and not excluded(p))
    documents = {p: _document((repo / p).read_text()) for p in markdown}
    pages = {p['new']: p for p in config['pages'] if not p.get('deleted')}
    errors, graph = set(), {p: set() for p in markdown}

    def report(kind, path, detail):
        errors.add(f'{path}: {kind}: {detail}')

    def resolve(source, href):
        href = html.unescape(re.sub(r'\\([() ])', r'\1', href))
        url = urlsplit(href)
        if url.scheme or url.netloc:
            if url.netloc.lower() not in ('github.com', 'www.github.com'):
                return None
            parts = url.path.strip('/').split('/')
            if not parts or parts[0] != 'SNodeC' or len(parts) < 2:
                return None
            if len(parts) >= 3 and parts[2] in ('blob', 'tree'):
                if len(parts) < 4 or not parts[3] or parts[2] == 'blob' and len(parts) < 5:
                    report('broken-link', source, f'malformed SNodeC URL {href}')
                    return None
                if parts[1] != name or re.fullmatch(r'[0-9a-fA-F]{40}', parts[3]):
                    return None
                # A branch name can contain slashes: prefer the longest tracked suffix.
                candidates = [unquote('/'.join(parts[i:])) for i in range(4, len(parts))] or ['README.md']
                target = 'README.md' if parts[2] == 'tree' and '/'.join(parts[3:]) in refs else next((p for p in candidates if p in tracked or any(t.startswith(p + '/') for t in tracked)), candidates[0])
            elif parts[1] == name and len(parts) == 2:
                target = 'README.md'
            else:
                return None
        else:
            target = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(url.path))) if url.path else source
            if url.path.startswith('/'):
                target = unquote(url.path).lstrip('/')
        if target not in tracked:
            children = [p for p in tracked if p.startswith(target.rstrip('/') + '/')]
            if children:
                # A directory view exposes its tracked documents and subdirectories.
                graph[source].update(p for p in markdown if p in children)
                target = target.rstrip('/') + '/README.md'
                if target not in tracked and not url.fragment:
                    return None
            else:
                if any(entry['reason'].lower().startswith('resolves in published packages') and (fnmatch.fnmatchcase(target, entry['path']) or fnmatch.fnmatchcase(target + '/', entry['path'])) for entry in config.get('exempt', [])):
                    return None
                report('broken-link', source, href)
                return None
        fragment = unquote(url.fragment)
        if fragment and target in documents and fragment not in documents[target][1]:
            report('missing-anchor', source, f'{href} (target {target})')
        return target

    for path in markdown:
        parts = PurePosixPath(path).parts
        in_scope = parts[0] in ('docs', 'status', 'keys', 'web') or (parts[0] == 'packages' and len(parts) >= 3)
        if name in plan and in_scope and path not in pages:
            report('unplanned-page', path, 'not declared in navigation/plan.yml')
        for href in documents[path][0]:
            target = resolve(path, href)
            if target in graph:
                graph[path].add(target)
    for path, page in sorted(pages.items()):
        if page.get('excluded'):
            continue
        if path not in tracked:
            report('missing-generated-block', path, 'planned page is not tracked')
            continue
        text = _without_code((repo / path).read_text())
        if not re.search(r'<!-- snodec:begin page-header -->.*?<!-- snodec:end page-header -->', text, re.S):
            report('missing-generated-block', path, 'page-header')
        if path.endswith('/README.md') and posixpath.dirname(path) in config['sections'] and page.get('section_list', True) and not re.search(r'<!-- snodec:begin section-pages -->.*?<!-- snodec:end section-pages -->', text, re.S):
            report('missing-generated-block', path, 'section-pages')
    # Optional review rules: none of these are imported by Verify or publication.
    for path in markdown:
        text = _without_code((repo / path).read_text())
        allowed = [(m.start(), m.end()) for m in re.finditer(
            r'<!-- snodec:begin (page-header|organization|menu) -->.*?<!-- snodec:end \1 -->', text, re.S)]
        buttons = re.finditer(r'<a\b[^>]*>\s*(?:<picture>.*?)?<img\b[^>]*src="[^"\n]*(?:menu|nav)/[^"\n]+"[^>]*>.*?</a>|\[!\[[^\]]*\]\([^)]*(?:menu|nav)/[^)]+\)\]\([^)]+\)', text, re.S)
        for button in buttons:
            if not any(start <= button.start() < end for start, end in allowed):
                report('button-outside-navigation', path, f'line {text.count(chr(10), 0, button.start()) + 1}')
        page = pages.get(path)
        if page and not page.get('excluded') and page['up'] in graph and path not in graph[page['up']]:
            report('missing-backlink', path, f"parent {page['up']} does not link down to this page")
        size = (repo / path).stat().st_size
        if size > 300 * 1024:
            report('page-too-large', path, f'{size} bytes exceeds 300 KB')
        elif size > 100 * 1024 and information is not None:
            information.append(f'{path}: information: {size} bytes exceeds 100 KB')
    reachable, queue = set(), ['README.md']
    while queue:
        path = queue.pop()
        if path not in reachable:
            reachable.add(path)
            queue.extend(graph.get(path, set()) - reachable)
    for path in markdown:
        if path not in reachable:
            report('unreachable-page', path, 'no route from README.md')
    return sorted(errors)
