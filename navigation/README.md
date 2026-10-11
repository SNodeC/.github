# Navigation generator and documentation audit

`plan.yml` is the authority for approved paths, section labels, Up chains, introductions and menu changes. `PLAN.md` is the human review copy, including proposed cleanup additions. Catalog identity and brand tokens remain their existing authorities. There is no second page registry or site generator.

```sh
python tools/snodec_sync page-headers --repo /path/to/checkout
python tools/snodec_sync page-headers --repo /path/to/checkout --check
python tools/snodec_sync docs-audit --repo /path/to/checkout
```

Apply the plan's `git mv` and declared deletions before generating. `page-headers` does not move/delete authored pages or rewrite unrelated links. It fails if required moved pages are absent or declared deletions remain; `--check` reports drift without writing. For DistributionPackages publication sources, select `site/` to use the Packages plan; the DistributionPackages root uses its own plan. Missing generated status files are supplied by the publisher. Neither command installs packages, reads secrets, calls the network or publishes anything.

## The stricter guard

`docs-audit` reads the Git index (`git ls-files`) and the current text of tracked Markdown. Run it at a repository root with an SNodeC origin remote, after staging any intended new documents. It lists every violation in stable order and exits non-zero: unplanned documentation, pages unreachable from root `README.md`, missing tracked link/image targets, missing heading/explicit anchors, and missing paired generated page-header/section-pages blocks. Code examples and comments do not create navigation edges. Directory links expose the tracked documents reachable through GitHub directory views.

The owner-approved unplanned-page check applies only to repositories enrolled in the header plan, for Markdown under `docs/`, `status/`, `keys/`, `web/` and `packages/*/`. AutoTalk and Book remain header-free and are still checked for reachability, links and anchors. Existing `excluded: true` media-note declarations do not generate headers or section-list entries, but their links and reachability are audited. Coding-agent instructions, media notes and source-tree READMEs must be linked; do not hide them with exemptions.

A new Markdown presentation page must be added to `plan.yml` in the same PR. Each declared section uses `README.md`, never `index.md`. Tracked Markdown outside presentation folders is still checked for reachability and links. `node_modules/` and each repository's `.github/` directory are outside the audit. Same-repository GitHub blob/tree links participate in the graph; 40-hex commit-pinned permalinks are historical and are not checked against HEAD. Other SNodeC repository links receive syntax checks only; there are no external availability probes.

An optional per-repository `exempt:` list accepts safe path globs and a single-line `reason` beginning with `Vendored`, `Third-party` or `Generated test fixture`. Exemptions cover only actual vendored/third-party trees and generated test fixtures; use narrow paths, not a blanket documentation exemption. This cleanup introduces no exemptions.

```yaml
exempt:
  - path: vendor/example/**
    reason: Vendored third-party dependency documentation.
```

## Shared rendering

```python
from tools.snodec_sync import render_header
header = render_header('Packages', 'status/snodec.md')
```

The read-only library accepts a catalog name or checkout path. Future PROJECTS-driven status pages inherit their declared section/sibling Up policy; they need no additional project registry. Other undeclared presentation pages fail. Runtime uses Python's standard library and PyYAML only. The checked-in marks and Octicons are inputs, not runtime downloads.

The generator replaces marked headers, preserves historic anchors outside the block and generates section lists from actual H1s in plan order. Root READMEs and the profile get no page headers. Banner plus button row stays unchanged: ↑ parent on the left; Organization first in HTML, then Repository, both right-aligned. The Organization button is labelled Organization. Buttons stay 160 px wide. The existing wider native/OpenWrt route buttons and native wrapping remain unchanged. Structural menus are arrow-free; onward/up-menu arrows retain their approved geometry.

Desktop banners remain 1280×56. At viewport widths up to 640 px, `<picture>` selects the existing 480×72 compact SVG, with the same mark, palette and typography. Phone stacking of Organization above Repository is accepted. No CSS workaround or alternate renderer is introduced. DistributionPackages reuses the authoritative Packages gear and infrastructure accent instead of duplicating its graphic.

## Tests and rollout

SVG goldens live in `tests/fixtures/navigation/`; tests generate all Markdown fixtures in temporary directories. Production preview pages and captured navigation evidence are not maintained as live documentation.

Run `python -m unittest discover -s tests -v`. Step 1 audit reports attached to its PR are the Step 2 worklist, not a claim that consumers already pass. The owner reviews and merges Step 1, then creates the new `v1.1` tag. Never move `v1.0`. Consumer cleanup, publication and CI changes are separate later steps, requiring the owner's continuation.
