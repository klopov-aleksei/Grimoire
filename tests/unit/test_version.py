import pytest

import grimoire
from grimoire import version_info


def test_version_info_default_matches_dunder_version():
    assert ".".join(map(str, version_info())) == grimoire.__version__


def test_version_info_parses_explicit_string():
    assert version_info("1.2.3") == (1, 2, 3)


@pytest.mark.parametrize("bad", ["1.2", "a.b.c", "1.2.3.4", ""])
def test_version_info_rejects_invalid(bad):
    with pytest.raises(ValueError):
        version_info(bad)
