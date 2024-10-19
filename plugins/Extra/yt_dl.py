from __future__ import unicode_literals
import os
import requests
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL
import sys

# Define the progress bar
def progress_bar(current, total):
    bar_length = 40  # Length of the progress bar
    progress = current / total
    red_length = int(bar_length * (1 - progress))
    green_length = bar_length - red_length
    bar = f"[{'█' * green_length}{'-' * red_length}] {progress * 100:.1f}%"
    return bar

# Update the output
def hook(d):
    if d['status'] == 'downloading':
        current = d['downloaded_bytes']
        total = d['total_bytes']
        sys.stdout.write(f"\r{progress_bar(current, total)}")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        print(f"\nDownload completed! File saved to: {d['filename']}")

@Client.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    query = ' '.join(message.command[1:])
    m = await message.reply(f"**Searching your song...!\n {query}**")
    ydl_opts = {"format": "bestaudio[ext=m4a]", "progress_hooks": [hook]}

    audio_file = None  # Initialize variable
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        performer = f"[VJ NETWORKS™]"
        duration = results[0]["duration"]
    except Exception as e:
        print(str(e))
        return await m.edit("Example: /song vaa vaathi song")

    await m.edit("**Downloading your song...!**")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.download([link])  # Ensure the file is downloaded
            await m.edit("**Download completed!**")
        
        cap = "**BY›› [VJ NETWORKS™](https://t.me/vj_bots)**"
        dur = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':'))))
        await message.reply_audio(
            audio_file,
            caption=cap,
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name
        )
        await m.delete()
    except Exception as e:
        await m.edit("**🚫 ERROR 🚫**")
        print(e)

    # Clean up
    if audio_file and os.path.exists(audio_file):
        os.remove(audio_file)
    if os.path.exists(thumb_name):
        os.remove(thumb_name)

def get_text(message: Message) -> str:
    text_to_return = message.text
    if message.text is None or " " not in text_to_return:
        return None
    return message.text.split(None, 1)[1]

@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    urlissed = get_text(message)
    pablo = await client.send_message(message.chat.id, f"**FINDING YOUR VIDEO** `{urlissed}`")
    if not urlissed:
        return await pablo.edit("Example: /video Your video link")
    
    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = requests.get(kekme).content
    thumb_name = f"thumb_{fridayz}.jpg"
    
    with open(thumb_name, "wb") as thumb_file:
        thumb_file.write(sedlyf)

    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferredformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "progress_hooks": [hook],
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
    except Exception as e:
        return await pablo.edit_text(f"**Download Failed. Please Try Again..♥️** \n**Error :** `{str(e)}`")

    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"""**TITLE :** [{thum}]({mo})\n**REQUESTED BY :** {message.from_user.mention}"""

    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=thumb_name,
        caption=capy,
        supports_streaming=True,
        reply_to_message_id=message.id
    )
    await pablo.delete()
    
    # Clean up
    for files in (thumb_name, file_stark):
        if files and os.path.exists(files):
            os.remove(files)
