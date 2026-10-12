# Navigation generator

`plan.yml` is the authority for approved paths, section labels, Up chains, introductions and menu changes. `PLAN.md` is the human review copy, including proposed cleanup additions. Catalog identity and brand tokens remain their existing authorities. There is no second page registry or site generator.

```sh
python tools/snodec_sync page-headers --repo /path/to/checkout
python tools/snodec_sync page-headers --repo /path/to/checkout --check
```

Apply the plan's `git mv` and declared deletions before generating. `page-headers` does not move/delete authored pages or rewrite unrelated links. It fails if required moved pages are absent or declared deletions remain; `--check` reports drift without writing. For DistributionPackages publication sources, select `site/` to use the Packages plan; the DistributionPackages root uses its own plan. Missing generated status files are supplied by the publisher. The generator installs packages, reads secrets, calls the network or publishes anything.

## Documentation ownership

Documentation edits are not CI reachability, link, anchor or generated-output gates. The former docs-audit command, its exemptions and its tests have been removed. Use the page-header generator when updating shared navigation; it is not a prerequisite for code verification.

## Shared rendering

```python
from tools.snodec_sync import render_header
header = render_header('Packages', 'status/snodec.md')
```

The read-only library accepts a catalog name or checkout path. Future PROJECTS-driven status pages inherit their declared section/sibling Up policy; they need no additional project registry. Other undeclared presentation pages fail. Runtime uses Python's standard library and PyYAML only. The checked-in marks and Octicons are inputs, not runtime downloads.

The generator replaces marked headers, preserves historic anchors outside the block and generates section lists from actual H1s in plan order. Root READMEs and the profile get no page headers. Banner plus button row stays unchanged: ↑ parent on the left; Organization first in HTML, then Repository, both right-aligned. The Organization button is labelled Organization. Buttons stay 160 px wide. The existing wider native/OpenWrt route buttons and native wrapping remain unchanged. Structural menus are arrow-free; onward/up-menu arrows retain their approved geometry.

Desktop banners remain 1280×56. At viewport widths up to 640 px, `<picture>` selects the existing 480×72 compact SVG, with the same mark, palette and typography. Phone stacking of Organization above Repository is accepted. No CSS workaround or alternate renderer is introduced. DistributionPackages reuses the authoritative Packages gear and infrastructure accent instead of duplicating its graphic.

## Tests and releases

Run `python -m unittest discover -s tests -v` for generator and workflow behavior. Presentation goldens and authored-document drift gates are not maintained. Existing release tags remain unchanged; a changed Verify workflow requires a new approved release and caller pins.
