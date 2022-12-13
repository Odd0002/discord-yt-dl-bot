import asyncio
import logging
import os
import re
import urllib.parse
from collections import namedtuple
from multiprocessing import Pool, Process, Queue

import discord
import yt_dlp
from discord.ext import tasks, commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
VALID_CHANNELS = os.getenv('VALID_CHANNELS').split(',')
VALID_USERS = os.getenv('VALID_USERS').split(',')

OUTPUT_DIR='/yt-dl-files/'
FFMPEG_LOCATION='/ffmpeg-dl/ffmpeg-bin/bin/ffmpeg'

message_queue = Queue()
MessageInfo = namedtuple("MessageInfo", "message channel_id")


def download_video(URL, channel_id):
    main_ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': (OUTPUT_DIR + '%(title)s-%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegMetadata'
        }],
        'writeinfojson': True,
        'writedescription': True,
        'writethumbnail': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        #'getcomments': True,
        'overwrites': False,
        'check_formats': None,
        'cookiefile':'cookies.txt',
        'ffmpeg_location': FFMPEG_LOCATION
        }

    with yt_dlp.YoutubeDL(main_ydl_opts) as ydl:
        try:
            start_message = MessageInfo("Starting download...", channel_id)
            message_queue.put(start_message)
            info = ydl.extract_info(URL, download=True)
            filename = ydl.prepare_filename(info)
            message = MessageInfo("Download done of file {0}.".format(filename), channel_id)
            message_queue.put(message)
        except Exception as ex:
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            ex_clean = ansi_escape.sub('', str(ex))
            message = MessageInfo(ex_clean, channel_id)
            message_queue.put(message)


class MyClient(discord.Client):
    async def on_ready(self):
        self.download_video_listener.start()

    async def on_message(self, message):
            if str(message.channel.name) in VALID_CHANNELS and str(message.author) in VALID_USERS:
                p = Process(target=download_video, args=(message.content, message.channel.id))
                p.start()

    @tasks.loop(seconds=1.0)
    async def download_video_listener(self):
        if (message_queue.empty()):
            return
        message = message_queue.get()
        if message is None:
            return
        await self.get_channel(message.channel_id).send(message.message)

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()