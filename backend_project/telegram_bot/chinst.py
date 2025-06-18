import os
import shutil
import subprocess
import zipfile
import urllib.request

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_DIR = "ffmpeg"
FFMPEG_BIN = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def download_ffmpeg():
    print("Downloading FFmpeg...")#debugging purpose
    zip_path = "ffmpeg.zip"
    urllib.request.urlretrieve(FFMPEG_URL, zip_path)
    print("✅ Download complete. Extracting...")
    #debugging purpose as i had issue with manual installation

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(FFMPEG_DIR)
    for root, dirs, files in os.walk(FFMPEG_DIR):
        for file in files:
            if file == "ffmpeg.exe":
                ffmpeg_exe_path = os.path.join(root, file)
                shutil.copy(ffmpeg_exe_path, FFMPEG_BIN)
                print(f"ffmpeg.exe copied to {FFMPEG_BIN}")
                break

    os.remove(zip_path)

def main():
    if is_ffmpeg_installed():
        print("FFmpeg is already installed.")
    else:
        print("FFmpeg not found. Installing it now...")
        download_ffmpeg()

       
        os.environ["PATH"] += os.pathsep + os.path.abspath(FFMPEG_DIR)
        print("FFmpeg installed and added to PATH (temporarily).")

if __name__ == "__main__":
    main()
