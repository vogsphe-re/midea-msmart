from importlib import metadata

try:
    __version__ = metadata.version("msmart-vog")
except metadata.PackageNotFoundError:
    __version__ = "UNKNOWN"
