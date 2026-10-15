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

The generator replaces marked headers, preserves historic anchors and generates section lists from actual H1s in plan order. Each page has a stable `banner` anchor before its banner; root READMEs place it before the hero. Up and page-level links target `#banner`; intentional section, source-file, download and external-documentation links retain their targets. Pages without a banner retain their existing destinations.

The banner row shows Up on the left and Repository, Organization and Account on the right. Identity buttons display names with Octicons: the repository's display name, SNode.C, and Volker Christian. Titles and accessible image labels identify the destination type, including the two SNode.C buttons. Right floats use reverse HTML order so the visible order is repository, organization, account. The organization links to `https://github.com/SNodeC#banner`; the account links to `https://github.com/VolkerChristian#banner`. Root identity rows use the same renderer.

Desktop banners remain 1280×56; below 640 px the existing 480×72 compact SVG is selected. Identity buttons select 36×28 icons on mobile, including root rows; Up stays 160×28. Full button widths grow for long names. Native GitHub wrapping is preserved. DistributionPackages reuses the Packages gear and infrastructure accent; organization control uses the SNode.C mark.

## Tests and releases

Run `python -m unittest discover -s tests -v` for generator and workflow behavior. Presentation goldens and authored-document drift gates are not maintained. Existing release tags remain unchanged. Verify callers and the template follow `@main` by owner decision; documentation tooling does not require a Verify release.

## Shared visual spec

Navigation and title-menu labels use 15 px / 600 with `-apple-system, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif`; banners use the same stack at their existing sizes. Heroes retain DejaVu Sans. Outline navigation and filled `#203440` title menus remain distinct. Mobile icon selection uses the approved three `<source>` elements plus a fallback `<img>`, with no image width/height on the three identity buttons; SVG intrinsic sizes and native GitHub padding are preserved. The snode.c GitHub gate passed at 390 and 1440 px in light/dark modes before rollout.

Root Organization blocks are generated from the same markup and SVG renderer. Book Companion can be generated in its exported public checkout without enrolling its learning pages; copy the generated root README and identity assets back to the private source through the existing export allow-list. No private source is published by this tool.
