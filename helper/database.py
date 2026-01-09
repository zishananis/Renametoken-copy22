# (c) @RknDeveloperr
# Rkn Developer
# Don't Remove Credit 😔

import motor.motor_asyncio
import datetime
from config import Config
from helper.utils import send_log


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user
        self.premium = self.db.premium

    # ================= USER ================= #

    def new_user(self, user_id: int):
        return {
            "_id": int(user_id),
            "join_date": datetime.date.today().isoformat(),

            # media
            "file_id": None,
            "caption": None,
            "prefix": None,
            "suffix": None,

            # limits
            "used_limit": 0,
            "daily": 0,
            "usertype": "Free",
            "uploadlimit": Config.FREE_UPLOAD_LIMIT,

            # metadata
            "metadata_mode": False,
            "metadata_code": "",

            "custom_metadata": {
                "title": None,
                "author": None,
                "artist": None,
                "audio": None,
                "video": None,
                "subtitle": None
            },

            # premium
            "expiry_time": None,
            "has_free_trial": False,

            # ban
            "ban_status": {
                "is_banned": False,
                "ban_duration": 0,
                "banned_on": datetime.date.max.isoformat(),
                "ban_reason": ""
            }
        }

    async def add_user(self, bot, message):
        u = message.from_user
        if not await self.is_user_exist(u.id):
            await self.col.insert_one(self.new_user(u.id))
            await send_log(bot, u)

    async def is_user_exist(self, user_id):
        return bool(await self.col.find_one({"_id": int(user_id)}))

    async def get_user_data(self, user_id):
        return await self.col.find_one({"_id": int(user_id)})

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_one({"_id": int(user_id)})

    # ================= THUMBNAIL ================= #

    async def set_thumbnail(self, user_id, file_id):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"file_id": file_id}}
        )

    async def get_thumbnail(self, user_id):
        user = await self.get_user_data(user_id)
        return user.get("file_id") if user else None

    # ================= CAPTION ================= #

    async def set_caption(self, user_id, caption):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"caption": caption}}
        )

    async def get_caption(self, user_id):
        user = await self.get_user_data(user_id)
        return user.get("caption") if user else None

      # ================= PREFIX / SUFFIX ================= #

    async def set_prefix(self, user_id, prefix):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"prefix": prefix}}
        )

    async def get_prefix(self, user_id):
        user = await self.get_user_data(user_id)
        return user.get("prefix") if user else None

    async def set_suffix(self, user_id, suffix):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"suffix": suffix}}
        )

    async def get_suffix(self, user_id):
        user = await self.get_user_data(user_id)
        return user.get("suffix") if user else None

    # ================= METADATA ================= #

    async def get_metadata_mode(self, user_id):
        user = await self.get_user_data(user_id)
        return user.get("metadata_mode", False) if user else False
    async def set_metadata_mode(self, user_id, mode: bool):
         await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"metadata_mode": bool(mode)}}
        )

    async def set_metadata_code(self, user_id, code):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"metadata_code": code}}
        )

    async def get_metadata_code(self, user_id):
        user = await self.get_user_data(user_id)
        return user.get("metadata_code") if user else None

    async def get_custom_metadata(self, user_id):
        user = await self.get_user_data(user_id)
        return user.get("custom_metadata", {}) if user else {}

    async def set_custom_metadata(self, user_id, key, value):
        if key not in ["title", "author", "artist", "audio", "video", "subtitle"]:
            return
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {f"custom_metadata.{key}": value}}
        )

    # ================= LIMITS ================= #

    async def set_used_limit(self, user_id, used):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"used_limit": used}}
        )

    async def reset_daily_limit(self, user_id):
        now = datetime.datetime.now()
        next_reset = now + datetime.timedelta(days=1)

        user = await self.get_user_data(user_id)
        if not user:
            return

        last = user.get("daily", 0)
        if last == 0 or (isinstance(last, datetime.datetime) and now > last):
            await self.col.update_one(
                {"_id": int(user_id)},
                {"$set": {"daily": next_reset, "used_limit": 0}}
            )

    async def set_usertype(self, user_id, usertype):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"usertype": usertype}}
        )

    async def set_uploadlimit(self, user_id, limit):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"uploadlimit": limit}}
        )

    # ================= PREMIUM ================= #

    async def get_premium(self, user_id):
        return await self.premium.find_one({"id": int(user_id)})

    async def add_premium(self, user_id, data, limit=None, usertype=None):
        await self.premium.update_one(
            {"id": int(user_id)},
            {"$set": data},
            upsert=True
        )
        if Config.UPLOAD_LIMIT_MODE and limit and usertype:
            await self.set_usertype(user_id, usertype)
            await self.set_uploadlimit(user_id, limit)

    async def remove_premium(self, user_id):
        await self.premium.update_one(
            {"id": int(user_id)},
            {"$set": {"expiry_time": None}}
        )
        if Config.UPLOAD_LIMIT_MODE:
            await self.set_usertype(user_id, "Free")
            await self.set_uploadlimit(user_id, Config.FREE_UPLOAD_LIMIT)

    async def has_premium_access(self, user_id):
        data = await self.get_premium(user_id)
        if not data:
            return False

        expiry = data.get("expiry_time")
        if isinstance(expiry, datetime.datetime) and datetime.datetime.now() <= expiry:
            return True

        await self.remove_premium(user_id)
        return False

    # ================= BAN ================= #

    async def get_ban_status(self, user_id):
        user = await self.get_user_data(user_id)

    # ✅ user hi nahi hai
        if not user:
            return {
                "is_banned": False,
                "ban_duration": 0,
                "banned_on": None,
                "ban_reason": ""
            }

    # ✅ ban_status hi missing hai
        return user.get("ban_status", {
            "is_banned": False,
            "ban_duration": 0,
            "banned_on": None,
            "ban_reason": ""
        })

    async def ban_user(self, user_id, ban_duration=0, ban_reason=""):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {
                "ban_status": {
                    "is_banned": True,
                    "ban_duration": int(ban_duration),
                    "banned_on": datetime.datetime.now().isoformat(),
                    "ban_reason": ban_reason
                }
            }}
        )

    async def remove_ban(self, user_id):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {
                "ban_status": {
                    "is_banned": False,
                    "ban_duration": 0,
                    "banned_on": datetime.date.max.isoformat(),
                   "ban_reason": ""
                }
            }}
        )
    async def get_all_banned_users(self):
        return await self.col.find(
            {"ban_status.is_banned": True}
        ).to_list(length=None)

    async def total_premium_users_count(self):
        return await self.premium.count_documents({
            "expiry_time": {"$ne": None}
        })

# ================= INSTANCE ================= #

digital_botz = Database(Config.DB_URL, Config.DB_NAME)