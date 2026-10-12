# Navigation generator

`plan.yml` is the authority for approved paths, section labels, Up chains, introductions and menu changes. `PLAN.md` is the human review copy, including proposed cleanup additions. Catalog identity and brand tokens remain their existing authorities. There is no second page registry or site generator.

```sh
python tools/snodec_sync page-headers --repo /path/to/checkout
python tools/snodec_sync page-headers --repo /path/to/checkout --check
```

Apply the plan's `git mv` and declared deletions before generating. `page-headers` does not move/delete authored pages or rewrite unrelated links. It fails if required moved pages are absent or declared deletions remain; `--check` reports drift without writing. For DistributionPackages publication sources, select `site/` to use the Packages plan; the DistributionPackages root uses its own plan. Missing generated status files are supplied by the publisher. The generator does not install packages, read secrets, call the network or publish anything.

## Documentation ownership

Documentation review is separate from build verification. `docs-audit` is an optional, read-only local/PR review command; it never runs in Verify, package builds or publication. A new planned Markdown page is added to `plan.yml` in the same PR. Existing excluded media notes remain reachable but have no generated header. Narrow `exempt:` declarations identify published-output targets or vendored/generated fixture paths with a reason; they do not excuse ordinary unreachable pages.

```sh
python tools/snodec_sync docs-audit --repo /path/to/checkout
```

The audit reports unplanned enrolled pages, unreachable tracked Markdown, broken local links, missing anchors and generated blocks. It also reports image buttons outside marked navigation blocks, missing parent backlinks and files above 300 KB; files above 100 KB are information only. It does not fetch remote URLs. `section_list: false` disables the generated section list where an existing project table is the section's navigation authority.

## Design rules

Button images are allowed only in the banner navigation row (or the root Organization block) and the marked title menu, including the organization area menu. Everything below that menu is a normal text link, including route choices. Wrap title menus in `<!-- snodec:begin menu -->` / `<!-- snodec:end menu -->`.

Tables grow by rows: one thing per row. A growing project set gets another row or another page, never another project column or a list of projects within a cell.

## Shared rendering

```python
from tools.snodec_sync import render_header
header = render_header('Packages', 'status/snodec.md')
```

The read-only library accepts a catalog name or checkout path. Future PROJECTS-driven status pages inherit their declared section/sibling Up policy; they need no additional project registry. Other undeclared presentation pages fail. Runtime uses Python's standard library and PyYAML only. The checked-in marks and Octicons are inputs, not runtime downloads.

The generator replaces marked headers, preserves historic anchors outside the block and generates section lists from actual H1s in plan order. Root READMEs and the profile get no page headers. Banner plus button row stays unchanged: ↑ parent on the left; Organization first in HTML, then Repository, both right-aligned. The Organization button is labelled Organization. Buttons stay 160 px wide. Native wrapping remains unchanged. Structural title menus are arrow-free; onward and route links are ordinary text.

Desktop banners remain 1280×56. At viewport widths up to 640 px, `<picture>` selects the existing 480×72 compact SVG, with the same mark, palette and typography. Phone stacking of Organization above Repository is accepted. No CSS workaround or alternate renderer is introduced. DistributionPackages reuses the authoritative Packages gear and infrastructure accent instead of duplicating its graphic.

## Tests and releases

Run `python -m unittest discover -s tests -v` for generator and workflow behavior. Presentation goldens and authored-document drift gates are not maintained. Existing release tags remain unchanged. Verify callers and the template follow `@main` by owner decision; documentation tooling does not require a Verify release.
