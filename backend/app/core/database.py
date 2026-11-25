import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.app.core.config import settings

logger = logging.getLogger("app.core.database")

# Collection names constants
COLLECTION_JOBS = "jobs"
COLLECTION_CANDIDATES = "candidates"
COLLECTION_EVALUATIONS = "evaluations"
COLLECTION_FAIRNESS_AUDITS = "fairness_audits"

EXPECTED_COLLECTIONS = [
    COLLECTION_JOBS,
    COLLECTION_CANDIDATES,
    COLLECTION_EVALUATIONS,
    COLLECTION_FAIRNESS_AUDITS,
]


class FallbackInsertOneResult:
    def __init__(self, inserted_id: Any):
        self.inserted_id = inserted_id


class FallbackInsertManyResult:
    def __init__(self, inserted_ids: List[Any]):
        self.inserted_ids = inserted_ids


class FallbackUpdateResult:
    def __init__(self, matched_count: int, modified_count: int, upserted_id: Any = None):
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id


class FallbackDeleteResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class FallbackCursor:
    """Async cursor interface mimicking Motor's AsyncIOMotorCursor."""

    def __init__(self, items: List[Dict[str, Any]]):
        self._items = items
        self._idx = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._idx < len(self._items):
            item = self._items[self._idx]
            self._idx += 1
            return item
        raise StopAsyncIteration

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        if length is None:
            return list(self._items)
        return list(self._items[:length])


class LocalJSONCollection:
    """
    In-memory and JSON file backed async collection that mirrors Motor collection methods.
    Ensures graceful offline development & deterministic testing without Atlas connectivity.
    """

    def __init__(self, collection_name: str, storage_dir: Path):
        self.name = collection_name
        self.file_path = storage_dir / f"{collection_name}.json"
        self._data: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load fallback file {self.file_path}: {e}")
                self._data = []
        else:
            self._data = []

    def _persist(self):
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to persist fallback store {self.file_path}: {e}")

    def _matches_filter(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        if not query:
            return True
        for key, expected_val in query.items():
            if key == "_id" and str(doc.get("_id")) == str(expected_val):
                continue
            if key == "$or" and isinstance(expected_val, list):
                if not any(self._matches_filter(doc, subq) for subq in expected_val):
                    return False
                continue
            # Handle nested dotted paths (e.g. "evaluations.job_id")
            if "." in key:
                parts = key.split(".")
                curr = doc
                matched = False
                for idx, part in enumerate(parts):
                    if isinstance(curr, list):
                        sub_path = ".".join(parts[idx:])
                        matched = any(
                            self._matches_filter(item, {sub_path: expected_val})
                            for item in curr
                            if isinstance(item, dict)
                        )
                        break
                    elif isinstance(curr, dict):
                        curr = curr.get(part)
                    else:
                        curr = None
                        break
                else:
                    matched = (curr == expected_val)

                if not matched:
                    return False
                continue

            if doc.get(key) != expected_val:
                return False
        return True

    async def find_one(self, filter: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        filter = filter or {}
        for doc in self._data:
            if self._matches_filter(doc, filter):
                return dict(doc)
        return None

    def find(self, filter: Optional[Dict[str, Any]] = None) -> FallbackCursor:
        filter = filter or {}
        matches = [dict(doc) for doc in self._data if self._matches_filter(doc, filter)]
        return FallbackCursor(matches)

    async def insert_one(self, document: Dict[str, Any]) -> FallbackInsertOneResult:
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        self._data.append(doc)
        self._persist()
        return FallbackInsertOneResult(doc["_id"])

    async def insert_many(self, documents: List[Dict[str, Any]]) -> FallbackInsertManyResult:
        inserted_ids = []
        for doc_item in documents:
            doc = dict(doc_item)
            if "_id" not in doc:
                doc["_id"] = str(uuid.uuid4())
            self._data.append(doc)
            inserted_ids.append(doc["_id"])
        self._persist()
        return FallbackInsertManyResult(inserted_ids)

    async def update_one(
        self, filter: Dict[str, Any], update: Dict[str, Any], upsert: bool = False
    ) -> FallbackUpdateResult:
        matched = 0
        modified = 0
        for i, doc in enumerate(self._data):
            if self._matches_filter(doc, filter):
                matched += 1
                if "$set" in update:
                    doc.update(update["$set"])
                    self._data[i] = doc
                    modified += 1
                self._persist()
                return FallbackUpdateResult(matched_count=matched, modified_count=modified)

        if upsert:
            new_doc = dict(filter)
            if "$set" in update:
                new_doc.update(update["$set"])
            if "_id" not in new_doc:
                new_doc["_id"] = str(uuid.uuid4())
            self._data.append(new_doc)
            self._persist()
            return FallbackUpdateResult(
                matched_count=0, modified_count=1, upserted_id=new_doc["_id"]
            )

        return FallbackUpdateResult(matched_count=0, modified_count=0)

    async def delete_one(self, filter: Dict[str, Any]) -> FallbackDeleteResult:
        for i, doc in enumerate(self._data):
            if self._matches_filter(doc, filter):
                del self._data[i]
                self._persist()
                return FallbackDeleteResult(deleted_count=1)
        return FallbackDeleteResult(deleted_count=0)

    async def count_documents(self, filter: Optional[Dict[str, Any]] = None) -> int:
        filter = filter or {}
        return sum(1 for doc in self._data if self._matches_filter(doc, filter))

    async def create_index(self, keys: Any, **kwargs) -> str:
        # No-op in memory index
        return "index_ok"


class LocalJSONDatabase:
    """Mock Database proxying collection requests to LocalJSONCollection."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._collections: Dict[str, LocalJSONCollection] = {}

    def get_collection(self, name: str) -> LocalJSONCollection:
        if name not in self._collections:
            self._collections[name] = LocalJSONCollection(name, self.base_dir)
        return self._collections[name]

    def __getitem__(self, name: str) -> LocalJSONCollection:
        return self.get_collection(name)


class DatabaseManager:
    """Manages Async Motor Client with Atlas TLS, ping verification, and local fallback."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[Any] = None
    is_fallback: bool = False

    async def connect_to_mongo(self) -> None:
        """Initialize MongoDB Atlas connection with TLS/SSL or activate fallback."""
        mongo_uri = settings.MONGODB_URI
        logger.info("Initializing database connection...")

        # Guard: Check if uri contains placeholder or is dummy
        is_placeholder = (
            "sample_user" in mongo_uri
            or "<username>" in mongo_uri
            or "cluster0.mongodb.net" in mongo_uri
        )

        if is_placeholder and settings.ENABLE_LOCAL_FALLBACK_STORE:
            logger.warning(
                "Placeholder MongoDB Atlas URI detected. Activating offline JSON/in-memory fallback store."
            )
            self._activate_fallback()
            return

        try:
            # MongoDB Atlas configuration with certifi TLS and 5s timeout
            client_options = {
                "serverSelectionTimeoutMS": 5000,
                "tlsCAFile": certifi.where(),
            }

            self.client = AsyncIOMotorClient(mongo_uri, **client_options)
            # Startup ping check
            await self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.is_fallback = False
            logger.info(
                f"Successfully connected to MongoDB Atlas database: '{settings.MONGODB_DB_NAME}'"
            )

            # Ensure collections exist and build basic indexes
            await self._init_collections()

        except Exception as e:
            logger.warning(f"MongoDB Atlas connection ping failed ({e}).")
            if settings.ENABLE_LOCAL_FALLBACK_STORE:
                logger.info("Activating Local JSON Fallback Store for offline resilience.")
                self._activate_fallback()
            else:
                logger.error("Local fallback store is disabled. Raising connection error.")
                raise e

    def _activate_fallback(self) -> None:
        """Configures the local JSON/in-memory fallback database."""
        fallback_dir = Path(settings.FALLBACK_DATA_DIR)
        fallback_dir.mkdir(parents=True, exist_ok=True)
        self.db = LocalJSONDatabase(fallback_dir)
        self.is_fallback = True

        # Pre-initialize expected collections
        for col in EXPECTED_COLLECTIONS:
            self.db.get_collection(col)

        logger.info(f"Local JSON fallback active at: {fallback_dir.resolve()}")

    async def _init_collections(self) -> None:
        """Create indexes and ensure collections are accessible."""
        if self.is_fallback or self.db is None:
            return

        try:
            # Candidates collection indexes
            await self.db[COLLECTION_CANDIDATES].create_index("email", unique=True, sparse=True)
            await self.db[COLLECTION_CANDIDATES].create_index("candidate_id", unique=True, sparse=True)
            # Jobs collection indexes
            await self.db[COLLECTION_JOBS].create_index("job_id", unique=True, sparse=True)
            # Evaluations collection indexes
            await self.db[COLLECTION_EVALUATIONS].create_index(
                [("candidate_id", 1), ("job_id", 1)], unique=True
            )
            logger.info("Database collections and indexes initialized successfully.")
        except Exception as idx_err:
            logger.warning(f"Collection index initialization warning: {idx_err}")

    async def close_mongo_connection(self) -> None:
        """Close MongoDB connection gracefully."""
        if self.client:
            self.client.close()
            logger.info("MongoDB Atlas connection closed.")


# Database manager singleton instance
db_manager = DatabaseManager()


def get_database() -> Any:
    """Dependency or accessor for current database (Atlas or Fallback)."""
    if db_manager.db is None:
        # Lazy fallback init if called prior to startup event
        db_manager._activate_fallback()
    return db_manager.db


def get_collection(collection_name: str) -> Any:
    """Helper to fetch a specific collection."""
    db = get_database()
    return db[collection_name]


def is_fallback_active() -> bool:
    """Returns True if the system is currently using the offline JSON fallback store."""
    return db_manager.is_fallback
