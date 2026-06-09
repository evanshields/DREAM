"""DREAM deal-persistence package. Import the public surface from here."""
from .deal_store import (
    DealStore,
    SQLiteDealStore,
    DealRecord,
    DealNotFound,
    VersionConflict,
    get_deal_store,
    open_sqlite,
    default_db_path,
)

__all__ = [
    "DealStore",
    "SQLiteDealStore",
    "DealRecord",
    "DealNotFound",
    "VersionConflict",
    "get_deal_store",
    "open_sqlite",
    "default_db_path",
]
