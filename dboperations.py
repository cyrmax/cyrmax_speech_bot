from motor.motor_asyncio import AsyncIOMotorClient
from aiogram.types import User
from dataclasses import dataclass


@dataclass
class UserStatRecord:
    _id: str
    chat_id: str
    fullname: str
    username: str
    voice_count: int
    total_voice_length: int


@dataclass
class StatsResult:
    voice_count: int
    total_voice_length: int
    user_records: list[UserStatRecord]


class EmptyStatsResult:
    pass


class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb://mongodb:27017")
        self.db = self.client.cyrmaxspeechbot

    async def write_stats(self, user: User, chat_id: int | str, voice_length: int):
        user_db_id = f"chat{chat_id}_user{user.id}"
        # If record for user does not exist yet, create it
        if await self.db.voice_stats.count_documents({"_id": user_db_id}) == 0:
            await self.db.voice_stats.insert_one(
                {
                    "_id": user_db_id,
                    "chat_id": chat_id,
                    "username": user.username,
                    "fullname": user.full_name,
                    "voice_count": 1,
                    "total_voice_length": voice_length,
                }
            )
            return
        else:
            await self.db.voice_stats.update_one(
                {"_id": user_db_id},
                {"$inc": {"voice_count": 1, "total_voice_length": voice_length}},
            )
            return

    async def get_stats(self, chat_id: int | str) -> StatsResult:
        total_stats = await self.db.voice_stats.aggregate(
            [
                {"$match": {"chat_id": chat_id}},
                {
                    "$group": {
                        "_id": None,
                        "total_count": {"$sum": "$voice_count"},
                        "total_length": {"$sum": "$total_voice_length"},
                    }
                },
            ]
        ).to_list(1)
        if len(total_stats) == 0:
            return EmptyStatsResult()
        user_stats = self.db.voice_stats.find({"chat_id": chat_id})
        sorted_user_stats = user_stats.sort("voice_count", -1)
        sorted_user_stats = await sorted_user_stats.to_list(500)
        return StatsResult(
            total_stats[0]["total_count"],
            total_stats[0]["total_length"],
            [UserStatRecord(**user) for user in sorted_user_stats],
        )
