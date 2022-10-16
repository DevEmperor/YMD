#!/usr/bin/python3


# CONFIGURATION-SECTION
OUTPUT_DIR = ""  # set an output folder in case you want to set this folder as default
GENIUS_ACCESS_TOKEN = ""  # set a Genius access token if you want to add lyrics

# check for missing dependencies which are:
try:
    import os
    import shutil
    import subprocess
    from urllib.request import urlretrieve
    from PIL import Image
    import requests

    import yt_dlp
    import eyed3
    from eyed3.core import Date
    import lyricsgenius
except ImportError as e:
    exit("\033[91mMissing dependency: {}. Please check your installation!".format(e.name))

# colors used to make the terminal look nicer
GREEN, YELLOW, RED, CYAN, BOLD, RST = "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[1m", "\033[0m"
INFO, WARNING, ERROR, REQUEST = f"[{GREEN}+{RST}]", f"[{YELLOW}~{RST}]", f"[{RED}-{RST}]", f"[{CYAN}?{RST}]"


class MyLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def prog_hook(d):
    if d["status"] == "finished":
        print("\n{} Done downloading, now converting and tagging ...".format(INFO))
    elif d["status"] == "error":
        pass
    else:
        try:  # some videos do not contain an artist, so instead we take the name of the channel
            artist = item["artist"]
        except KeyError:
            artist = item["uploader"]
        print("\r{} Downloading track {} / {} : {} - {}{}{} ({}) ..." \
              .format(INFO, item["playlist_index"] if len(items) > 1 else 1, item["playlist_count"] if len(items) > 1 else 1, artist, BOLD, item["title"], RST,
                      "{:2.1f}%".format(d["downloaded_bytes"] / d["total_bytes"] * 100)), end="")


# main-function
if __name__ == "__main__":
    # always check for ctrl+c
    try:
        T_WIDTH = shutil.get_terminal_size().columns

        # welcome-message
        gap = "\n" + " " * (T_WIDTH // 2 - 14)
        print(gap + f"██{RED}╗{RST}   ██{RED}╗{RST}███{YELLOW}╗{RST}   ███{YELLOW}╗{RST}██████{GREEN}╗{RST}" +
              gap + f"{RED}╚{RST}██{RED}╗{RST} ██{RED}╔╝{RST}████{YELLOW}╗{RST} ████{YELLOW}║{RST}██{GREEN}╔══{RST}██{GREEN}╗{RST}" +
              gap + f" {RED}╚{RST}████{RED}╔╝{RST} ██{YELLOW}╔{RST}████{YELLOW}╔{RST}██{YELLOW}║{RST}██{GREEN}║{RST}  ██{GREEN}║{RST}" +
              gap + f"  {RED}╚{RST}██{RED}╔╝{RST}  ██{YELLOW}║╚{RST}██{YELLOW}╔╝{RST}██{YELLOW}║{RST}██{GREEN}║{RST}  ██{GREEN}║{RST}" +
              gap + f"   ██{RED}║{RST}   ██{YELLOW}║ ╚═╝{RST} ██{YELLOW}║{RST}██████{GREEN}╔╝{RST}" +
              gap + f"   {RED}╚═╝{RST}   {YELLOW}╚═╝     ╚═╝{RST}{GREEN}╚═════╝{RST}" +
              "\n" + " " * (T_WIDTH // 2 - 14) + "Youtube-Music-Downloader 1.0" +
              gap + "  developed by Jannis Zahn")

        # specify the output-directory and further configuration
        print("\n---- CONFIGURATION " + "-" * (T_WIDTH - 19) + "\n")
        if not os.path.isdir(OUTPUT_DIR):
            while True:
                OUTPUT_DIR = input("{} Please specify an existing and writable output-directory: ".format(REQUEST))
                if os.path.isdir(OUTPUT_DIR):
                    break
        OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)
        print("{} Output-Directory: {}\n".format(INFO, OUTPUT_DIR))
        add_covers = input("{} Should I add the cover arts to your tracks? [YES / no] ".format(REQUEST)).lower() != "no"

        while True:
            URL = input("{} Please enter the URL of a track / album / playlist to download: ".format(REQUEST))
            if URL.startswith("https://music.youtube.com/"):
                break

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "progress_hooks": [prog_hook],
            "format": "bestaudio/best",
            "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
            ""
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                },
            ]
        }
        
        # initialize access to Genius-API
        genius = None
        if GENIUS_ACCESS_TOKEN != "":
            genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
            genius.verbose = False

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\n---- DOWNLOADING " + "-" * (T_WIDTH - 17) + "\n")
            print("{} Extracting information from the URL ...".format(INFO))
            items = ydl.extract_info(URL, download=False)
            if "entries" in items:
                items = items["entries"]
            else:
                items = [items]

            print("\n{} URL contains a single track".format(INFO) if len(items) == 1 else "\n{} URL contains an album / a playlist".format(INFO))
            for item in items:
                while True:
                    try:
                        error_code = ydl.download(item["original_url"])  # DOWNLOAD
                        if error_code != 0:
                            raise yt_dlp.utils.DownloadError
                        break
                    except yt_dlp.utils.DownloadError:
                        input("{} Couldn't download this track... Please fix your network connection and press ENTER!".format(ERROR))

                # parse tags and download cover
                tags = eyed3.load(os.path.join(OUTPUT_DIR, item["title"].replace("|", "_").replace("/", "_").replace("\"", "＂") + ".mp3"))

                tags.tag.title = item["title"]
                try:  # some videos do not contain an artist, so instead we take the name of the channel
                    tags.tag.artist = item["artist"]
                except KeyError:
                    tags.tag.artist = item["uploader"]
                try:
                    tags.tag.album = item["album"]
                except KeyError:
                    pass
                try:  # add release_year if it is a track, else the upload_date
                    tags.tag.recording_date = Date(int(item["upload_date"][:4]))
                    tags.tag.recording_date = Date(item["release_year"])
                except (KeyError, TypeError):
                    pass
                tags.tag.track_num = (item["playlist_index"] if len(items) > 1 and "Album" in item["playlist"] else None,
                                      item["playlist_count"] if len(items) > 1 and "Album" in item["playlist"] else None)
                tags.tag.copyright = "Downloaded with YoutubeMusicDownloader from Youtube Music"

                if add_covers:
                    urlretrieve(item["thumbnail"], os.path.join(OUTPUT_DIR, ".cover.webp"))  # download cover art
                    img = Image.open(os.path.join(OUTPUT_DIR, ".cover.webp"))
                    cropped = img.crop((280, 0, 1000, 720))  # crop thumbnail from rectangle to square
                    cropped.save(os.path.join(OUTPUT_DIR, ".cover.webp"))
                    tags.tag.images.set(3, open(os.path.join(OUTPUT_DIR, ".cover.webp"), "rb").read(), "image/webp", u"cover")

                # try to find the lyrics
                if genius is not None and genius.access_token.startswith("Bearer"):
                    while True:
                        try:
                            genius_song = genius.search_song(item["title"])
                            break
                        except requests.exceptions.RequestException:
                            input("{} Couldn't get song lyrics from Genius... Please fix your network connection and press ENTER!".format(ERROR))
                    if genius_song is not None:  # only if a song text was found
                        lyrics = genius_song.lyrics
                    else:
                        lyrics = "There are no lyrics available for this track..."
                else:
                    lyrics = "There are no lyrics available for this track..."
                tags.tag.lyrics.set(lyrics, u"XXX")
                tags.tag.save()

        try:
            os.remove(os.path.join(OUTPUT_DIR, ".cover.webp"))
        except FileNotFoundError:
            pass
        print("\n{}{} Done! {} tracks downloaded. Bye!{}".format(INFO, GREEN, len(items), RST))

    except KeyboardInterrupt:
        exit("\n{}Detected Ctrl+C (Keyboard-Interrupt) ... Bye! :-)".format(RED))
