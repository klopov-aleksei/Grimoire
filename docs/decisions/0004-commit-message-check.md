# 0004. Commit message check

## Status

Accepted.

## Context

The project uses Conventional Commits (`type(scope): description`). A check on
the commit message keeps the history uniform and catches mistakes before they
reach the remote. The project already uses pre-commit for linting and
formatting, so the check should fit into the same tool and require no extra
runtime.

## Decision

Use the `conventional-pre-commit` hook from the pre-commit framework, run at
the `commit-msg` stage. Allowed types: feat, fix, docs, chore, refactor, test,
build, ci. `make install` installs both the `pre-commit` and `commit-msg` hook
types.

## Alternatives considered

- commitizen: a full release and changelog tool; more than is needed for a
  message check and adds a second configuration surface.
- commitlint: requires Node.js and npm packages in a Python project.

## Consequences

- A commit with a non-conforming message is rejected locally.
- Hooks are not enforced for contributors who skip `make install`; CI can
  repeat the check later if needed.
- The hook revision is pinned in `.pre-commit-config.yaml` and updated with
  `pre-commit autoupdate`.
