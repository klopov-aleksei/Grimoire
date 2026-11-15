# tests

- `unit/`: fast tests with no external services. They run by default
  (`make test`) with the 90% coverage gate, in CI on Linux and macOS.
- `integration/`: tests that need Docker services or the LLM. They are marked
  `integration` and deselected by default locally; run them with
  `make test-integration` after `make up`.

CI policy for integration tests: the database tests run on Linux only, in a
separate job against a `pgvector/pgvector:pg17` service container (GitHub
service containers need an Ubuntu runner). The job is added with the database
issue; a commented placeholder is in `.github/workflows/ci.yml`. Tests that
need the LLM server are never run in CI.
