# Phase 4 — preservation-first presentation

## Scope

Only the organization profile and the existing README collections of **snode.c, mqttsuite, AISuite and CodexUI** change. All other repository READMEs remain untouched. This stage changes no CI caller, build manifest, package pipeline, secret, license file or tag. It does not merge or release anything automatically.

The governing invariant is **shared structure without loss of project-specific content**. The [frame contract](../templates/readme-frame.md) applies only to the four selected repositories. Catalog identity, existing documentation and brand tokens remain their respective authorities; no new sync service or second build policy is introduced.

## Organization

The existing deterministic profile renderer now exposes area navigation, kinds and catalog dependency links. Links to snode.c, mqttsuite, AISuite and CodexUI use their source-verified `project-overview` banner anchors; workflow/release API paths remain unfragmented. Every catalog entry, summary, note, release reference, fork parent and archive placement is retained. Verified workflow metadata uses the current shared CI callers; the removed AutoTalk native-workflow URL is corrected in the organization snapshot only, without editing AutoTalk. The profile still makes no project-count claim. No Landingpages figure is used.

## Repository preservation map

| Repository | Core | Existing content retained |
| --- | --- | --- |
| snode.c | Product | Banner; native server/client/shared context and Python interoperability; HTTP, SSE and WebSocket examples; lifecycle and transport explanations; capabilities; installation; teaching origin; reporting and dual-license text. |
| mqttsuite | Product | Banner; five application roles; publish/subscribe; mapping JSON; bridge topology and listener commands; database setup and projection semantics; transport matrix; administrative access warning; reporting and dual-license text. |
| AISuite | Product | Banner; agent and model-provider boundaries; libraries and protocol generation; all build, bridge and SDK commands; observer/authentication warning; local-source consumption; compatibility limits; verification caveats and independence/license text. |
| CodexUI | App | Banner; real native screenshot and provenance; native/browser distinction; thread grouping; state ownership; source requirements and installation; browser checkout layout; all qualification commands and incomplete-coverage caveats; documentation and independence/license text. |

Existing headings are retained or mapped to explicit legacy anchors. Guide files and original media are not moved. The approved secondary-link presentation update rewrites only navigation callouts; existing back-button arrow glyphs translate up 1 px without resizing. Banners, diagrams, examples and substantive guide content remain preserved. New documentation indexes route to the existing pages rather than copying instructions. New light/dark header chips derive from the existing tokens and kind glyphs; these are not replacement banners. The menu uses the original blue-gray SVG block-button style, with 108×24 sizing, accessible titles/alternative text and buttons-only navigation. The root README and docs index share identical destinations and button order.

## Earlier verification (before the direct-build-guide migration)

The control repository's catalog check, all 31 unit/boundary tests and deterministic profile drift check passed locally. Additional presentation checks passed for authored content preservation, exact fenced-example equality, legacy anchors, local files/fragments, original documentation/media preservation apart from the approved callout and arrow translations and authoritative chip colors/glyphs. GitHub-rendered Markdown HTML was inspected in local Chrome previews at 1280px and 390px, in light and dark themes; these are layout previews with a local stylesheet, not a claim of exact live GitHub CSS. Do not interpret Markdown checks as product build qualification or as complete native/browser UI qualification.

| Repository | Original fenced examples retained | Legacy anchors retained | Original docs/media files retained |
| --- | --- | --- | --- |
| snode.c | 18 | 14 | 64 |
| mqttsuite | 18 | 11 | 38 |
| AISuite | 8 | 19 | 12 |
| CodexUI | 6 | 15 | 26 |

The complete profile renderer PR changes seven production-source lines and removes seven (net zero). Its regression assertions add 25 test lines with no test removals. Menu checks also verify the original block-button palette and geometry, 12.91:1 text contrast in both themes, matching root/index destinations and the absence of duplicate navigation. The four consumer changes contain documentation and derived SVG presentation assets only; no product production code or tests change.

Full cross-repository README generation, weekly conformance reporting and automatic sync PRs are not delivered by this editorial step. They must remain scoped and separately approved; marker presence alone must never be represented as an operating sync service. The original three-screen budget is intentionally subordinate to the owner's requirement to retain all existing content inline.

## Secondary links and arrow alignment

The approved continuation removes “Go further:” / “Reference:” navigation prefixes and renders each existing destination as its own short SVG button with an appended right arrow. All 23 destinations and their full accessible labels remain intact across 17 callouts in snode.c, mqttsuite and CodexUI; explanatory text remains nearby, and multiple buttons share one paragraph in their original order. AISuite has no matching callouts or arrow-bearing buttons, so its published assets remain unchanged.

Both existing left-arrow back buttons keep their original canvas, palette, 13 px font, label baseline and horizontal geometry. Only arrow glyphs translate up 1 px; new right arrows use the same placement. Font-ink metrics and before/after raster checks distinguish placement from size. The existing main-menu buttons have no arrows and are unchanged. No production code, tests, CI, licensing or tags are modified by this continuation.

The final approved hierarchy keeps main-menu buttons arrow-free, at their existing widths with natural wrapping. Secondary/back buttons replace the thin font arrow with a single bold filled SVG silhouette embedded in each existing asset: unchanged 9×4 measured ink bounds, 1.5 px shaft, vertical centre y=12; left arrows mirror the same shape. All 21 arrow-bearing assets use this geometry. Label typography and positions are retained within SVG's fractional positioning precision (less than 0.016 px); no font-arrow renderer remains. No separate arrow asset, new generator or ordinary-link arrow is introduced. This continuation changes documentation/SVG assets only: production source +0/-0 and repository test source +0/-0.

## Common-menu semantic alignment

The four root menus and docs indexes now enter the same README-level roles: Start → Quick start; Install → Install; Build → Build from source; Use → First success/First run; Configure → Configuration; Architecture → Architecture; Contribute → Contributing. Existing API entries remain direct reference links. Quick start is only a short reader route, no longer a second installation chooser or an app feature tour. Detailed guides keep topic-specific structure one level below these entries.

SNode.C and MQTTSuite now have distinct source-build and runtime-configuration entry sections pointing into their unchanged guides. AISuite's Configure entry targets the actual configuration contract rather than an entire architecture document. CodexUI's Start enters Quick start, while its overview, screenshot and UI tour remain intact; Architecture preserves the former `how-it-fits-together` anchor. AISuite and CodexUI installation commands and their original prefix/privilege caveats move from Build into Install exactly once; source build/test commands stay under Build. All existing examples, media, guides, warnings and qualifications remain preserved. This semantic correction changes documentation only: production-source +0/-0 and repository-test-source +0/-0.

## Buttons-only menus and installation cleanup

The owner removed the duplicate “Text navigation” dropdown and its plain-link copy from all four root READMEs and documentation indexes. The linked SVG buttons retain their titles, alternative text, order and destinations. The organization profile has no such dropdown and is unchanged.

Install now uses short, separate paragraphs with bold route labels across the four projects, beginning with “Choose your route.” There are no installation tables, grids or bordered panels. Available routes remain project-specific; source-only projects do not acquire a binary-package promise. SNode.C and MQTTSuite remove the repeated package pitch and platform enumeration; the single Packages destination provides the current matrix. MQTTSuite's administrative-exposure warning becomes a concise application-by-application list under Configuration, preserving its safety meaning and heading/anchor. All examples, commands, requirements, privilege/prefix caveats, banners, figures and guide contents remain. This continuation changes documentation only: production source +0/-0, repository test source +0/-0.

The latest owner instruction permits rewriting prose and deleting redundant passages together with their links. Content retention is semantic, not a word-for-word or link-count constraint; menus contain only buttons. MQTTSuite’s automatic-framework-dependency note sits with the signed-package route rather than beneath the source route.

## Organization menu buttons

The profile renderer replaces the six-area plain-link row with linked SVG buttons in the same arrow-free 108×24 blue-gray style as the repository menus. Short visible labels (Community, Infrastructure) keep the fixed width; full area names remain link titles and image alternative text. Area order and section destinations still derive from `AREAS`, not a second navigation registry. Assets use paths relative to the profile so branch previews can display them before merge. There is no duplicate text-navigation row or dropdown. The change replaces one production-source line with one (net zero); regression assertions verify generated links, asset availability, style and contrast.

## Direct build guides and route-label punctuation

The latest approved structure supersedes the intermediate README build sections described above: Install remains a concise chooser; Build and every source-install link enter the build guide directly. Remove all four README Build from source sections. SNode.C and MQTTSuite reuse their existing complete source guides. AISuite and CodexUI move prerequisites, configure/build commands and install commands/caveats into `docs/build.md`; CodexUI's browser build steps also move there, and `web/README.md` retains deployment/verification rather than a duplicate source-build procedure. First-use examples and qualification warnings remain in the READMEs.

Install route labels now use a bold colon, not the rejected long dash; Quick start uses the same colon separator convention. Main-menu SVGs, route availability, runtime warnings, banners and figures remain unchanged. Documentation only: production source +0/-0 and repository test source +0/-0. Moved commands must be verified across the README and its build guide, not by requiring every former build block to remain in the README.
