from yt_dlp import YoutubeDL

URLS = [
    'https://www.youtube.com/watch?v=G67sCJKNjy8/'
]

with YoutubeDL() as ydl:
    ydl.download(URLS)


