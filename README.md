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
  fields produce empty cells, not invented badges or version numbers.
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
In particular, snode.c and mqttsuite still show their current release-package
workflow until callers are added in a later phase. The control repository's CI
path is included because that workflow is delivered here.

## Reusable C++ Verify

`.github/workflows/verify.yml` is `workflow_call`-only. A preparation job
validates the caller's manifest and selects the container/capabilities before the
`snodec / cpp` job is scheduled. Checkouts use the exact PR head SHA (otherwise
the event SHA); checkout credentials are not persisted. The C++ checkout includes
submodules.

The default image is `gcc:15.3.0-trixie`. Base packages are the specified build
dependencies plus Python 3 for stdlib command orchestration. Extra packages must
be individual package names. CMake and CTest arguments are passed as argument
lists, never evaluated as shell fragments.

Dependencies support `<SNodeC-repository>@source` only, in declared order.
The GitHub API supplies each default branch and resolves it to a commit before
checkout; source submodules are included. Each dependency is configured in
Release mode with `BUILD_TESTING=OFF`, built and installed into its own staging
prefix. Previously staged dependencies flow through `CMAKE_PREFIX_PATH` and
`LD_LIBRARY_PATH` (`lib` and `lib64`). The API token is removed from the
environment before any dependency/caller build code runs.

The caller is configured with Ninja and its `cmake_options`, built, tested
when enabled, and installed into a staging prefix. The workflow owns staging
prefixes and the dependency search path; it sets `CMAKE_INSTALL_LIBDIR=lib`.
Runtime directories and the snodec group are opt-in. IPv6 is also opt-in and
enables NET_ADMIN, the IPv6 sysctl and a dummy interface with `fd00::1/128`.
Whitespace checking runs even after a build/test failure, against the PR base
or the previous push commit (the empty tree for an initial commit).

Tests execute the actual inline workflow scripts, including a real two-dependency
CMake/CTest/install boundary fixture. They do not duplicate the implementation.
The control CI runs catalog checks, tests and profile drift independently so
one failure does not suppress subsequent checks.

After merge, **the maintainer** publishes `v1.0.0` and the moving `v1`.
Templates are not installed into other repositories in this phase. Other CI
profiles, organization sync PRs, package/release/site/figure lanes and dev SDK
assets belong to later phases.

See [evidence](EVIDENCE.md), [brand values](brand/README.md),
[contributing](CONTRIBUTING.md) and [security](SECURITY.md).
