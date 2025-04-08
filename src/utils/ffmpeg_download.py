import asyncio
import aiohttp
from aiohttp import ClientSession

async def async_ffmpeg_download(m3u8_url, output_path, cookies_str):
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-headers", f"Cookie: {cookies_str}",
        "-i", m3u8_url,
        "-c:v", "libx264",
        "-profile:v", "baseline",
        "-level", "3.0",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()
    print(f"Downloaded with ffmpeg: {output_path}")

async def async_direct_video_download(url, output_path, session):
    async with session.get(url) as resp:
        if resp.status == 200:
            with open(output_path, "wb") as f:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
            print(f"Downloaded direct video: {output_path}")

