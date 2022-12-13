FROM python:3.11-bullseye

COPY src /app

# Update stuff
RUN apt-get update && apt-get -y upgrade

# Download yt-dlp specific ffmpeg
RUN mkdir ffmpeg-dl
WORKDIR ffmpeg-dl
RUN wget https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
RUN tar -xf ffmpeg-master-latest-linux64-gpl.tar.xz
RUN mv ffmpeg-master-latest-linux64-gpl ffmpeg-bin

# Install requirements
WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run the bot
CMD python bot.py