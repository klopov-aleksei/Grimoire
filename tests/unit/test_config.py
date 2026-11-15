import pytest

from grimoire.config import ConfigError, Settings, get_settings, load_settings

ALL_VARS = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "LLAMA_BASE_URL",
    "LLAMA_API_KEY",
    "LLAMA_MODEL",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CLUB_CHAT_ID",
    "TELEGRAM_ALLOWED_USER_IDS",
]
REQUIRED = {
    "POSTGRES_PASSWORD": "pw-secret-1",
    "LLAMA_BASE_URL": "http://llm.test/v1",
    "LLAMA_API_KEY": "key-secret-2",
    "LLAMA_MODEL": "m.gguf",
}


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    for name in ALL_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)  # a stray real .env can never be picked up
    get_settings.cache_clear()


def set_required(monkeypatch, **extra):
    for name, value in {**REQUIRED, **extra}.items():
        monkeypatch.setenv(name, value)


def test_defaults(monkeypatch):
    set_required(monkeypatch)
    s = load_settings(None)
    assert s.postgres_user == "grimoire"
    assert s.postgres_db == "grimoire"
    assert s.postgres_host == "127.0.0.1"
    assert s.postgres_port == 5432
    assert s.telegram_bot_token is None
    assert s.telegram_club_chat_id is None
    assert s.telegram_allowed_user_ids == []


def test_overrides_from_environment(monkeypatch):
    set_required(
        monkeypatch,
        POSTGRES_USER="u",
        POSTGRES_DB="d",
        POSTGRES_HOST="db",
        POSTGRES_PORT="6543",
        TELEGRAM_BOT_TOKEN="tok",
        TELEGRAM_CLUB_CHAT_ID="-100123",
    )
    s = load_settings(None)
    assert (s.postgres_user, s.postgres_db, s.postgres_host) == ("u", "d", "db")
    assert s.postgres_port == 6543
    assert s.llama_base_url == "http://llm.test/v1"
    assert s.telegram_bot_token.get_secret_value() == "tok"
    assert s.telegram_club_chat_id == -100123


def test_empty_optional_values_are_none(monkeypatch):
    set_required(monkeypatch, TELEGRAM_BOT_TOKEN="", TELEGRAM_CLUB_CHAT_ID="")
    s = load_settings(None)
    assert s.telegram_bot_token is None
    assert s.telegram_club_chat_id is None


def test_env_file_loading_ignores_unknown(tmp_path):
    env_file = tmp_path / "test.env"
    lines = [f"{k}={v}" for k, v in REQUIRED.items()] + ["UNKNOWN_THING=1", "POSTGRES_DB=fromfile"]
    env_file.write_text("\n".join(lines) + "\n")
    s = load_settings(str(env_file))
    assert s.postgres_db == "fromfile"
    assert s.llama_model == "m.gguf"


def test_environment_beats_file(monkeypatch, tmp_path):
    env_file = tmp_path / "test.env"
    env_file.write_text("POSTGRES_DB=fromfile\n")
    set_required(monkeypatch, POSTGRES_DB="fromenv")
    assert load_settings(str(env_file)).postgres_db == "fromenv"


def test_default_env_file_is_read_from_working_directory(tmp_path):
    (tmp_path / ".env").write_text("\n".join(f"{k}={v}" for k, v in REQUIRED.items()))
    assert load_settings().llama_model == "m.gguf"


def test_missing_values_name_every_variable(monkeypatch):
    monkeypatch.setenv("LLAMA_BASE_URL", "http://x/v1")
    monkeypatch.setenv("LLAMA_MODEL", "m")
    with pytest.raises(ConfigError) as info:
        load_settings(None)
    message = str(info.value)
    assert "Missing required settings: POSTGRES_PASSWORD, LLAMA_API_KEY." in message
    assert ".env.example" in message


def test_missing_error_has_no_secret_values(monkeypatch):
    monkeypatch.setenv("POSTGRES_PASSWORD", "pw-secret-1")
    with pytest.raises(ConfigError) as info:
        load_settings(None)
    assert "pw-secret-1" not in str(info.value)


def test_invalid_int_is_readable(monkeypatch):
    set_required(monkeypatch, POSTGRES_PORT="abc", TELEGRAM_ALLOWED_USER_IDS="1,x")
    with pytest.raises(ConfigError) as info:
        load_settings(None)
    message = str(info.value)
    assert "Invalid settings:" in message
    assert "POSTGRES_PORT" in message
    assert "TELEGRAM_ALLOWED_USER_IDS" in message
    assert "Traceback" not in message


def test_secrets_absent_from_repr_str_and_dump(monkeypatch):
    set_required(monkeypatch, TELEGRAM_BOT_TOKEN="tok-secret-3")
    s = load_settings(None)
    for text in (repr(s), str(s), str(s.model_dump()), s.model_dump_json()):
        for secret in ("pw-secret-1", "key-secret-2", "tok-secret-3"):
            assert secret not in text


def test_database_url_default_scheme_and_quoting(monkeypatch):
    set_required(monkeypatch, POSTGRES_PASSWORD="p@ss:w/rd %1")
    s = load_settings(None)
    assert (
        s.database_url() == "postgresql://grimoire:p%40ss%3Aw%2Frd%20%251@127.0.0.1:5432/grimoire"
    )
    assert s.database_url("postgresql+psycopg").startswith("postgresql+psycopg://")
    assert "p@ss" not in repr(s)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("", []), ("1,2,3", [1, 2, 3]), (" 1 , 2,, 3 ", [1, 2, 3]), ("-5", [-5])],
)
def test_allowed_user_ids_parsing(monkeypatch, raw, expected):
    set_required(monkeypatch, TELEGRAM_ALLOWED_USER_IDS=raw)
    assert load_settings(None).telegram_allowed_user_ids == expected


def test_allowed_user_ids_accepts_list_in_code():
    s = Settings(
        _env_file=None, telegram_allowed_user_ids=[7], **{k.lower(): v for k, v in REQUIRED.items()}
    )
    assert s.telegram_allowed_user_ids == [7]


def test_get_settings_is_cached(monkeypatch):
    set_required(monkeypatch)
    assert get_settings() is get_settings()
