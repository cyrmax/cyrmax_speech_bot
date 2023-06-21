import asyncio


async def convert_audio(data: bytes) -> bytes:
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-loglevel",
        "quiet",
        "-hide_banner",
        "-i",
        "-",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-f",
        "s16le",
        "-",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    result, _ = await process.communicate(data)
    await process.wait()
    stdout_data, _ = await process.communicate()
    return result + stdout_data
