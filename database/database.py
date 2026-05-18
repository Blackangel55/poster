"""
database.py — MongoDB database handler for OTT Poster Bot
Uses motor (async MongoDB driver) for non-blocking DB operations.
"""

import logging
import motor.motor_asyncio

from config import DB_URI, DB_NAME

log = logging.getLogger(__name__)


class Database:

    def __init__(self, db_uri: str, db_name: str):
        self.client   = motor.motor_asyncio.AsyncIOMotorClient(db_uri)
        self.db        = self.client[db_name]

        # Collections
        self.users        = self.db["users"]
        self.banned       = self.db["banned_users"]
        self.admins       = self.db["admins"]
        self.fsub         = self.db["fsub_channels"]
        self.image_cache  = self.db["image_cache"]

    # ─── USER MANAGEMENT ─────────────────────────────────────────────────────

    async def user_exists(self, user_id: int) -> bool:
        found = await self.users.find_one({"_id": user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        if not await self.user_exists(user_id):
            await self.users.insert_one({"_id": user_id})
            log.info("New user added: %s", user_id)

    async def del_user(self, user_id: int):
        await self.users.delete_one({"_id": user_id})

    async def get_all_users(self) -> list[int]:
        docs = await self.users.find().to_list(length=None)
        return [doc["_id"] for doc in docs]

    async def total_users(self) -> int:
        return await self.users.count_documents({})

    # ─── BAN MANAGEMENT ──────────────────────────────────────────────────────

    async def is_banned(self, user_id: int) -> bool:
        found = await self.banned.find_one({"_id": user_id})
        return bool(found)

    async def ban_user(self, user_id: int):
        if not await self.is_banned(user_id):
            await self.banned.insert_one({"_id": user_id})
            log.info("User banned: %s", user_id)

    async def unban_user(self, user_id: int):
        await self.banned.delete_one({"_id": user_id})
        log.info("User unbanned: %s", user_id)

    async def get_banned_users(self) -> list[int]:
        docs = await self.banned.find().to_list(length=None)
        return [doc["_id"] for doc in docs]

    # ─── ADMIN MANAGEMENT ────────────────────────────────────────────────────

    async def is_admin(self, user_id: int) -> bool:
        found = await self.admins.find_one({"_id": user_id})
        return bool(found)

    async def add_admin(self, user_id: int):
        if not await self.is_admin(user_id):
            await self.admins.insert_one({"_id": user_id})
            log.info("Admin added: %s", user_id)

    async def del_admin(self, user_id: int):
        await self.admins.delete_one({"_id": user_id})
        log.info("Admin removed: %s", user_id)

    async def get_all_admins(self) -> list[int]:
        docs = await self.admins.find().to_list(length=None)
        return [doc["_id"] for doc in docs]


    # ─── FORCE SUBSCRIBE CHANNELS ───────────────────────────────────────────

    async def add_fsub_channel(self, channel_id: int):
        found = await self.fsub.find_one({"_id": channel_id})
        if not found:
            await self.fsub.insert_one({"_id": channel_id})
            log.info("Fsub channel added: %s", channel_id)

    async def remove_fsub_channel(self, channel_id: int):
        await self.fsub.delete_one({"_id": channel_id})
        log.info("Fsub channel removed: %s", channel_id)

    async def get_fsub_channels(self) -> list[int]:
        docs = await self.fsub.find().to_list(length=None)
        return [doc["_id"] for doc in docs]

    async def fsub_channel_exists(self, channel_id: int) -> bool:
        found = await self.fsub.find_one({"_id": channel_id})
        return bool(found)


    # ─── IMAGE CACHE ─────────────────────────────────────────────────────────
    # Stores: { _id: url_hash, url: str, file_id: str, bytes: Binary }
    # Priority on retrieval: file_id first (fastest), then raw bytes

    async def get_cached_image(self, url_hash: str) -> dict | None:
        """Return cached doc with file_id and/or bytes, or None."""
        return await self.image_cache.find_one({"_id": url_hash})

    async def cache_image(
        self,
        url_hash: str,
        url: str,
        file_id: str = None,
        image_bytes: bytes = None,
    ):
        """Insert or update cache entry for a poster image."""
        update = {"url": url}
        if file_id:
            update["file_id"] = file_id
        if image_bytes:
            import bson
            update["bytes"] = bson.Binary(image_bytes)

        await self.image_cache.update_one(
            {"_id": url_hash},
            {"$set": update},
            upsert=True,
        )
        log.info("Image cached: hash=%s file_id=%s", url_hash, file_id)

    async def update_file_id(self, url_hash: str, file_id: str):
        """Save Telegram file_id after first upload so future sends skip download."""
        await self.image_cache.update_one(
            {"_id": url_hash},
            {"$set": {"file_id": file_id}},
            upsert=False,
        )
        log.info("file_id saved for hash=%s", url_hash)


# ─── SINGLETON ───────────────────────────────────────────────────────────────
db = Database(DB_URI, DB_NAME)
