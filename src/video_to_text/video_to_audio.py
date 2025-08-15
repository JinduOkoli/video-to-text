import yt_dlp

def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio',
             'preferredcodec': 'mp3',
             'preferredquality': '192'}
        ]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url)
        file_name = f"{info['title']}.mp3"
    return file_name, info['title']
