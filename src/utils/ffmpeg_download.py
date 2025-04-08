import subprocess

def ffmpeg_download(m3u8_url, output_mp4, cookies_str):
    # FFmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-headers", f"Cookie: {cookies_str}",
        "-i", m3u8_url,
        "-c:v", "libx264",
        "-profile:v", "baseline",  # Ensure compatibility
        "-level", "3.0",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        output_mp4
    ]

    # Run FFmpeg process
    subprocess.run(ffmpeg_cmd, check=True)

    print(f"Download complete: {output_mp4}")