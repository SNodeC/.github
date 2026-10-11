# Navigation generator — Step 1

`plan.yml` is the authority for approved paths, section labels, Up chains, introductions and menu changes. `PLAN.md` is its supplied human review copy. The two menu changes originally recorded only in that copy/prompt are now encoded losslessly in YAML with the owner's approval. No paths or introductions were redesigned.

```sh
python3 tools/snodec_sync page-headers --repo /path/to/checkout
python3 tools/snodec_sync page-headers --repo /path/to/checkout --check
```

Apply the plan's `git mv` and `git rm` operations **before** generating. The command deliberately does not move/delete pages or rewrite unrelated links. It fails if required moved pages are absent or declared deletions remain. `--check` reports drift without writing. For DistributionPackages, point at its `site/` directory (or its checkout). Missing generated status files are supplied later by its renderer; authored pages must exist. The command never edits state, installs packages, reads secrets, calls the network or publishes anything.

```python
from tools.snodec_sync import render_header
header = render_header('Packages', 'status/snodec.md')
```

The read-only library accepts a catalog name or checkout path. Future PROJECTS-driven status pages inherit their declared section/sibling Up policy; they need no additional project registry or per-project plan entry. Other undeclared pages fail. Runtime uses Python's standard library and PyYAML only; the small copied graphics and Octicons are checked-in inputs, not runtime downloads.

The generator replaces existing marked headers, retains historic anchors outside the block, removes old unmarked package identity banners, leaves excluded pages without headers and generates section lists from actual H1s in plan order. Root READMEs/profile get no headers. Existing menu destinations remain; pure upward buttons are removed. Shared Install assets are not repurposed when a guide needs Quick install: it gets its own asset. Menus are 160×28 (existing 274px buttons become/stay 328×28). Structural menus are arrow-free; onward/up-menu arrows retain the approved bold path, size and direction.

[Packages rendering fixture](preview/Packages/docs/installation/README.md#page-overview) is evidence, not a new Packages page system or real status data. Fixture destinations reproduce the proposed hierarchy entirely inside this PR. To recheck it without identifying the enclosing control checkout as Packages, copy `preview/Packages` into an isolated temporary directory named Packages and run the same CLI there.

Step 2 has **not** happened. No product or DistributionPackages source pages moved, no pipeline/library integration was deployed, no Packages snapshot was published, and no tag moved. Review/merge this PR first; the owner then moves the existing `v1.0` tag. Consumer PRs follow separately and each will contain the required Moves and Headers commits.
