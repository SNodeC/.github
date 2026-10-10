# Contributing to SNode.C projects

Choose the owning repository from the [organization profile](https://github.com/SNodeC). Use that project's **Contribute** menu for its issue tracker, build instructions and engineering guidelines. Report the revision, platform, steps to reproduce and expected/actual behavior; remove credentials, private configuration and private conversation data from reports.

Keep changes scoped to their owning project. Do not create, change or require licence files, move release tags, or change package/security infrastructure without explicit maintainer approval. For a private vulnerability report, follow [SECURITY.md](SECURITY.md), not a public issue.

## Control repository

Open control-repository pull requests in [SNodeC/.github](https://github.com/SNodeC/.github/pulls). Repository identity belongs in `catalog.yml`; build settings belong in the owning repository's manifest. Edit the profile's generator inputs, not generated `profile/README.md`.

Run the generator and checks described in [README.md](README.md). Cite sources for identity changes; use `confirm: true` for summaries needing maintainer confirmation. The [scoped README frame](templates/readme-frame.md) applies only to the four repositories already participating in the current documentation phase.
