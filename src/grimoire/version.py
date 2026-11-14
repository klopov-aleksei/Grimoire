"""Version helpers."""

__version__ = "0.1.0"


def version_info(version: str = __version__) -> tuple[int, int, int]:
    """Parse a ``MAJOR.MINOR.PATCH`` string into a tuple of ints."""
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"invalid version string: {version!r}")
    major, minor, patch = (int(p) for p in parts)
    return major, minor, patch
