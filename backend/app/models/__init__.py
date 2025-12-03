from .run import Run
from .workload import Workload
# If you have these models in your repo, keep these imports;
# if any of these files don't exist, you can safely comment/remove that line.
try:
    from .server import Server
except ImportError:  # pragma: no cover
    Server = None  # type: ignore

try:
    from .storage import Storage
except ImportError:  # pragma: no cover
    Storage = None  # type: ignore

try:
    from .network import Network  # only if app/models/network.py exists
except ImportError:  # pragma: no cover
    Network = None  # type: ignore

try:
    from .application import Application  # only if you have this model
except ImportError:  # pragma: no cover
    Application = None  # type: ignore


__all__ = [
    "Run",
    "Workload",
    "Server",
    "Storage",
    "Network",
    "Application",
]
