"""DREAM deal-persistence package. Import the public surface from here."""
from .deal_store import (
    DealStore,
    SQLiteDealStore,
    DealRecord,
    DealNotFound,
    VersionConflict,
    get_deal_store,
)

__all__ = [
    "DealStore",
    "SQLiteDealStore",
    "DealRecord",
    "DealNotFound",
    "VersionConflict",
    "get_deal_store",
]
