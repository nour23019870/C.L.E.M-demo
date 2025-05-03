import subprocess
import os
from pathlib import Path
from time import sleep
import sys
import json
import shutil
import importlib.util

# Modern hacker-style header
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
                                                                 
                Welc0m T0 🄻①🄶🄷🅃 🄼🅄🅂①🄲                                
'''
    print(banner)

# Check if yt-dlp is installed and available
def check_yt_dlp():
    """Check if yt-dlp is installed and available, either as command or Python module"""
    # Check if command is in PATH
    if shutil.which("yt-dlp") is not None:
        return "command"
    
    # Check if module is installed
    if importlib.util.find_spec("yt_dlp") is not None:
        return "module"
    
    # Not found
    print("\n❌ Error: yt-dlp not found in your system")
    print("\n📋 Please install yt-dlp using one of these methods:")
    print("   1. Run: pip install -r requirements.txt")
    print("   2. Run: pip install yt-dlp")
    print("   3. Download from https://github.com/yt-dlp/yt-dlp#installation")
    print("\nIf you've already installed yt-dlp but still see this error, you may need to:")
    print("   1. Add the Python Scripts directory to your PATH")
    print("   2. Restart your terminal or computer")
    print("   3. Or try using 'python -m yt_dlp' directly\n")
    return False

# Progress bar with percentage
def animate_bar(task, total):
    bar = ""
    for i in range(1, 51):
        percent = int((i / 50) * 100)
        sys.stdout.write(f"\r🎵 {task}... [{bar:<50}] {percent}%")
        sys.stdout.flush()
        bar += "▌"
        sleep(0.02)
    print("\n")

# Get playlist entries using yt-dlp
def get_playlist_entries(url, yt_dlp_mode):
    if yt_dlp_mode == "command":
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", url]
    else:  # module mode
        cmd = [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--dump-json", url]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    
    entries = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
                
    return entries

def download_audio(url):
    print("\n⬇️  Downloading and converting to MP3...\n")

    # Verify that yt-dlp is available
    yt_dlp_mode = check_yt_dlp()
    if not yt_dlp_mode:
        return

    music_dir = str(Path.home() / "Music")
    os.makedirs(music_dir, exist_ok=True)

    try:
        entries = get_playlist_entries(url, yt_dlp_mode)
        total = len(entries) if entries else 1

        for i, entry in enumerate(entries if entries else [None], 1):
            label = f"Track {i}/{total}"
            animate_bar(label, total)

            cmd_url = f"https://www.youtube.com/watch?v={entry['id']}" if entry else url

            if yt_dlp_mode == "command":
                command = [
                    "yt-dlp",
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--audio-quality", "0",
                    "-o", os.path.join(music_dir, "%(title)s.%(ext)s"),
                    cmd_url
                ]
            else:  # module mode
                command = [
                    sys.executable, "-m", "yt_dlp",
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--audio-quality", "0",
                    "-o", os.path.join(music_dir, "%(title)s.%(ext)s"),
                    cmd_url
                ]

            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("\n✅ All downloads complete! Saved in ~/Music\n")
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("Please make sure yt-dlp is properly installed and try again.")

if __name__ == "__main__":
    print_banner()
    while True:
        url = input("📎 Paste YouTube URL here (or type 'exit'): ").strip()
        if url.lower() == "exit":
            print("👋 Exiting L1ght Music. Stay safe out there.")
            break
        elif url:
            download_audio(url)
        else:
            print("❌ No URL provided. Try again or type 'exit'.")
