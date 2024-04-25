from importlib import metadata

try:
    __version__ = metadata.version("vogmidea")
except metadata.PackageNotFoundError:
    __version__ = "UNKNOWN"
