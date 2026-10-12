# SNodeC control repository

This repository owns the organization catalog and the [profile](profile/README.md) generated from it. Brand tokens define the shared accents, contrast pairs and glyphs. The shared Verify workflow provides reusable, manifest-driven verification. The navigation plan, page-header generator and `docs-audit` keep documentation paths, generated navigation and tracked-page reachability reviewable from one control point.

## Documentation

- [Navigation generator and documentation audit](navigation/README.md)
- [Navigation plan review](navigation/PLAN.md)
- [Brand tokens and glyphs](brand/README.md)
- [Navigation assets and provenance](brand/navigation/README.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Historical records](history/README.md)

## Local checks

Python 3 with PyYAML is sufficient for catalog/profile work. CMake, Ninja, Git
and a C++ compiler are also needed for the workflow boundary integration tests.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python tools/snodec_sync check
python tools/snodec_sync profile
python -m unittest discover -s tests -v
python tools/snodec_sync profile --output /tmp/snodec-profile.md
diff -u profile/README.md /tmp/snodec-profile.md
```

`check` reports all catalog validation errors and exits non-zero.
`profile` validates before writing. Both commands accept `--catalog`; rendering
also accepts `--metadata` and `--output`. Defaults resolve relative to this
repository, not the working directory.

## Authorities

- `catalog.yml`: identity, classification, ecosystem edges and lifecycle only.
  Entry order controls row order; areas always use the prescribed organization order.
- `profile/github-metadata.json`: checked-in GitHub API evidence for default
  branches, workflow paths and release tags. No timestamps or network requests
  enter rendering. Update this snapshot deliberately when those facts change;
  profile generation is not a live inventory sync. Missing workflow/release
  fields never invent badges or version numbers: the compact Status cell omits an unavailable CI badge and uses a dash for an unavailable release.
- `brand/tokens.yml`: one authority for light/dark text and tinted backgrounds,
  plus area-to-accent mappings. Products may override their area's accent.
  CodexUI inherits Applications' interface amber; app entries never use `accent`.
- `brand/glyphs/`: seven 24×24, 1.5-unit, `currentColor` stroke glyphs.
- `templates/`: the exact future CI caller and commented build-only manifest.
  Forks are not enrolled.

No project count is generated in the organization profile. Retiring/retired entries are catalog classifications only: this repository does not archive anything. Upstream forks are not enrolled in shared Verify.

Workflow badges show an existing workflow, **not** a promise of push/PR testing.
The snode.c and mqttsuite release-package workflows remain tag-triggered;
shared Verify callers are manual-only. The control repository's CI
path is included because that workflow is delivered here.

## Shared Verify

`.github/workflows/verify.yml` remains `workflow_call`-only and read-only. The
manifest is the single authority for build options; the catalog holds identity.
Preparation validates the manifest before selecting the C++ container or native
Python matrix. The canonical caller uses only `workflow_dispatch`: full
Verify does not run on ordinary pushes, PRs or version-tag pushes. Heavy
release builds/tests stay in the existing tag-triggered package pipeline.
The control repository retains its lightweight catalog/unit/drift checks. Its own `CI` workflow is currently disabled by owner decision; changing its files does not authorize re-enabling it.
Every checkout uses the exact PR head SHA, otherwise the event
SHA, with no persisted credentials. C++ includes recursive submodules.

### C++

The default container is `gcc:15.3.0-trixie`. Extra apt packages, CMake arguments,
CTest arguments and optional `ctest_launcher` are argument lists, not shell
fragments. `parallel` controls build workers. Non-secret `env` values reach
builds and tests; reserved GitHub/runner/token variables are rejected.

Ordered dependencies accept only `<repository>@source`: resolve the default
branch via the GitHub API, fetch its exact commit, then build and stage the
install in dependency order. The staged installs provide `CMAKE_PREFIX_PATH`
and `LD_LIBRARY_PATH` to later builds. The read token is removed before
executing build code. No dependency binaries are downloaded or published.

The caller configures with Ninja, builds, runs CTest as an unprivileged `snodec`
user when enabled (`--no-tests=error`), then installs into a staging prefix.
`CMAKE_INSTALL_LIBDIR=lib` and dependency paths are owned by the workflow.
Linux jobs use `ubuntu-24.04` runners. Preparation has a 10-minute timeout and hygiene a 15-minute timeout. C++ builds default to 60 minutes; the optional integer `ci.timeout_minutes` accepts 10–180 minutes for the `cpp` profile only. Each Python matrix job has a fixed 60-minute timeout.

Runtime directories and IPv6 remain opt-in; IPv6 adds NET_ADMIN, the sysctl and
`fd00::1/128` on a dummy interface. snode.c enables its existing component, unit,
policy and staged installed-consumer tests explicitly in its manifest.

### Python

AutoTalk's existing qualification becomes the shared `python` profile:
Python 3.12 on Ubuntu 24.04, Windows 2025 and macOS 15, editable development
install, pytest excluding physical audio devices, native package build,
packaged smoke launch and archive/checksum upload. The manifest supplies only
local project arguments, build/launch commands and artifact paths. Matrix
failures do not cancel the other platforms. Package qualification can still run
after test failures, without turning a failed test job green.

### Independent hygiene

Whitespace checks run against the PR base or previous push commit (empty tree
on the initial commit). An independent job also checks changed C/C++ and CMake
files against existing repository formatting policies. It runs `docs-audit` over all tracked documentation using tooling checked out at the exact called workflow commit. It neither invents a style where none exists nor performs unreliable external-URL probes. Failures are collected rather than stopping at the first file. This job still runs when compilation/tests fail.

### Verify releases and caller pins

A changed `verify.yml` ships at a new `vX.Y` tag after review and merge. Existing tags are never moved. The current release is `v1.2`, commit `37b76768a383ea28c03fd9e7ceda7eecf3007c0a`. Callers pin the full release commit SHA with a `# vX.Y` comment; they pass no secrets unless Verify actually reads one (currently none). Product CI remains `workflow_dispatch`-only by owner decision, independent of the existing version-tag package pipelines.

Every Verify release updates `templates/ci.yml` and all callers to the new tag's full commit SHA in the same release step, once the new tag exists. The template is the canonical onboarding example, not a mutable-tag shortcut. The documented release step keeps the template current without a network-dependent newest-tag test.

Tests execute the actual inline workflow scripts, including ordered source
builds and a real CMake/CTest/staged-install consumer, Python commands and
hygiene aggregation. Boundary tests also assert that binary dependency modes,
publication options and publisher workflows are absent or rejected.

Repository README frames and generated navigation are governed by the [navigation plan](navigation/README.md). Package/release publication remains a separate responsibility.

Historical rollout and design records live only in [history](history/README.md); they are not current release policy. See also [brand values](brand/README.md), [contributing](CONTRIBUTING.md) and [security](SECURITY.md).
