import os
import subprocess
import sys
import json
from pathlib import Path
from time import sleep
from yt_dlp.utils import DownloadError
import yt_dlp

# Stylish hacker banner
def print_banner():
    os.system("clear" if os.name == "posix" else "cls")
    banner = r'''
    
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░      
░▒▓█▓▒░   ░▒▓████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒▒▓███▓▒░▒▓████████▓▒░  ░▒▓█▓▒░          
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
░▒▓████████▓▒░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          

                Welc0m T0 L1ght Vedio                                
'''
    print(banner)

# Animated bar (simulated progress)
def animate_bar(task):
    bar = ""
    for i in range(1, 51):
        percent = int((i / 50) * 100)
        sys.stdout.write(f"\r📥 {task}... [{bar:<50}] {percent}%")
        sys.stdout.flush()
        bar += "▌"
        sleep(0.02)
    print()

def download_with_progress(url, output_path):
    ydl_opts = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }

    animate_bar("Merging best video + audio")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


if __name__ == '__main__':
    print_banner()
    try:
        link = input("📎 Paste YouTube URL here (or type 'exit'): ").strip()
        if link.lower() == 'exit':
            print("👋 Exiting L1ght Music. Stay safe out there.")
            sys.exit(0)

        output_path = str(Path.home() / "Videos")
        os.makedirs(output_path, exist_ok=True)

        print('\n🎶 Downloading audio...\n')
        animate_bar("Audio stream")
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'outtmpl': f'{output_path}/%(title)s.audio.%(ext)s', 'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info)

        print('\n🎥 Downloading video...\n')
        animate_bar("Video stream")
        with yt_dlp.YoutubeDL({'format': 'bestvideo', 'outtmpl': f'{output_path}/%(title)s.video.%(ext)s', 'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=True)
            video_file = ydl.prepare_filename(info)

        print('\n🔗 Merging audio + video...\n')
        download_with_progress(link, output_path)

        # Clean up
        for f in [audio_file, video_file]:
            if f and os.path.exists(f):
                os.remove(f)

        print('\n✅ Download complete! Check your Videos folder.\n')

    except DownloadError as e:
        print(f'\n❌ Download error: {e}')
    except Exception as e:
        print(f'\n❌ Unexpected error: {e}')
