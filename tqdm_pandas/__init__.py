from .patcher import patch_pandas, unpatch_pandas

try:
    from ._version import version as __version__
except ImportError:
    # Fallback if _version.py doesn't exist
    __version__ = "unknown"