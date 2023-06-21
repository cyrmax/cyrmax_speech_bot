import asyncio
import os
from pathlib import Path


async def recognize_audio(filepath: str | Path, lang: str) -> str:
    process = await asyncio.create_subprocess_exec(
        "vosk-transcriber",
        "-l",
        lang,
        "-i",
        str(filepath),
        "--log-level",
        "ERROR",
        "-o",
        f"{filepath}.out",
        "--log-level",
        "ERROR",
        "--model-name",
        "vosk-model-ru-0.22",
        "--tasks",
        "8",
    )
    await process.wait()
    with open(f"{filepath}.out", "r", encoding="utf-8") as f:
        text = f.read()
    os.remove(f"{filepath}.out")
    return text
