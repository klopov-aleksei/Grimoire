# 0005. Settings library

## Status

Accepted.

## Context

Several modules need configuration (database, model server, Telegram). Reading
environment variables in each of them would scatter defaults and parsing, and
a missing value would surface late. One typed settings object, loaded from
`.env` and the environment, keeps this in one place.

## Decision

Use `pydantic-settings`. It gives typed fields and validation at start-up,
secret types that are masked in `repr`, and `.env` loading with the real
environment taking precedence. It is also the usual choice alongside
FastAPI and pydantic, which this project uses later, so no second
validation style is introduced.

## Alternatives considered

- Plain `os.environ` with a dataclass: no extra dependency, but parsing,
  validation and secret masking would all be hand-written.

## Consequences

- One new runtime dependency (`pydantic-settings`, which brings `pydantic`).
- Missing or invalid values fail when `get_settings()` is first called, with
  a message naming the variables.
