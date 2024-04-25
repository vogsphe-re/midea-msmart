from importlib import metadata

try:
    __version__ = metadata.version("msmartvog")
except metadata.PackageNotFoundError:
    __version__ = "UNKNOWN"
