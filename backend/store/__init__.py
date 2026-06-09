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
from .user_store import (
    SQLiteUserStore,
    UserRecord,
    UserNotFound,
    UserExists,
    get_user_store,
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
    "SQLiteUserStore",
    "UserRecord",
    "UserNotFound",
    "UserExists",
    "get_user_store",
]
