# Step 1 verification

## Invariant and scope

One approved navigation plan, catalog identity and brand tokens drive one offline header/menu implementation. The exported read-only `render_header` uses the same implementation as the CLI. No second project registry, runtime downloads, publication logic or synchronization layer was added. PROJECTS-generated status pages inherit their declared section policy.

Step 1 is preparation, not deployment to consumers. Product source pages, DistributionPackages/site, the Packages renderer and live Packages pages are unchanged. Consumer moves, whole-body link rewrites and removal of obsolete assets belong to Step 2; this report does not claim those have been verified or completed.

## Source verification — measured

Default branches were read through the GitHub API, never renamed or assumed. Applicable repository/global instructions were read before editing. The snapshots used for path/title/graphic verification were:

| Repository | Default branch | Commit |
| --- | --- | --- |
| .github | main | `dbad6b59a6fb6af1d61486a78eebfc67452a5ccf` |
| snode.c | master | `129fda2093f6f9fc0fd6928e210735ee6a465df1` |
| mqttsuite | master | `09df1ffabba42dfe61c060d89f0a2704037bd2dd` |
| AISuite | master | `f5a04358e589f5e7abc951972e432d27ce850f8a` |
| CodexUI | master | `52be73cd39b7de9aefb9c9a8e367337f16b899ca` |
| DistributionPackages (authored Packages source) | main | `47a1da32b2ff62aa4730887ce493007c7ac50a4c` |
| Packages (generated status/legacy pages) | main | `cfd165fa1cec99007e43b69f07bd205da79d6ae3` |

[Path verification](plan-path-check.json): 107 plan entries; zero missing old paths, destination/media collisions or missing post-move parents. The Packages `source_commit` there identifies DistributionPackages/site; generated pages were separately checked against the Packages commit above. [Chain verification](chain-check.json): every Up chain terminates at its root and every Up label is at most 14 characters. [Title verification](title-check.json): every inspected authored H1 matches the plan. Generated titles were not invented or compared as authored content.

No plan fact required correction. The owner-approved additions encode the Package guide Quick install changes and status All projects removal already specified in the human plan/prompt. The prompt-permitted visible menu shortenings are recorded in both plan files; paths, introductions, full accessible labels and URLs are unchanged.

## Local verification — measured

43 tests passed, no skips, through `python3 -m unittest discover -s tests -v`. This includes the existing catalog/profile and reusable-workflow tests, plus plan chains, invalid inputs, generated links/assets, exact button order, exclusions, root guards, actual-H1 lists, deterministic regeneration, write-free checks, preserved body/commands/historic anchors, semantic Install links, future generated projects and protected state bytes.

Catalog check, profile drift check, control menu drift check, isolated committed-fixture drift check and `git diff --check` passed. The final diff leaves the control root README, catalog, workflow files, licences and tags unchanged. No other repository was edited.

[Contrast ratios](contrast.json): button text in both themes, all five banner accent texts against both gradient endpoint colors, white banner names and white menu text pass 4.5:1. [Menu width measurements](menu-widths.json): Chrome Canvas measured 88 actually referenced non-back menu assets using Arial 16px/600; after the recorded short labels, none exceeds its reserved text space. This is font measurement, not a claim to have reviewed every real consumer page in a browser.

## Native GitHub verification — measured

The committed Packages hierarchy is a **rendering fixture**, not real package/status data. The screenshots use native github.com blob previews at branch commit `14dc0516cfa7f7e349c3442e59e16fa5b9d86c5a`; the fixture files are unchanged by the follow-up correction. Chrome viewport widths were 1920 and 390 CSS pixels; device scale factor 1. Light/dark preferences were emulated and GitHub's standard theme attributes selected accordingly. No custom page CSS or Markdown renderer was used.

[DOM geometry and image-load measurements](metrics.json) cover all twelve captures. At desktop width the Markdown article is 1012px wide: Up is left; Repository is left of Organization on the right; all buttons share the same Y position. GitHub retained `align="right"` and computed `float:right`. It retained `clear="all"` and computed `clear:both`; every H1 is below all buttons. Source order is Up, Organization, Repository. No broken images were observed. The theme-specific picture sources were retained.

At 390px viewport width, the article is 309px: Up occupies the first line; Organization and Repository stack at the right on subsequent lines. This is the explicitly accepted native narrow-screen behavior, not a mobile workaround. GitHub contributes 20px left padding to the right-floated image boxes; their SVG contents remain 160×28.

| Fixture | Desktop light | Desktop dark | Phone light | Phone dark |
| --- | --- | --- | --- | --- |
| Section README | [Screenshot](docs__installation__README.md-1920-light.png) | [Screenshot](docs__installation__README.md-1920-dark.png) | [Screenshot](docs__installation__README.md-390-light.png) | [Screenshot](docs__installation__README.md-390-dark.png) |
| Section page | [Screenshot](docs__installation__debian.md-1920-light.png) | [Screenshot](docs__installation__debian.md-1920-dark.png) | [Screenshot](docs__installation__debian.md-390-light.png) | [Screenshot](docs__installation__debian.md-390-dark.png) |
| Code README | [Screenshot](keys__README.md-1920-light.png) | [Screenshot](keys__README.md-1920-dark.png) | [Screenshot](keys__README.md-390-light.png) | [Screenshot](keys__README.md-390-dark.png) |

### Contract-bound/native limitations

The prescribed 1280×56 banner scales to 309×13.52 on phone. Its 25px source name becomes approximately 6px at that width; legibility is poor. No alternate banner or CSS workaround was introduced because the geometry is binding.

The authored banner is an unlinked identity `<img>`, not repository navigation. GitHub automatically wraps it in a link to its own SVG blob; this native image-view affordance cannot be suppressed by the prescribed markup. The measurements record that wrapper rather than incorrectly claiming the rendered parent is a paragraph.

Visual inspection supports the requested desktop layout and readable buttons in both themes, but does not establish professional quality for the still-unmigrated full consumer documentation system.

## CI and handoff

At the owner's explicit request, the control CI workflow (`ci.yml`, GitHub workflow ID `380610177`) was disabled through the API and verified as `disabled_manually`, with no active control runs. Reusable Verify remains unchanged. No workflow definitions, triggers, package pipeline, secrets, signing, tags or branch names were changed; no CI was dispatched or rerun.

[Change accounting](accounting.json) separates production Python, tests, documentation/evidence and SVG assets; binary screenshots are counted separately. Production growth was explicitly approved (350–500 lines estimated). The existing profile menu geometry was reshaped rather than introducing another profile renderer. This prepares the single implementation for the explicitly staged consumer migration, not a second live implementation.

Stop at PR handoff. The owner merges Step 1 and moves the existing `v1.0` tag before separately authorizing Step 2.
