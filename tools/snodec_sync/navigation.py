"""Offline navigation rendering; no moves, network, CI or publication side effects."""
import html
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[2]
NS = '{http://www.w3.org/2000/svg}'
FONT = '-apple-system, &quot;Segoe UI&quot;, &quot;Noto Sans&quot;, Helvetica, Arial, sans-serif'
ARROW = 'M0 1.25H5.5V0L9 2L5.5 4V2.75H0Z'
ET.register_namespace('', NS[1:-1])


def slug(label):
    return re.sub('[^a-z0-9]+', '-', label.lower()).strip('-')


def validate_plan(plan):
    """Validate all declared chains, not just the requested checkout."""
    for name, config in plan.items():
        if name == 'menu_labels':
            if not isinstance(config, dict) or any(not isinstance(k, str) or not isinstance(v, str) or not v.strip() for k, v in config.items()):
                raise ValueError('menu_labels requires nonempty text labels')
            continue
        for entry in config.get('exempt', []):
            if (not isinstance(entry, dict) or set(entry) != {'path', 'reason'}
                    or not isinstance(entry['path'], str) or not entry['path']
                    or PurePosixPath(entry['path']).is_absolute() or '..' in PurePosixPath(entry['path']).parts
                    or not isinstance(entry['reason'], str) or '\n' in entry['reason'] or '\r' in entry['reason']
                    or not entry['reason'].lower().startswith(('vendored', 'third-party', 'generated test fixture', 'resolves in published packages'))):
                raise ValueError(f'{name}: exempt requires a safe path glob and approved one-line reason')
            if entry['reason'].lower().startswith('resolves in published packages') and (name != 'DistributionPackages' or not entry['path'].startswith('site/') or len(PurePosixPath(entry['path']).parts) < 3 or PurePosixPath(entry['path']).parts[1] == 'docs'):
                raise ValueError('Published-output exemptions are limited to DistributionPackages/site targets')
        active = {}
        for page in config['pages']:
            for field in ('old', 'new', 'up'):
                path = page[field]
                if path is not None and (PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts):
                    raise ValueError(f'{name}: unsafe {field}: {path}')
            if len(page['up_label']) > 15 or not page['up_label'].strip():
                raise ValueError(f'{name}: Up label exceeds 15 characters: {page["up_label"]}')
            if 'section_list' in page and type(page['section_list']) is not bool:
                raise ValueError(f'{name}: section_list must be boolean')
            if page.get('deleted'):
                continue
            if page['new'] in active:
                raise ValueError(f'{name}: duplicate target: {page["new"]}')
            active[page['new']] = page
        for path in active:
            seen = set()
            while path != 'README.md':
                if path in seen or path not in active:
                    raise ValueError(f'{name}: invalid Up chain at {path}')
                seen.add(path)
                path = active[path]['up']
        for change in config.get('menu_changes', []):
            if any(p not in active for p in change['pages']):
                raise ValueError(f'{name}: menu change references an undeclared page')


def _config(repo):
    plan = yaml.safe_load((ROOT / 'navigation/plan.yml').read_text())
    validate_plan(plan)
    menu_labels = plan.pop('menu_labels', {})
    name = str(repo)
    if name not in plan and name != '.github':
        checkout = Path(repo).resolve()
        result = subprocess.run(['git', '-C', str(checkout), 'remote', 'get-url', 'origin'],
                                capture_output=True, text=True)
        match = re.search(r'SNodeC/([^/]+?)(?:\.git)?\s*$', result.stdout)
        name = match[1] if match else checkout.name
        name = next((key for key, value in plan.items()
                     if '/' in value['source'] and value['source'].split('/')[0] == name
                     and checkout.name == value['source'].split('/')[-1]), name)
    if name in ('.github', 'SNode.C-Book-Companion'):
        config = {'display': 'SNodeC' if name == '.github' else 'SNode.C Book Companion', 'pages': [], 'sections': {}}
    elif name in plan:
        config = plan[name]
    else:
        raise ValueError(f'Checkout is not in navigation/plan.yml: {repo}')
    catalog = yaml.safe_load((ROOT / 'catalog.yml').read_text())
    entry = next(e for e in catalog if e['name'] == name)
    tokens = yaml.safe_load((ROOT / 'brand/tokens.yml').read_text())
    accent = entry.get('accent', tokens['area_accents'][entry['area']])
    return name, config | {'menu_labels': menu_labels}, tokens['accents'][accent], tokens['accents']['foundation-blue']


def _page(config, page_path):
    for page in config['pages']:
        if page['new'] == page_path and not page.get('deleted'):
            if page.get('excluded'):
                raise ValueError(f'Excluded page has no header: {page_path}')
            return page
    # New PROJECTS-driven status pages inherit the single declared sibling policy.
    # No project list or second navigation registry is introduced here.
    parent = posixpath.dirname(page_path)
    siblings = [p for p in config['pages'] if p['title'] == '(generated)'
                and posixpath.dirname(p['new']) == parent
                and p['label'] == config['sections'].get(parent)]
    policies = {(p['label'], p['up'], p['up_label']) for p in siblings
                if p['up'] == posixpath.join(parent, 'README.md')}
    if len(policies) == 1 and page_path.endswith('.md') and '..' not in PurePosixPath(page_path).parts:
        label, up, up_label = policies.pop()
        return {'new': page_path, 'label': label, 'up': up, 'up_label': up_label}
    raise ValueError(f'No navigation policy for page: {page_path}')


def _relative(target, page_path):
    return posixpath.relpath(target, posixpath.dirname(page_path) or '.')


def _button(nav, stem, title, href, right=False, mobile=False):
    escape = lambda text: html.escape(text, quote=True)
    compact = (f'<source media="(max-width: 640px) and (prefers-color-scheme: dark)" srcset="{nav}/{stem}-icon-dark.svg">'
               f'<source media="(max-width: 640px)" srcset="{nav}/{stem}-icon-light.svg">') if mobile else ''
    size = '' if mobile else ' width="160" height="28"'
    return (f'<a href="{escape(href)}" title="{escape(title)}"><picture>{compact}'
            f'<source media="(prefers-color-scheme: dark)" srcset="{nav}/{stem}-dark.svg">'
            f'<img {"align=\"right\" " if right else ""}src="{nav}/{stem}-light.svg" '
            f'alt="{escape(title)}" title="{escape(title)}"{size}></picture></a>')


def _organization():
    return ('<!-- snodec:begin organization -->\n<p>' +
            _button('docs/media/nav', 'organization', 'SNodeC organization',
                    'https://github.com/SNodeC', True) +
            '<br clear="all"></p>\n<!-- snodec:end organization -->')


def _header(config, page_path):
    page = _page(config, page_path)
    display = config['display']
    nav = _relative('docs/media/nav', page_path)
    escape = lambda text: html.escape(text, quote=True)
    up_fragment = 'project-overview' if page['up'] == 'README.md' else 'page-overview'
    buttons = [_button(nav, 'up-' + slug(page['up_label']), 'Up to ' + page['up_label'],
                      _relative(page['up'], page_path) + '#' + up_fragment),
               _button(nav, 'organization', 'SNodeC organization', 'https://github.com/SNodeC', True, True),
               _button(nav, 'repository', display + ' repository',
                      _relative('README.md', page_path) + '#project-overview', True, True)]
    return ('<!-- snodec:begin page-header -->\n<a id="page-overview"></a>\n'
            f'<p><picture><source media="(max-width: 640px)" '
            f'srcset="{nav}/banner-{slug(page["label"])}-compact.svg">'
            f'<img src="{nav}/banner-{slug(page["label"])}.svg" '
            f'alt="{escape(display + " — " + page["label"])}" width="100%"></picture></p>\n'
            '<p>' + ''.join(buttons) + '<br clear="all"></p>\n<!-- snodec:end page-header -->')


def render_header(repo, page_path):
    """Render one post-move page header, including dynamically generated status pages.

    repo is a catalog name or checkout path (DistributionPackages/site for Packages).
    It performs no writes. Import from tools.snodec_sync or snodec_sync.
    """
    return _header(_config(repo)[1], str(page_path))


def _svg(width, height, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(label, quote=True)}">'
            f'<title>{html.escape(label)}</title>{body}</svg>\n')


def _header_button(label, title, icon, color, theme, width=160):
    fill, stroke, text = (('#f6f8fa', '#d0d7de', '#1f2328') if theme == 'light'
                          else ('#161b22', '#3d444d', '#e6edf3'))
    original = ET.parse(ROOT / f'brand/navigation/octicons/{icon}.svg').getroot()
    notice = (ROOT / 'brand/navigation/octicons/NOTICE.md').read_text().split('```text\n')[1].split('```')[0]
    shapes = ''.join(ET.tostring(x, encoding='unicode') for x in original if x.tag != NS + 'title')
    return _svg(width, 28, title,
                '<!-- ' + notice + ' -->'
                f'<rect x=".5" y=".5" width="{width-1}" height="27" rx="5" fill="{fill}" stroke="{stroke}"/>'
                f'<g transform="translate({(width-16)/2 if width == 36 else 13:g} 6)" fill="{color}">{shapes}</g>' +
                (f'<text x="38" y="19" font-family="{FONT}" font-size="15" font-weight="600" '
                 f'fill="{text}">{html.escape(label)}</text>' if width != 36 else ''))


def _banner(name, display, label, color, compact=False):
    mark = ET.parse(ROOT / f'brand/navigation/marks/{"Packages" if name == "DistributionPackages" else name}.svg').getroot()
    x, y, width, height = map(float, mark.attrib['viewBox'].split())
    scale = 44 / height
    graphic = ''.join(ET.tostring(child, encoding='unicode') for child in mark)
    canvas_width, canvas_height = (480, 72) if compact else (1280, 56)
    transform = f'translate(46 {canvas_height // 2}) scale({scale:.8f}) translate({-x-width/2:g} {-y-height/2:g})'
    return _svg(canvas_width, canvas_height, display + ' — ' + label,
                '<defs><linearGradient id="background" x2="1" y2="1">'
                '<stop stop-color="#101f35"/><stop offset="1" stop-color="#172f47"/>'
                f'</linearGradient><clipPath id="rounded"><rect width="{canvas_width}" height="{canvas_height}" rx="10"/>'
                '</clipPath></defs><g clip-path="url(#rounded)">'
                f'<rect width="{canvas_width}" height="{canvas_height}" fill="url(#background)"/>'
                f'<rect width="8" height="{canvas_height}" fill="{color}"/></g><g transform="{transform}">{graphic}</g>'
                f'<text x="84" y="{32 if compact else 37}" font-family="{FONT}" font-size="25" '
                f'font-weight="700" fill="#ffffff">{html.escape(display)}</text>'
                f'<text x="{84 if compact else 1244}" y="{58 if compact else 37}" text-anchor="{"start" if compact else "end"}" font-family="{FONT}" '
                f'font-size="23" font-weight="600" fill="{color}">{html.escape(label)}</text>')


def _menu_svg(label, width, arrow='', title=None):
    center = width / 2 - (8 if arrow else 0)
    shape = (f'<path d="{ARROW}" fill="#ffffff" aria-hidden="true" '
             f'transform="translate({width - 17} 12){" rotate(-90 4.5 2)" if arrow == "up" else ""}"/>') if arrow else ''
    return _svg(width, 28, title or label,
                f'<rect x=".5" y=".5" width="{width-1}" height="27" rx="5" fill="#203440" stroke="#395260"/>'
                f'<text x="{center:g}" y="19" text-anchor="middle" font-family="{FONT}" font-size="15" '
                f'font-weight="600" fill="#ffffff">{html.escape(label)}</text>{shape}')


def _strip_header(text):
    pattern = r'<!-- snodec:begin page-header -->.*?<!-- snodec:end page-header -->\s*'
    if 'snodec:begin page-header' in text and not re.search(pattern, text, re.S):
        raise ValueError('Unclosed page-header block')
    text = re.sub(pattern, '', text, flags=re.S)
    # Pre-marker package pages: remove only their old identity banner/overview anchor.
    title = re.search(r'^# ', text, re.M)
    if not title:
        raise ValueError('Page requires an H1')
    prefix, body = text[:title.start()], text[title.start():]
    prefix = re.sub(r'^.*page-banner\.svg.*\n', '', prefix, flags=re.M)
    prefix = re.sub(r'<a id="page-overview"></a>\s*', '', prefix)
    return prefix.rstrip(), body


def _section_list(config, path, texts):
    if not _page(config, path).get('section_list', True):
        return ''
    entries = []
    for page in config['pages']:
        if page.get('deleted') or page.get('excluded') or page['up'] != path or page['new'] not in texts:
            continue
        title = re.search(r'^# (.+)$', texts[page['new']], re.M)[1]
        entries.append(f'- [{title}]({_relative(page["new"], path)}#page-overview)')
    return '<!-- snodec:begin section-pages -->\n' + '\n'.join(entries) + '\n<!-- snodec:end section-pages -->'


def _up_link(src, href, path, ancestors):
    target, _, fragment = href.partition('#')
    target = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
    return PurePosixPath(src).name.startswith('back-') or (
        target in ancestors and fragment in ('', 'page-overview', 'project-overview', 'readme'))


def _menus(checkout, config, texts, outputs):
    declared = {p['new']: p for p in config['pages'] if not p.get('deleted')}
    for path, original in list(texts.items()):
        ancestors, parent = set(), path
        while parent in declared:
            parent = declared[parent]['up']
            ancestors.add(parent)
            if parent == 'README.md':
                break
        def anchor(match):
            tag = match[0]
            image = re.search(r'<img\b[^>]*src="([^"]+)"[^>]*>', tag)
            if not image:
                return tag
            href = re.search(r'href="([^"]+)"', tag)[1]
            if _up_link(image[1], href, path, ancestors):
                return ''
            return tag
        text = re.sub(r'<a\b[^>]*href="[^"]+"[^>]*>\s*<img\b[^>]*>\s*</a>', anchor, original)
        # Markdown image uplinks are likewise buttons, not ordinary prose references.
        text = re.sub(r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)',
                      lambda m: '' if _up_link(m[2], m[3], path, ancestors) else m[0], text)
        for src in re.findall(r'(?:src="|!\[[^\]]*\]\()([^"\s)]+\.svg)', text):
            if src.startswith(('https:', 'http:', '/')):
                continue
            asset = posixpath.normpath(posixpath.join(posixpath.dirname(path), src))
            if '..' in PurePosixPath(asset).parts or not (checkout / asset).is_file():
                continue
            svg = ET.parse(checkout / asset).getroot()
            if svg.attrib.get('height') != '28' or 'nav' in PurePosixPath(asset).parts:
                continue
            label_node = svg.find('.//' + NS + 'text')
            if label_node is None:
                continue
            label = ''.join(label_node.itertext())
            title_node = svg.find(NS + 'title')
            title = title_node.text if title_node is not None else label
            remove = False
            for change in config.get('menu_changes', []):
                if path not in change['pages']:
                    continue
                image_pattern = re.escape(src)
                # Apply changes to the selected link, not unrelated same-label buttons.
                if change['label'] == label and (not change.get('target') or
                   re.search(r'href="' + re.escape(change['target']) + r'"[^>]*>[^<]*<img[^>]*src="' + image_pattern, text)):
                    if change.get('remove'):
                        text = re.sub(r'<a\b[^>]*>\s*<img\b[^>]*src="' + image_pattern + r'"[^>]*>\s*</a>', '', text)
                        remove = True
                    else:
                        replacement = change['replacement']
                        # Different semantics must not rewrite a shared root Install asset.
                        new_asset = str(PurePosixPath(asset).with_name('menu-' + slug(replacement) + '.svg'))
                        new_src = _relative(new_asset, path)
                        text = text.replace(f'src="{src}"', f'src="{new_src}"')
                        text = text.replace(f'alt="{label}"', f'alt="{replacement}"').replace(f'title="{label}"', f'title="{replacement}"')
                        asset, src, label, title = new_asset, new_src, replacement, replacement
            if remove:
                continue
            width = 160
            arrow = next(('up' if any('rotate(-90' in n.attrib.get('transform', '') for n in svg.iter()) else 'right'
                          for node in svg.iter(NS + 'path') if node.attrib.get('d') == ARROW), '')
            outputs[asset] = _menu_svg(config.get('menu_labels', {}).get(label, label), width, arrow, title)
            text = re.sub(r'(<img\b[^>]*src="' + re.escape(src) + r'"[^>]*\bwidth=")[^"]+("[^>]*>)',
                          lambda m: m[1] + str(width) + m[2], text)
        texts[path] = text


def page_headers(repo, check=False):
    """Generate into an already-moved checkout. Return every drift path; check is read-only."""
    checkout = Path(repo).resolve()
    name, config, accent, org_accent = _config(checkout)
    if name == 'Packages' and checkout.name != 'site' and (checkout / 'site').is_dir():
        checkout = checkout / 'site'
    if not (checkout / 'README.md').is_file():
        raise ValueError('Checkout requires its root README.md')
    texts, outputs = {}, {}
    for page in config['pages']:
        if page.get('deleted'):
            if (checkout / page['old']).exists():
                raise ValueError(f'Apply approved git rm first: {page["old"]}')
            continue
        path = page['new']
        if (checkout / path).is_file():
            texts[path] = (checkout / path).read_text()
        elif page['old'] is None:
            texts[path] = f'# {page["title"]}\n\n{page["intro"]}\n'
        elif page['title'] != '(generated)':
            raise ValueError(f'Apply approved git mv first: {page["old"]} → {path}')
    for path in ['README.md'] + (['profile/README.md'] if name == '.github' else []):
        if (checkout / path).is_file():
            texts[path] = (checkout / path).read_text()
    # Strip before menu processing so reserved Repository/Up links cannot be removed.
    prefixes = {}
    for page in config['pages']:
        path = page['new']
        if path not in texts:
            continue
        prefixes[path], texts[path] = _strip_header(texts[path])
    _menus(checkout, config, texts, outputs)
    for page in config['pages']:
        path = page['new']
        if page.get('deleted') or path not in texts:
            continue
        body = texts[path].rstrip()
        if not page.get('excluded'):
            if path.endswith('/README.md') and posixpath.dirname(path) in config['sections']:
                listing = '## Sections\n\n' + _section_list(config, path, texts)
                pattern = r'(?:## Sections\n\n)?<!-- snodec:begin section-pages -->.*?<!-- snodec:end section-pages -->'
                body = re.sub(pattern, '', body, flags=re.S).rstrip()
                if page.get('section_list', True):
                    prefix, separator, rest = body.partition('\n## ')
                    body = prefix.rstrip() + '\n\n' + listing + ('\n\n## ' + rest if separator else '')
            body = _header(config, path) + '\n\n' + body
        texts[path] = (prefixes[path] + '\n\n' if prefixes[path] else '') + body + '\n'
    root_organization = name in ('.github', 'SNode.C-Book-Companion') or 'snodec:begin organization' in texts['README.md']
    if root_organization:
        block = _organization()
        text = texts['README.md']
        pattern = r'<!-- snodec:begin organization -->.*?<!-- snodec:end organization -->'
        if re.search(pattern, text, re.S):
            text = re.sub(pattern, lambda _: block, text, flags=re.S)
        else:
            text = re.sub(r'^# ', lambda _: block + '\n\n# ', text, count=1, flags=re.M)
        texts['README.md'] = text
    outputs.update(texts)
    active = [p for p in config['pages'] if not p.get('deleted') and not p.get('excluded')]
    for label in sorted({p['label'] for p in active}):
        for compact in (False, True):
            outputs[f'docs/media/nav/banner-{slug(label)}{"-compact" if compact else ""}.svg'] = _banner(name, config['display'], label, accent['dark']['text'], compact)
    buttons = [('repository', 'Repository', config['display'] + ' repository', 'repo', accent),
               ('organization', 'Organization', 'SNodeC organization', 'organization', org_accent)]
    buttons += [('up-' + slug(label), label, 'Up to ' + label, 'arrow-up', accent)
                for label in sorted({p['up_label'] for p in active})]
    buttons = [button for button in buttons if active or button[0] == 'organization']
    if active or root_organization:
        for stem, label, title, icon, colors in buttons:
            for theme in ('light', 'dark'):
                outputs[f'docs/media/nav/{stem}-{theme}.svg'] = _header_button(label, title, icon, colors[theme]['text'], theme)
                if active and stem in ('repository', 'organization'):
                    outputs[f'docs/media/nav/{stem}-icon-{theme}.svg'] = _header_button(label, title, icon, colors[theme]['text'], theme, 36)
    drift = [path for path, text in sorted(outputs.items())
             if not (checkout / path).is_file() or (checkout / path).read_text() != text]
    if not check:
        for path in drift:
            destination = checkout / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(outputs[path])
    return drift
