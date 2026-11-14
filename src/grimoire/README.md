# grimoire

Top-level package.

`config.py` holds the typed settings (`Settings`) and the cached accessor
`get_settings()`. Values come from `.env` in the working directory and from
environment variables (the environment wins); no other module reads the
environment. Missing required values raise `ConfigError` naming the variables,
and secrets are masked in `repr`. `Settings.database_url()` builds the
connection URL with the password quoted; the driver scheme is a parameter.
