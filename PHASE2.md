# Phase 2: verification consolidation

## Governing invariant

Build/test policy lives once in the control repository. A caller owns build
options in `.snodec/repo.yml` and only genuinely project-specific `x-` jobs.
All verification remains read-only. Dependencies are built from source at
API-resolved default-branch commits and installed into job-local staging
prefixes. No dependency binary is downloaded or published.

The Python profile replaces the duplicated native-build workflow; shared C++
source builds replace the duplicated dependency-build jobs rather than leave
two CI implementations in service.
Repository READMEs, licence files, package workflows, secrets, stable product
tags and default branch names are outside this change.

## Preserved behavior and new checks

| Repository | Shared profile | Repository-specific behavior |
| --- | --- | --- |
| snode.c | cpp, tests/apps enabled | 220 tests, including installed-consumer/policy coverage and eight directory-initialization regression scenarios |
| mqttsuite | cpp, snode.c from source | Six new CTest smoke tests: five CLI help contracts and real MQTT CONNECT/SUBSCRIBE/live and retained PUBLISH/PING/DISCONNECT |
| AISuite | cpp, snode.c from source | Codex tests/apps enabled, IPv6/runtime directories; unchanged protocol-generation command as `x-protocol` |
| CodexUI | cpp, snode.c/AISuite from source | Native qualification with Xvfb/offscreen and existing timing policy; web qualification remains `x-web` (Node 22/24.20.0, checksum-pinned Chrome, profiling, production/browser qualification, diagnostics and uploads) |
| AutoTalk | python | Three native platforms, non-audio-device pytest, native build, packaged smoke launch, archive/checksum artifacts; old native-build workflow removed |

The snode.c policy test still strictly restricts package triggers and workflow
paths; it additionally recognizes the thin Verify caller and tests inline event
parsing, duplicate events and unexpected events. No existing test is disabled.
MQTTSuite help deliberately returns 2 when framework bootstrap displays help;
its smoke test verifies this established contract and the actual usage output.

## Evidence scope

Local C++ qualification uses the requested GCC 15.3.0 / Debian trixie container,
real source trees, isolated runtime directories and unprivileged CTest.
The control unit suite executes the actual workflow scripts with real tiny
CMake builds; only network/privileged boundaries are mocked there.

Default-branch green runs cannot be claimed before merging the coordinated
PRs. Windows/macOS native packaging and
CodexUI browser qualification must be confirmed by their GitHub jobs. PRs remain
draft where shared-workflow prerequisites are outstanding. App test fixes were
explicitly deferred by the maintainer, not silently skipped.

## Merge order

1. Merge the control PR and tag-reference follow-up; move the existing `v1.0`
   tag to that reviewed control commit, as explicitly approved by the maintainer.
   Callers use `@v1.0`; no `v1` tag is created and no `Book-*` tag is changed.
2. Merge snode.c and require green default-branch Verify.
3. Merge mqttsuite and AISuite; verify their source dependency builds and tests,
   plus AISuite protocol validation. No release asset is required.
4. CodexUI builds snode.c then AISuite from source; AutoTalk depends only on the
   shared workflow release. The maintainer explicitly deferred their existing
   test defects to later work; tests and failure gates remain enabled.
5. Phase 2 gate: snode.c and mqttsuite are green on their API-reported default
   branches. Phase 3 package migration and Phase 4 README alignment are not started.

## Local results before opening PRs

- Control before dependency-publication removal: 31 tests passed; catalog
  validation, deterministic profile drift,
  `actionlint 1.7.12`, changed C++/CMake formatting and whitespace checks pass.
- snode.c: all 212 tests pass as an unprivileged user (including the updated
  policy test and installed-consumer test).
- mqttsuite: all six new smoke tests pass as an unprivileged user.
- AISuite: all 22 tests pass; the pinned protocol-generation check passes.
- CodexUI: full Xvfb/offscreen CTest discovers 84 cases: 16 failures (12 thread
  pane semantic-no-op paint gates; four grouped 10,000-row timeouts), four Breeze
  cases skipped by their existing availability guard. The same semantic-no-op
  failure reproduces under the old root execution model on unchanged sources;
  no UI test or implementation is weakened here. Native production build passes.
  The preserved web job was structurally compared with its baseline: equal
  except replacing AISuite's hard-coded branch with its default-branch checkout.
- AutoTalk Linux native package build and packaged smoke launch pass locally.
  The full pytest run hangs in prepared-playback qualification; Linux/Windows/macOS
  full qualification is not claimed green. The
  shared matrix preserves the existing jobs; these must pass after release of
  the shared workflow. Local Linux qualification uses Python 3.12 and an
  isolated container, not the user's desktop or audio services.

Logs remain in the implementation workspace's `evidence/` directory; they are
not committed build artifacts or substituted for GitHub default-branch gates.

## Explicitly deferred work

The maintainer requested on 2026-10-10: defer CodexUI and AutoTalk test fixes.
Their tests remain enabled with unchanged correctness gates. Local investigation
was stopped; no application implementation or audio-test skip was added. The
control, snode.c, mqttsuite and AISuite verification results above are unaffected.

Coordinated PRs: [control #2](https://github.com/SNodeC/.github/pull/2),
[snode.c #266](https://github.com/SNodeC/snode.c/pull/266),
[mqttsuite #31](https://github.com/SNodeC/mqttsuite/pull/31),
[AISuite #60](https://github.com/SNodeC/AISuite/pull/60),
[CodexUI #76](https://github.com/SNodeC/CodexUI/pull/76),
[AutoTalk #6](https://github.com/SNodeC/AutoTalk/pull/6).

## Workflow tag decision

The maintainer explicitly requested moving the already existing tag in
SNodeC/.github rather than creating `v1`. The API inventory contains only
`v1.0`; it becomes the workflow reference in the canonical template and all
five callers. This changes only the control-workflow design tag, never any
product version or `Book-*` tag.

## Source-only dependency decision

The maintainer requested removal of development SDKs on 2026-10-10. The active
SNode.C run was cancelled before publication, and no SDK release was created.
Publisher jobs and their write permissions, binary download/export code,
manifest options and the publisher workflow are deleted. Every C++ dependency
is now an explicit ordered `@source` build. The GCC container remains a build
environment only; this does not change the package pipeline or product tags.

Removal verification: all 30 control tests pass, including the real ordered
source-build/CTest/staged-install consumer and source-only negative contracts;
catalog, deterministic profile drift, workflow syntax and whitespace pass.
