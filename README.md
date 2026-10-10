# SNodeC control repository

Phase 1 establishes the organization catalog, generated profile, accessible brand
tokens and the reusable C++ Verify workflow. It does **not** enroll repositories,
rewrite their READMEs, change the package pipeline or create release tags.

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

The supplied named list has 33 existing repositories plus this new control
repository. Every named entry is included. No project count is generated in the
organization profile. Retiring/retired entries are catalog classifications only:
this repository does not archive anything. All six upstream forks remain active.

Workflow badges show an existing workflow, **not** a promise of push/PR testing.
The snode.c and mqttsuite release-package workflows remain tag-triggered;
shared Verify callers are manual-only. The control repository's CI
path is included because that workflow is delivered here.

## Shared Verify (Phase 2)

`.github/workflows/verify.yml` remains `workflow_call`-only and read-only. The
manifest is the single authority for build options; the catalog holds identity.
Preparation validates the manifest before selecting the C++ container or native
Python matrix. The canonical caller uses only `workflow_dispatch`: full
Verify does not run on ordinary pushes, PRs or version-tag pushes. Heavy
release builds/tests stay in the existing tag-triggered package pipeline.
The control repository retains its lightweight catalog/unit/drift checks.
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
files against existing repository formatting policies and changed Markdown's
local file links. It neither invents a style where none exists nor performs
unreliable external-URL probes. Failures are collected rather than stopping at
the first file. This job still runs when compilation/tests fail.

### Coordinated rollout

Merge the control workflow change first. The maintainer then publishes the
reviewed shared-workflow commit by moving the existing `v1.0` tag in
**SNodeC/.github**. Callers and the canonical template use `@v1.0`; no new
`v1` tag is created. The maintainer explicitly approved moving this existing tag.
Merge callers without dispatching Verify. Release qualification is triggered
through the existing product version-tag package pipeline. Consumers build
their ordered dependencies from source, with no release-asset prerequisites.
AutoTalk can follow the control workflow independently. No duplicate old/native
build jobs remain after migration.

Tests execute the actual inline workflow scripts, including ordered source
builds and a real CMake/CTest/staged-install consumer, Python commands and
hygiene aggregation. Boundary tests also assert that binary dependency modes,
publication options and publisher workflows are absent or rejected.

Repository README frames are **Phase 4**, not Phase 2. Package/release/site,
figure, ecosystem and org-sync lanes remain separate later phases.

See [Phase 2 evidence and rollout](PHASE2.md), [Phase 1 evidence](EVIDENCE.md),
[brand values](brand/README.md), [contributing](CONTRIBUTING.md) and
[security](SECURITY.md).
