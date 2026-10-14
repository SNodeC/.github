# Navigation plan

Generated inventory of all subpages: proposed path, banner text and upward button. Code READMEs keep their path. New section READMEs are marked *new*. Review, correct, then hand to Codex together with the prompt.

## SNode.C

| Current path | New path | Page title | Banner | ↑ Button → target |
| --- | --- | --- | --- | --- |
| `docs/index.md` | `docs/README.md` | SNode.C documentation | SNode.C · Documentation | ↑ SNode.C → `README.md` |
| *new* | `docs/design/README.md` | Design | SNode.C · Design | ↑ Documentation → `docs/README.md` |
| `docs/config-comment-metadata.md` | `docs/design/config-comment-metadata.md` | Configuration comment metadata | SNode.C · Design | ↑ Design → `docs/design/README.md` |
| `docs/resource-policy-and-streaming.md` | `docs/design/resource-policies-and-streaming.md` | Framework resource policies and descriptor streaming | SNode.C · Design | ↑ Design → `docs/design/README.md` |
| `docs/core-stream-shutdown-lifecycle.md` | `docs/design/stream-shutdown-lifecycle.md` | Established stream shutdown lifecycle | SNode.C · Design | ↑ Design → `docs/design/README.md` |
| *new* | `docs/guides/README.md` | Guides | SNode.C · Guides | ↑ Documentation → `docs/README.md` |
| `docs/readme/install.md` | `docs/guides/build-from-source.md` | Build and install SNode.C from source | SNode.C · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/readme/capabilities.md` | `docs/guides/capabilities.md` | SNode.C capability map | SNode.C · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/readme/deployment.md` | `docs/guides/deployment.md` | Deploy an SNode.C application | SNode.C · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/readme/examples.md` | `docs/guides/examples.md` | Build something with SNode.C | SNode.C · Guides | ↑ Guides → `docs/guides/README.md` |
| *new* | `docs/logging/README.md` | Logging | SNode.C · Logging | ↑ Documentation → `docs/README.md` |
| `docs/logging/public-log-api.md` | `docs/logging/public-api.md` | Public logging API | SNode.C · Logging | ↑ Logging → `docs/logging/README.md` |
| `docs/logging/semantic-text-output-format.md` | `docs/logging/text-output-format.md` | Semantic text output format | SNode.C · Logging | ↑ Logging → `docs/logging/README.md` |
| `examples/echo/README.md` | *unchanged* | External SNode.C echo pair | SNode.C · Examples | ↑ SNode.C → `README.md` |
| `src/apps/README.md` | *unchanged* | Example application inventory | SNode.C · Examples | ↑ SNode.C → `README.md` |
| `src/apps/oauth2/authorization_server/vue-frontend-oauth2-auth-server/README.md` | *unchanged* | Vue 3 + TypeScript + Vite | *no header* | — |
| `src/apps/oauth2/client_app/vue-frontend-oauth2-client/README.md` | *unchanged* | Vue 3 + TypeScript + Vite | *no header* | — |
| `src/express/express-compat-suite/README.md` | *unchanged* | Express Compatibility Suite (Node.js/Express v4 vs SNode.C/Express) | SNode.C · Tests | ↑ SNode.C → `README.md` |
| `src/tools/snodec-control/README.md` | *unchanged* | snodec-control | SNode.C · Tools | ↑ SNode.C → `README.md` |
| `src/tools/snodec-control/tests/fixtures/README.md` | *unchanged* | Test fixtures | SNode.C · Tools | ↑ snodec-control → `src/tools/snodec-control/README.md` |
| `src/tools/snodec-control/tests/manual/smoke-ui-notes.md` | *unchanged* | Manual UI smoke test notes | SNode.C · Tools | ↑ snodec-control → `src/tools/snodec-control/README.md` |
| `tests/component/net/README.md` | *unchanged* | Legacy Stream Component Test Coverage | SNode.C · Tests | ↑ SNode.C → `README.md` |

**New section READMEs (proposed introduction)**

- `docs/design/README.md`: Design notes on stream shutdown, resource policies and configuration metadata.
- `docs/guides/README.md`: Task-oriented guides for building, running and deploying SNode.C applications.
- `docs/logging/README.md`: The public logging API and the format of its semantic text output.

**Media moves**

- `docs/readme/media/` → `docs/media/`

**Links outside Markdown pages and from other repositories**

- `snode.c:src/tools/snodec-control/src/ConfigModel.h (docs/config-comment-metadata.md)`
- `snode.c:src/tools/snodec-control/src/Json.h (docs/config-comment-metadata.md)`
- `snode.c:src/tools/snodec-control/src/Metadata.h (docs/config-comment-metadata.md)`
- `snode.c:src/tools/snodec-control/src/ui/UiState.cpp (docs/config-comment-metadata.md)`
- `snode.c:src/tools/snodec-control/tests/SnodecControlConfigParserTest.cpp (docs/config-comment-metadata.md)`
- `SNode.C-Landingpages:SNode.C/workflow/03-TECHNICAL-FACTS.md @master`

## MQTTSuite

| Current path | New path | Page title | Banner | ↑ Button → target |
| --- | --- | --- | --- | --- |
| `docs/index.md` | `docs/README.md` | MQTTSuite documentation | MQTTSuite · Documentation | ↑ MQTTSuite → `README.md` |
| *new* | `docs/guides/README.md` | Guides | MQTTSuite · Guides | ↑ Documentation → `docs/README.md` |
| `docs/readme/bridging.md` | `docs/guides/bridging.md` | Connect two brokers | MQTTSuite · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/readme/install.md` | `docs/guides/build-from-source.md` | Build and install MQTTSuite from source | MQTTSuite · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/readme/deployment.md` | `docs/guides/deployment.md` | Operate MQTTSuite deliberately | MQTTSuite · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/readme/mapping.md` | `docs/guides/mapping.md` | Map messages into the form your application needs | MQTTSuite · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/readme/storage.md` | `docs/guides/storage.md` | Persist messages and project useful fields | MQTTSuite · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/mqttstore-user-guide.md` | *unchanged* | MQTTStore User Guide | MQTTSuite · Documentation | ↑ Documentation → `docs/README.md` |

**New section READMEs (proposed introduction)**

- `docs/guides/README.md`: Guides for building, deploying, bridging, mapping and storing with MQTTSuite.

**Media moves**

- `docs/readme/media/` → `docs/media/`
- `docs/images/` → `docs/media/`

**Links outside Markdown pages and from other repositories**

- `DistributionPackages:evidence/package-status-redesign/docs/mqttsuite-package-options.md @HEAD`
- `DistributionPackages:site/docs/mqttsuite-package-options.md @HEAD`

## AISuite

| Current path | New path | Page title | Banner | ↑ Button → target |
| --- | --- | --- | --- | --- |
| `docs/index.md` | `docs/README.md` | AISuite documentation | AISuite · Documentation | ↑ AISuite → `README.md` |
| *new* | `docs/architecture/README.md` | Architecture | AISuite · Architecture | ↑ Documentation → `docs/README.md` |
| `src/ai/openai/codex/docs/architecture.md` | `docs/architecture/codex-bridge.md` | codex / codex-bridge Architecture | AISuite · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| `src/ai/openai/codex/docs/mqttsuite-architecture-study.md` | `docs/architecture/mqttsuite-study.md` | MQTTSuite Architecture Study for codex | AISuite · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| `src/ai/openai/codex/docs/snodec-architecture-study.md` | `docs/architecture/snodec-study.md` | SNode.C Architecture Study for codex | AISuite · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| *new* | `docs/codex/README.md` | Codex | AISuite · Codex | ↑ Documentation → `docs/README.md` |
| `docs/codex-observer-policy.md` | `docs/codex/observer-policy.md` | Codex bridge observer policy | AISuite · Codex | ↑ Codex → `docs/codex/README.md` |
| `docs/codex-responses-profile.md` | `docs/codex/responses-profile.md` | Codex Responses compatibility profile: 0.154.0 | AISuite · Codex | ↑ Codex → `docs/codex/README.md` |
| *new* | `docs/guides/README.md` | Guides | AISuite · Guides | ↑ Documentation → `docs/README.md` |
| `docs/agent-providers.md` | `docs/guides/agent-providers.md` | Agent runtimes and model providers | AISuite · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/build.md` | `docs/guides/build-from-source.md` | Build and install AISuite from source | AISuite · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/media/README.md` | *unchanged* | Landing-page assets | *no header* | — |
| *new* | `docs/records/README.md` | Records | AISuite · Records | ↑ Documentation → `docs/README.md` |
| `docs/records/anthropic-verification.md` | *unchanged* | Implementation and verification record | AISuite · Records | ↑ Records → `docs/records/README.md` |
| `docs/records/observer-verification.md` | *unchanged* | Observer Verification | AISuite · Records | ↑ Records → `docs/records/README.md` |
| `packages/codex-frontend/README.md` | *unchanged* | `@snodec/codex-frontend` | AISuite · Frontend SDK | ↑ AISuite → `README.md` |

**New section READMEs (proposed introduction)**

- `docs/architecture/README.md`: Architecture of the codex bridge and the studies of SNode.C and MQTTSuite it is based on.
- `docs/codex/README.md`: Codex-specific policies and the supported Codex Responses compatibility profile.
- `docs/guides/README.md`: Building AISuite and choosing agent runtimes and model providers.
- `docs/records/README.md`: Implementation and verification records.

**Links outside Markdown pages and from other repositories**

- `SNode.C-Landingpages:AISuite/README.md @master`
- `SNode.C-Landingpages:CodexUI/README.md @master`
- `SNode.C-Landingpages:FACTS.md @master`
- `SNode.C-Landingpages:SNode.C-orga/README.md @master`

## CodexUI

| Current path | New path | Page title | Banner | ↑ Button → target |
| --- | --- | --- | --- | --- |
| `docs/index.md` | `docs/README.md` | Codex(W)UI documentation | CodexUI · Documentation | ↑ CodexUI → `README.md` |
| *new* | `docs/architecture/README.md` | Architecture | CodexUI · Architecture | ↑ Documentation → `docs/README.md` |
| `docs/app-server-protocol/master-data-model.md` | `docs/architecture/app-server-data-model.md` | Historical Codex app-server protocol and proposed master data model | CodexUI · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| `docs/codex-architecture.md` | `docs/architecture/overview.md` | CodexUI architecture | CodexUI · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| `docs/qt-ui-architecture-audit.md` | `docs/architecture/qt-ui-audit.md` | CodexUI Qt UI architecture and usability audit | CodexUI · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| `docs/qt-virtualized-conversation-view.md` | `docs/architecture/qt-virtualized-conversation-view.md` | Qt virtualized conversation view | CodexUI · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| *new* | `docs/architecture/remediation/README.md` | Remediation | CodexUI · Remediation | ↑ Architecture → `docs/architecture/README.md` |
| `docs/architecture/qt-remediation-findings-ledger.md` | `docs/architecture/remediation/findings-ledger.md` | Qt architecture remediation findings ledger | CodexUI · Remediation | ↑ Remediation → `docs/architecture/remediation/README.md` |
| `docs/architecture/qt-remediation-thread-prompt.md` | `docs/architecture/remediation/thread-prompt.md` | CodexUI Qt architecture remediation thread prompt | CodexUI · Remediation | ↑ Remediation → `docs/architecture/remediation/README.md` |
| *new* | `docs/architecture/reviews/README.md` | Reviews | CodexUI · Reviews | ↑ Architecture → `docs/architecture/README.md` |
| `docs/architecture/reviews/chatgpt-review.md` | `docs/architecture/reviews/chatgpt.md` | External architecture review — ChatGPT | CodexUI · Reviews | ↑ Reviews → `docs/architecture/reviews/README.md` |
| `docs/architecture/reviews/claude-review-a.md` | `docs/architecture/reviews/claude-a.md` | External architecture review — Claude A | CodexUI · Reviews | ↑ Reviews → `docs/architecture/reviews/README.md` |
| `docs/architecture/reviews/claude-review-b.md` | `docs/architecture/reviews/claude-b.md` | External architecture review — Claude B | CodexUI · Reviews | ↑ Reviews → `docs/architecture/reviews/README.md` |
| `docs/two-thread-shared-node-graph.md` | `docs/architecture/shared-node-graph.md` | Shared node graph: writer, UI and projection readers | CodexUI · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| `docs/architecture/timestamp-presentation.md` | *unchanged* | App-server timestamp presentation | CodexUI · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| `docs/ui-ux-internal-api.md` | `docs/architecture/ui-internal-api.md` | Native UI/UX internal API contract | CodexUI · Architecture | ↑ Architecture → `docs/architecture/README.md` |
| *new* | `docs/guides/README.md` | Guides | CodexUI · Guides | ↑ Documentation → `docs/README.md` |
| `docs/build.md` | `docs/guides/build-from-source.md` | Build and install Codex(W)UI from source | CodexUI · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/ui-behavior.md` | `docs/guides/interaction-guide.md` | Interaction guide | CodexUI · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/thread-projects-sections.md` | `docs/guides/thread-projects.md` | Native thread projects and sections | CodexUI · Guides | ↑ Guides → `docs/guides/README.md` |
| `docs/media/README.md` | *unchanged* | Landing-page assets | *no header* | — |
| *new* | `docs/qualification/README.md` | Qualification | CodexUI · Qualification | ↑ Documentation → `docs/README.md` |
| `docs/native-ui-ux-qualification-results.md` | `docs/qualification/native-results-2026-09-27.md` | Native qualification execution record — 2026-09-27 | CodexUI · Qualification | ↑ Qualification → `docs/qualification/README.md` |
| `docs/native-ui-ux-qualification-inventory.md` | `docs/qualification/native-test-suite.md` | CodexUI canonical interactive Xvfb test suite | CodexUI · Qualification | ↑ Qualification → `docs/qualification/README.md` |
| *new* | `docs/records/README.md` | Records | CodexUI · Records | ↑ Documentation → `docs/README.md` |
| `docs/records/thread-projects-verification.md` | *unchanged* | Thread Projects Verification | CodexUI · Records | ↑ Records → `docs/records/README.md` |
| `docs/records/timestamp-verification.md` | *unchanged* | Timestamp Verification | CodexUI · Records | ↑ Records → `docs/records/README.md` |
| *new* | `docs/ui-review/README.md` | UI review | CodexUI · UI review | ↑ Documentation → `docs/README.md` |
| `ui-review/CODE-POLISH-ROADMAP.md` | `docs/ui-review/code-polish-roadmap.md` | CodexUI code-polish roadmap | CodexUI · UI review | ↑ UI review → `docs/ui-review/README.md` |
| `ui-review/STATE-MATRIX.md` | `docs/ui-review/state-matrix.md` | CodexUI Current Interaction State Matrix | CodexUI · UI review | ↑ UI review → `docs/ui-review/README.md` |
| `design/ux-decisions/thread-turn-model.md` | `docs/ui-review/thread-turn-model.md` | CodexUI UX Decision: Threads, Turns, and Prompt Admission | CodexUI · UI review | ↑ UI review → `docs/ui-review/README.md` |
| `ui-review/UI-INVENTORY.md` | `docs/ui-review/ui-inventory.md` | CodexUI Current UI Inventory | CodexUI · UI review | ↑ UI review → `docs/ui-review/README.md` |
| `ui-review/UX-DESIGN-DECISIONS.md` | `docs/ui-review/ux-decisions.md` | CodexUI UI/UX Decisions | CodexUI · UI review | ↑ UI review → `docs/ui-review/README.md` |
| *new* | `docs/web/README.md` | Web UI | CodexUI · Web UI | ↑ Documentation → `docs/README.md` |
| `docs/web-1.0-contract.md` | `docs/web/contract-1.0.md` | CodexWebUI 1.0 Contract | CodexUI · Web UI | ↑ Web UI → `docs/web/README.md` |
| `docs/web-qualification.md` | `docs/web/qualification.md` | CodexWebUI qualification | CodexUI · Web UI | ↑ Web UI → `docs/web/README.md` |
| `docs/web-release.md` | `docs/web/release-process.md` | CodexWebUI release-candidate process | CodexUI · Web UI | ↑ Web UI → `docs/web/README.md` |
| `web/README.md` | *unchanged* | CodexWUI | CodexUI · Web UI | ↑ CodexUI → `README.md` |

**New section READMEs (proposed introduction)**

- `docs/architecture/README.md`: Architecture, internal contracts and design analyses of CodexUI.
- `docs/architecture/remediation/README.md`: The Qt architecture remediation: findings ledger and working prompt.
- `docs/architecture/reviews/README.md`: Historical external architecture reviews; findings refer to their captured revision.
- `docs/guides/README.md`: Building CodexUI and using its native interface.
- `docs/qualification/README.md`: The native interactive test suite and its recorded execution results.
- `docs/records/README.md`: Verification records for individual features.
- `docs/ui-review/README.md`: UI review material: inventory, state matrix, UX decisions and the code-polish roadmap.
- `docs/web/README.md`: The CodexWebUI 1.0 contract, its qualification and the release-candidate process.

**Media moves**

- `ui-review/screenshots/` → `docs/media/ui-review/`

**Links outside Markdown pages and from other repositories**

- `SNode.C-Landingpages:CodexUI/README.md @master`
- `SNode.C-Landingpages:FACTS.md @master`
- `SNode.C-Landingpages:SNode.C-orga/README.md @master`

## Packages (sources in `DistributionPackages/site/`)

| Current path | New path | Page title | Banner | ↑ Button → target |
| --- | --- | --- | --- | --- |
| *new* | `docs/README.md` | Documentation | Packages · Documentation | ↑ Packages → `README.md` |
| *new* | `docs/catalogs/README.md` | Catalogs | Packages · Catalogs | ↑ Documentation → `docs/README.md` |
| `docs/mqttsuite-package-options.md` | `docs/catalogs/mqttsuite.md` | MQTTSuite package catalog | Packages · Catalogs | ↑ Catalogs → `docs/catalogs/README.md` |
| `docs/snodec-package-options.md` | `docs/catalogs/snodec.md` | SNode.C package catalog | Packages · Catalogs | ↑ Catalogs → `docs/catalogs/README.md` |
| *new* | `docs/installation/README.md` | Installation | Packages · Installation | ↑ Documentation → `docs/README.md` |
| `docs/debian.md` | `docs/installation/debian.md` | Debian | Packages · Installation | ↑ Installation → `docs/installation/README.md` |
| `docs/fedora.md` | `docs/installation/fedora.md` | Fedora | Packages · Installation | ↑ Installation → `docs/installation/README.md` |
| `docs/install-mqttsuite.md` | — | Install MQTTSuite | *deleted* | — |
| `docs/install-snodec.md` | — | Install SNode.C | *deleted* | — |
| `docs/openwrt.md` | `docs/installation/openwrt.md` | OpenWrt | Packages · Installation | ↑ Installation → `docs/installation/README.md` |
| `docs/linux.md` | `docs/installation/package-selection.md` | DEB and RPM package selection | Packages · Installation | ↑ Installation → `docs/installation/README.md` |
| `docs/raspberrypi.md` | `docs/installation/raspberry-pi-os.md` | Raspberry Pi OS | Packages · Installation | ↑ Installation → `docs/installation/README.md` |
| `docs/rocky.md` | `docs/installation/rocky-linux.md` | Rocky Linux | Packages · Installation | ↑ Installation → `docs/installation/README.md` |
| `docs/ubuntu.md` | `docs/installation/ubuntu.md` | Ubuntu | Packages · Installation | ↑ Installation → `docs/installation/README.md` |
| `docs/maintainers.md` | — | Publication and maintenance | *deleted* | — |
| `docs/architecture.md` | `docs/publication.md` | How publication works | Packages · Documentation | ↑ Documentation → `docs/README.md` |
| `docs/setup.md` | — | Maintainer setup | *deleted* | — |
| `docs/status.md` | *unchanged* | (generated) | Packages · Package status | ↑ Package status → `status/README.md` |
| `docs/troubleshooting.md` | *unchanged* | Troubleshooting | Packages · Documentation | ↑ Documentation → `docs/README.md` |
| `keys/README.md` | *unchanged* | Package signing keys | Packages · Signing keys | ↑ Packages → `README.md` |
| `status/README.md` | *unchanged* | (generated) | Packages · Package status | ↑ Packages → `README.md` |
| `status/mqttsuite.md` | *unchanged* | (generated) | Packages · Package status | ↑ Package status → `status/README.md` |
| `status/snodec.md` | *unchanged* | (generated) | Packages · Package status | ↑ Package status → `status/README.md` |

**New section READMEs (proposed introduction)**

- `docs/README.md`: Installation guides, package catalogs, troubleshooting and how publication works.
- `docs/catalogs/README.md`: The package catalogs of SNode.C and MQTTSuite.
- `docs/installation/README.md`: Installation guides per distribution and how to select DEB and RPM packages.

**Menu buttons**

- Installation guides (debian, ubuntu, fedora, rocky-linux, raspberry-pi-os, openwrt): menu button "Install" (→ #quick-install) becomes "Quick install".
- status/snodec.md, status/mqttsuite.md (generated): remove the "All projects" button; ↑ Package status replaces it.
- Catalogs: menu button "Catalog" (→ in-page #package-catalog) stays: it names an in-page section, not a page.

**Links outside Markdown pages and from other repositories**

- `DistributionPackages:ci/publish/publication.py (docs/status.md)`
- `DistributionPackages:ci/publish/publication.py (docs/troubleshooting.md)`
- `DistributionPackages:ci/publish/publication.py (keys/README.md)`
- `DistributionPackages:ci/publish/publication.py (status/README.md)`
- `DistributionPackages:ci/publish/push.sh (docs/status.md)`
- `DistributionPackages:tests/test_package_pages.py (docs/mqttsuite-package-options.md)`
- `DistributionPackages:tests/test_package_pages.py (docs/snodec-package-options.md)`
- `DistributionPackages:tests/test_package_pages.py (docs/status.md)`
- `DistributionPackages:tests/test_package_pages.py (keys/README.md)`
- `DistributionPackages:tests/test_package_pages.py (status/README.md)`
- `DistributionPackages:tests/test_packaging.py (docs/status.md)`
- `DistributionPackages:tests/test_packaging.py (keys/README.md)`
- `DistributionPackages:tests/test_packaging.py (status/snodec.md)`
- `mqttsuite:docs/readme/install.md @main`
- `snode.c:docs/readme/deployment.md @main`
- `snode.c:docs/readme/install.md @main`

## Flagged items

| Repository | Finding | Recommendation |
| --- | --- | --- |
| snode.c | The two Vite scaffolding READMEs under `src/apps/oauth2/**/vue-frontend-*` ("Vue 3 + TypeScript + Vite") are template boilerplate, not SNode.C documentation. | Exclude from the header (no banner, no button). |
| snode.c | `docs/config-comment-metadata.md` is referenced from source comments in 5 files of `src/tools/snodec-control` (ConfigModel.h, Json.h, Metadata.h, ui/UiState.cpp, tests/SnodecControlConfigParserTest.cpp). | Update those path mentions in the move commit (comment-only change). |
| snode.c, mqttsuite | `docs/assets/` is used by Doxygen (`cmake/doxygen.cmake`) and, in mqttsuite, by `mqttbridge/html/index.html`. | Do not move `docs/assets/`; it is build input, not page media. |
| AISuite, CodexUI | `docs/media/README.md` ("Landing-page assets") documents image sources, it is not a reader page. | Exclude from the header. |
| Packages | `docs/install-snodec.md`, `docs/install-mqttsuite.md`, `docs/setup.md`, `docs/maintainers.md` are 8-line pointer pages with no inbound links. | Delete them instead of moving; their targets (catalogs, publication page, DistributionPackages) are reachable from the section READMEs. Without them a Maintenance section would have one page, so `architecture.md` becomes `docs/publication.md`. |
| Packages | `docs/status.md` is the generated legacy page that keeps old status anchors working. | Keep its path; banner "Package status", ↑ Package status (status/README.md). |
| Packages | `ci/publish/publication.py` builds guide links as `docs/<guide>.md` from its DISTRIBUTIONS table and links `docs/troubleshooting.md`, `docs/status.md`, `keys/README.md`; `ci/publish/push.sh` and `status.sh` name `docs/status.md`; tests reference several paths. | Update renderer, scripts and tests in the DistributionPackages PR. |
| CodexUI | Display name on banners: catalog name `CodexUI` vs page wording `Codex(W)UI`. | Use `CodexUI`. |
| all | `SNodeC/SNode.C-Landingpages` (retiring) links to several moved CodexUI, AISuite and snode.c pages on `master`. | Do not update; the repository is being retired. |
| all | Links from the private `SNodeC/SNode.C-Book` could not be checked. | Maintainer checks the moved paths listed in this plan manually. |

All labels are within 14 characters: AISuite, Architecture, Catalogs, Codex, CodexUI, Design, Documentation, Examples, Frontend SDK, Guides, Installation, Logging, MQTTSuite, Package status, Packages, Qualification, Records, Remediation, Reviews, SNode.C, Signing keys, Tests, Tools, UI review, Web UI, snodec-control.

## Visible menu labels at 160 px

The approved size rule requires shorter visible labels for these currently referenced menus. Destinations, full tooltips and alternative text remain unchanged; 274px menus become 328px rather than shortening. These presentation overrides are authoritative in `plan.yml`, not a second runtime registry.

| Existing visible label | New visible label |
|---|---|
| Native client & server | Client/server |
| SSE & WebSocket | SSE/WebSocket |
| Subprotocol source | Subprotocol |
| Signed packages | Packages |
| Build from source | From source |
| Mapping examples | Examples |
| Mapping schema | Map schema |
| MQTTStore guide | Store guide |
| Projection schema | Projection |
| Grouping & lifecycle | Groups/lifecycle |
| Browser frontend | Browser |
| Selected packages | Selected |

## Owner-approved responsive banner extension

Before Step 2, preserve the 1280×56 desktop banner unchanged and add a 480×72 compact variant. Native `<picture>` selects it at viewport widths up to 640px. Keep the repository graphic and accent; place name and section label on two lines. Header buttons, page paths, section hierarchy, introductions and Up chains are unchanged. This explicitly supersedes the original fixed-banner-only limitation, not the rest of the approved plan.


## Cleanup Step 1 proposals — 2026-10-12

`plan.yml` remains authoritative. These additions are proposed for owner review; no consumer is moved, split, generated or published by Step 1.

- **CodexUI Records:** move both Codex 0.162.1 migration inventory/results documents to `docs/records/`, with Records banners and ↑ Records.
- **CodexUI Findings ledger:** make `docs/architecture/remediation/findings-ledger/README.md` a section with ↑ Remediation. Its six content parts have Findings ledger banners and ↑ Findings ledger: `current-repair-plan.md`, `historical-record.md`, `s5-shared-foundations.md`, `s5-middle-region-audit.md`, `s5-resumed-worktree.md`, and `findings-and-crosswalk.md`.
- The original S5 `##` section measures **203,152 bytes**, so whole-`##` splits alone cannot satisfy the 100 KB ceiling. The proposal splits that oversized section at existing `###` boundaries, preserving all text. The other boundaries are existing `##` sections. Allow room for generated headers in every part; the largest proposed raw content part is the 95,194-byte current repair plan.
- **DistributionPackages:** add `docs/README.md`, `docs/maintainers.md` and `docs/setup.md`, with Documentation banners, the existing Packages gear and infrastructure accent. The root Up button uses the short visible label **Distribution**, pointing directly to DistributionPackages' root; this proposed label fits the unchanged 160 px button. Both desktop and compact banners identify **DistributionPackages** in full. `site/` continues to use the separate Packages policy.
- **Packages:** remove the `docs/status.md` declaration; `docs-audit` flags the legacy file until its Step 2 deletion. `status/README.md` remains the sole status entry page.
- **AISuite/CodexUI media notes:** keep the existing excluded declarations. They get no header, must be reachable from `docs/README.md`, and receive the same link/anchor audit.
- **Audit scope clarification approved by the owner:** the unplanned-page check applies only to header-enrolled repositories. AutoTalk and Book remain unenrolled; their tracked Markdown still receives reachability and link/anchor checks. No exemptions are added.

The Findings ledger parent label is 15 characters, so the existing label guard now accepts up to 15 rather than 14; button size, typography and renderer are unchanged. Longer labels remain rejected. The proposed paths, titles, boundaries and short Distribution label are review decisions for this PR, not an automatic content migration.
