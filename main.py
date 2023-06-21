import os
import sys

from aiogram import Bot, Dispatcher, executor, types

from recognizer import Recognizer
from convert import convert_audio
from dboperations import Database, EmptyStatsResult


bot_token = os.getenv("BOT_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
if bot_token is None:
    raise Exception("BOT_TOKEN is not set")

model_name = os.getenv("MODEL_NAME") or (sys.argv[2] if len(sys.argv) > 2 else None)
if model_name is None:
    raise Exception("MODEL_NAME is not set")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

recognizer = Recognizer(model_name)
database = Database()


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.reply(
        "Hello! I can recognize voice messages and translate them into text."
    )


# Main handler for voice messages
@dp.message_handler(content_types=types.ContentTypes.AUDIO | types.ContentTypes.VOICE)
async def voice_handler(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    if message.content_type == "voice":
        audio_file = await message.voice.get_file()
        duration = message.voice.duration
    if message.content_type == "audio":
        audio_file = await message.audio.get_file()
        duration = message.audio.duration
    print("Downloading file")
    audio_data = await bot.download_file(audio_file.file_path)
    audio_data = audio_data.read()
    await bot.send_chat_action(message.chat.id, "typing")
    print("Converting with ffmpeg")
    audio_data = await convert_audio(audio_data)
    await bot.send_chat_action(message.chat.id, "typing")
    print("Recognizing")
    text = await recognizer.recognize(audio_data)
    print("Recognize complete")
    await database.write_stats(message.from_user, message.chat.id, duration)
    sent_message = message
    for text_chunk in [text[i : i + 3500] for i in range(0, len(text), 3500)]:
        sent_message = await sent_message.reply(text_chunk)


@dp.message_handler(commands=["stats"])
async def get_stats(message: types.Message):
    results = await database.get_stats(message.chat.id)
    if isinstance(results, EmptyStatsResult):
        await message.reply("No stats yet for this chat")
        return
    text = "Cyrmax Speech Bot statistics:\n"
    text += f"Total amount of voice messages recognized in this chat: {results.voice_count}\n"
    text += f"Total length of all voice messages in this group: {results.total_voice_length}\n"
    text += "\nStats for every user:\n"
    for user in results.user_records:
        text += f"{user.fullname} ({user.username}) - count: {user.voice_count}, total length: {user.total_voice_length}\n"
    await message.reply(text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
