"""Backward-compatible namespace for the legacy import package."""

from codice_fiscale.metadata import (
    __author__,
    __copyright__,
    __description__,
    __license__,
    __title__,
    __version__,
)

from . import codicefiscale, partitaiva

__all__ = [
    "__author__",
    "__copyright__",
    "__description__",
    "__license__",
    "__title__",
    "__version__",
    "codicefiscale",
    "partitaiva",
]
