# Phase 4 — preservation-first presentation

## Scope

Only the organization profile and the existing README collections of **snode.c, mqttsuite, AISuite and CodexUI** change. All other repository READMEs remain untouched. This stage changes no CI caller, build manifest, package pipeline, secret, license file or tag. It does not merge or release anything automatically.

The governing invariant is **shared structure without loss of project-specific content**. The [frame contract](templates/readme-frame.md) applies only to the four selected repositories. Catalog identity, existing documentation and brand tokens remain their respective authorities; no new sync service or second build policy is introduced.

## Organization

The existing deterministic profile renderer now exposes area navigation, kinds and catalog dependency links. Every catalog entry, summary, note, release reference, fork parent and archive placement is retained. Verified workflow metadata uses the current shared CI callers; the removed AutoTalk native-workflow URL is corrected in the organization snapshot only, without editing AutoTalk. The profile still makes no project-count claim. No Landingpages figure is used.

## Repository preservation map

| Repository | Core | Existing content retained |
| --- | --- | --- |
| snode.c | Product | Banner; native server/client/shared context and Python interoperability; HTTP, SSE and WebSocket examples; lifecycle and transport explanations; capabilities; installation; teaching origin; reporting and dual-license text. |
| mqttsuite | Product | Banner; five application roles; publish/subscribe; mapping JSON; bridge topology and listener commands; database setup and projection semantics; transport matrix; administrative access warning; reporting and dual-license text. |
| AISuite | Product | Banner; agent and model-provider boundaries; libraries and protocol generation; all build, bridge and SDK commands; observer/authentication warning; local-source consumption; compatibility limits; verification caveats and independence/license text. |
| CodexUI | App | Banner; real native screenshot and provenance; native/browser distinction; thread grouping; state ownership; source requirements and installation; browser checkout layout; all qualification commands and incomplete-coverage caveats; documentation and independence/license text. |

Existing headings are retained or mapped to explicit legacy anchors. Guide files and original media are not moved or rewritten. New documentation indexes route to the existing pages rather than copying instructions. New light/dark header chips derive from the existing tokens and kind glyphs; these are not replacement banners.

## Verification boundaries

The control repository's catalog check, all 30 unit/boundary tests and deterministic profile drift check passed locally. Additional presentation checks passed for authored content preservation, exact fenced-example equality, legacy anchors, local files/fragments, unchanged original documentation/media and authoritative chip colors/glyphs. GitHub-rendered Markdown HTML was inspected in local Chrome previews at 1280px and 390px, in light and dark themes; these are layout previews with a local stylesheet, not a claim of exact live GitHub CSS. Do not interpret Markdown checks as product build qualification or as complete native/browser UI qualification.

| Repository | Original fenced examples retained | Legacy anchors retained | Original docs/media files unchanged |
| --- | --- | --- | --- |
| snode.c | 18 | 14 | 64 |
| mqttsuite | 18 | 11 | 38 |
| AISuite | 8 | 19 | 12 |
| CodexUI | 6 | 15 | 26 |

The profile renderer changes three production-source lines and removes three (net zero). Its regression assertions add eight test lines with no test removals. The four consumer changes contain documentation and derived SVG presentation assets only; no product production code or tests change.

Full cross-repository README generation, weekly conformance reporting and automatic sync PRs are not delivered by this editorial step. They must remain scoped and separately approved; marker presence alone must never be represented as an operating sync service. The original three-screen budget is intentionally subordinate to the owner's requirement to retain all existing content inline.
