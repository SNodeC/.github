# Contributing to SNode.C projects

Choose the owning repository from the [organization profile](https://github.com/SNodeC). Use that project's **Contribute** menu for its issue tracker, build instructions and engineering guidelines. Report the revision, platform, steps to reproduce and expected/actual behavior; remove credentials, private configuration and private conversation data from reports.

Keep changes scoped to their owning project. Do not create, change or require licence files, move release tags, or change package/security infrastructure without explicit maintainer approval. For a private vulnerability report, follow [SECURITY.md](SECURITY.md), not a public issue.

## Control repository

Open control-repository pull requests in [SNodeC/.github](https://github.com/SNodeC/.github/pulls). Repository identity belongs in `catalog.yml`; build settings belong in the owning repository's manifest. The profile is generated from `catalog.yml` (rows) and `profile/template.md` (prose). Edit those two files, never `profile/README.md`. Optional `tier` selects product, learn, install or secondary; `title` and `purpose` are single-line product display text; boolean `student` adds an entry to Student projects. Product rows require title/purpose and product/app kind; learn titles are optional, and secondary products require `student: true`.

Run the generator and checks described in [README.md](README.md). Cite sources for identity changes; use `confirm: true` for summaries needing maintainer confirmation. The [scoped README frame](templates/readme-frame.md) applies only to the four repositories explicitly enrolled in that frame.
