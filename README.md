# Grimoire (Гримуар)

Grimoire is an AI assistant for a board-game club. It is a Telegram bot that
answers rules questions with page citations from the official Russian
rulebooks, suggests games from the club's own shelf, and keeps the club's
session log and leaderboard.

## Status

Early stage: planning only. There is no code in this repository yet.

## Planned stack

- Python, FastAPI (async), aiogram for the Telegram bot
- PostgreSQL with pgvector, Elasticsearch for retrieval
- LangChain / LangGraph for the answering pipeline
- A local LLM served by llama.cpp `llama-server`
- Docker Compose for local deployment

## Use of BoardGameGeek data

- This is a personal, non-commercial student project: no ads, no payments,
  no resale.
- The bot is private and used by one club of a few dozen people at most.
- The BoardGameGeek XML API is used for game metadata (names, including
  alternate names; mechanics; designers; expansions) for the games on the
  club's shelf and the group's favourites: dozens to a few hundred games.
- Each game is fetched once. Results are cached in the project's own
  database, and requests are rate-limited and kept to a minimum.
- Requests are made server-side only.
- The data is not redistributed or offered to other applications.
- The API token is kept out of the repository.

## Data and copyright

Rulebooks and third-party data are not stored in this repository.

## License

Apache License 2.0, see [LICENSE](LICENSE).
