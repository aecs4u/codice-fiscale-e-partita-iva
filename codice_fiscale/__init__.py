from codice_fiscale.metadata import (
    __author__,
    __copyright__,
    __description__,
    __license__,
    __title__,
    __version__,
)

__all__ = [
    "__author__",
    "__copyright__",
    "__description__",
    "__license__",
    "__title__",
    "__version__",
]

# Import new modules to make them available
try:
    from . import partitaiva  # noqa: F401
    __all__.append("partitaiva")
except ImportError:
    pass

try:
    from . import api  # noqa: F401
    __all__.append("api")
except ImportError:
    pass
