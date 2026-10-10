# Phase 2: verification consolidation

## Governing invariant

Build/test policy lives once in the control repository. A caller owns build
options in `.snodec/repo.yml` and only genuinely project-specific `x-` jobs.
Nothing grants build/test code a release write token. The separate development
publisher executes control-owned orchestration, not repository build scripts.

The approved extensions add the missing Python profile and SDK handoff;
reduction alone cannot supply those capabilities. They replace the duplicated
native/source-build jobs rather than leave two CI implementations in service.
Repository READMEs, licence files, package workflows, secrets, stable product
tags and default branch names are outside this change.

## Preserved behavior and new checks

| Repository | Shared profile | Repository-specific behavior |
| --- | --- | --- |
| snode.c | cpp, tests/apps enabled | Existing 212 tests, including installed-consumer/policy coverage; separate default-branch SDK publisher |
| mqttsuite | cpp, snode.c SDK | Six new CTest smoke tests: five CLI help contracts and real MQTT CONNECT/SUBSCRIBE/live and retained PUBLISH/PING/DISCONNECT; separate SDK publisher |
| AISuite | cpp, snode.c SDK | Codex tests/apps enabled, IPv6/runtime directories; unchanged protocol-generation command as `x-protocol`; publisher requires both Verify and protocol validation |
| CodexUI | cpp, snode.c/AISuite SDKs | Native qualification with Xvfb/offscreen and existing timing policy; web qualification remains `x-web` (Node 22/24.20.0, checksum-pinned Chrome, profiling, production/browser qualification, diagnostics and uploads) |
| AutoTalk | python | Three native platforms, non-audio-device pytest, native build, packaged smoke launch, archive/checksum artifacts; old native-build workflow removed |

The snode.c policy test still strictly restricts package triggers and workflow
paths; it additionally recognizes the thin Verify caller and tests inline event
parsing, duplicate events and unexpected events. No existing test is disabled.
MQTTSuite help deliberately returns 2 when framework bootstrap displays help;
its smoke test verifies this established contract and the actual usage output.

## Evidence scope

Local C++ qualification uses the requested GCC 15.3.0 / Debian trixie container,
real source trees, isolated runtime directories and unprivileged CTest. SDK
relocation is tested in a separate container with only extracted installs, no
producer staging/build paths: the existing SNode.C installed consumer runs and
CodexUI configures/builds against relocated snode.c and AISuite exports.
The control unit suite executes the actual workflow scripts with real tiny
CMake builds; only network/privileged boundaries are mocked there.

Default-branch green runs and actual GitHub development publication cannot be
claimed before merging the coordinated PRs. Windows/macOS native packaging and
CodexUI browser qualification must be confirmed by their GitHub jobs. PRs remain
draft where these prerequisites or shared-workflow/SDK prerequisites are outstanding. App test fixes were
explicitly deferred by the maintainer, not silently skipped.

## Merge order

1. Merge the control PR; maintainer publishes its reviewed version and moving
   `v1` in **SNodeC/.github**. No tag is created by this implementation task.
2. Merge snode.c; require green default-branch Verify and a published `dev` SDK.
3. Merge mqttsuite and AISuite; require green Verify, AISuite protocol validation
   and published SDKs. Stale/missing SDKs fail closed rather than rebuild silently.
4. CodexUI follows its SDK prerequisites; AutoTalk depends only on the shared
   workflow release. The maintainer explicitly deferred their existing test
   defects to later work; tests and failure gates remain enabled.
5. Phase 2 gate: snode.c and mqttsuite are green on their API-reported default
   branches. Phase 3 package migration and Phase 4 README alignment are not started.

## Local results before opening PRs

- Control: 31 tests pass; catalog validation, deterministic profile drift,
  `actionlint 1.7.12`, changed C++/CMake formatting and whitespace checks pass.
- snode.c: all 212 tests pass as an unprivileged user (including the updated
  policy test and installed-consumer test).
- mqttsuite: all six new smoke tests pass as an unprivileged user.
- AISuite: all 22 tests pass; the pinned protocol-generation check passes.
- Relocated real SDKs: the existing SNode.C installed consumer runs, and CodexUI
  configures/builds with only extracted snode.c/AISuite installs visible.
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
