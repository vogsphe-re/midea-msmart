from importlib import metadata

try:
    __version__ = metadata.version("msmart_vog")
except metadata.PackageNotFoundError:
    __version__ = "UNKNOWN"
