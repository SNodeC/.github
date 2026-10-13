<!-- snodec:begin organization -->
<p><a href="https://github.com/SNodeC" title="SNodeC organization"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/media/nav/organization-dark.svg"><img align="right" src="docs/media/nav/organization-light.svg" alt="SNodeC organization" title="SNodeC organization" width="160" height="28"></picture></a><br clear="all"></p>
<!-- snodec:end organization -->

# SNodeC control repository

This repository owns the organization catalog and the [profile](profile/README.md) generated from catalog rows and authored prose. Brand tokens define the shared accents, contrast pairs and glyphs. The shared Verify workflow provides reusable, manifest-driven verification. The navigation plan, page-header generator and optional `docs-audit` command keep documentation paths, generated navigation and tracked-page reachability reviewable from one control point.

## Documentation

- [Navigation generator](navigation/README.md)
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
git diff --exit-code profile/README.md
python -m unittest discover -s tests -v
python tools/snodec_sync profile --output /tmp/snodec-profile.md
diff -u profile/README.md /tmp/snodec-profile.md
```

`check` reports all catalog validation errors and exits non-zero.
`profile` validates before writing. Edit `catalog.yml` for rows and `profile/template.md` for prose, never generated `profile/README.md`. Both commands accept `--catalog`; rendering
also accepts `--metadata` and `--output`. Defaults resolve relative to this
repository, not the working directory.

## Authorities

- `catalog.yml`: identity, classification, ecosystem edges and lifecycle only.
  Entry order controls row order. Optional `tier` selects `product`, `learn`, `install` or the default `secondary`; product rows require single-line `title` and `purpose`. Learn titles are optional. Boolean `student` places entries in Student projects; a product with `student: true` also retains its product row. Product tiers require product/app kind; secondary products require `student: true`.
- [profile/template.md](profile/template.md): authored profile prose and exactly one standalone marker each for Products, Learn and More rows. `snodec_sync profile` combines it with `catalog.yml`; `profile/README.md` remains generated.
- `profile/github-metadata.json`: checked-in GitHub API evidence for default
  branches, workflow paths and release tags. No timestamps or network requests
  enter rendering. Update this snapshot deliberately when those facts change;
  profile generation is not a live inventory sync. Missing workflow/release
  fields never invent badges or version numbers: product Status cells omit unavailable CI badges, and product navigation omits unavailable Releases links.
- `brand/tokens.yml`: one authority for light/dark text and tinted backgrounds,
  plus area-to-accent mappings. Products may override their area's accent.
  CodexUI inherits Applications' interface amber; app entries never use `accent`.
- `brand/glyphs/`: seven 24×24, 1.5-unit, `currentColor` stroke glyphs.
- `templates/`: the exact future CI caller and commented build-only manifest.
  Forks are not enrolled.

After the existing CI succeeds on a push to `main` (including a merged pull request) or a manual run on `main`, it sends `sync-organization-profile` to `SNodeC/.github-private`. That private repository owns the publication workflow: it pulls the current public `main` profile and assets, validates the generated profile and commits changes only when needed. Unmerged pull requests run checks without dispatching or changing the member view. Dispatch requires this repository's `ORG_PROFILE_TOKEN` secret, a fine-grained token with Contents read/write access to `.github-private`. The private workflow also supports a manual trigger. The catalog, template and generator remain authoritative here.

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
The control repository runs catalog and generator unit tests on pushes, pull requests and manual dispatches, as approved by the owner. Workflow enablement remains an owner decision.
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
files against existing repository formatting policies. Documentation and presentation assets are not verification gates. It neither invents a style where none exists nor performs unreliable external-URL probes. Failures are collected rather than stopping at the first file. This job still runs when compilation/tests fail.

### Shared Verify updates

The five product callers and `templates/ci.yml` use `verify.yml@main`, following the API-verified default branch of this control repository. A merged shared-workflow change is used by their next manually started CI runs; it does not start those runs. Callers pass no secrets unless Verify actually reads one (currently none). Product CI remains `workflow_dispatch`-only, independent of version-tag package pipelines.

Existing tags are historical snapshots and are never moved. Page-header, menu and profile generation are separate from build CI; documentation changes require neither a Verify release nor caller updates. `docs-audit` is optional local/PR review tooling and is never a build, signing or publication gate.

Tests execute the actual inline workflow scripts, including ordered source
builds and a real CMake/CTest/staged-install consumer, Python commands and
hygiene aggregation. Boundary tests also assert that binary dependency modes,
publication options and publisher workflows are absent or rejected.

Repository README frames and generated navigation are governed by the [navigation plan](navigation/README.md). Package/release publication remains a separate responsibility.

Historical rollout and design records live only in [history](history/README.md); they are not current release policy. See also [brand values](brand/README.md), [contributing](CONTRIBUTING.md) and [security](SECURITY.md).

Verify no longer enforces documentation. Existing `v1.0`–`v1.3` tags remain unchanged.
