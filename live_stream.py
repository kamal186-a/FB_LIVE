import os
import sys
import subprocess

# ---------- Configuration ----------
# GitHub Actions میں انہیں Secrets کے طور پر سیٹ کریں، یا لوکل ٹیسٹنگ کے لیے یہاں براہ راست لکھ دیں
GOOGLE_DRIVE_LINK = os.environ.get(
    "GDRIVE_LINK",
    "https://drive.google.com/file/d/1NxUZNHgVDpWMyFjH7c8V-XJyv8Da3GCB/view?usp=sharing",
)
LOCAL_VIDEO_PATH = "video.mp4"

FACEBOOK_STREAM_KEY = "FB-122193920732780799-0-Ab4JgxUm67HqqOAuoVJlmviL"
FACEBOOK_RTMP_URL = f"rtmps://live-api-s.facebook.com:443/rtmp/{FACEBOOK_STREAM_KEY}"

YOUTUBE_STREAM_KEY = "qpcb-3zs7-m3hj-ygse-6e0c"
YOUTUBE_RTMP_URL = f"rtmp://a.rtmp.youtube.com/live2/{YOUTUBE_STREAM_KEY}"


def download_from_drive(link: str, output: str) -> None:
    """gdown لائبریری کے ذریعے گوگل ڈرائیو سے ویڈیو ڈاؤن لوڈ کرتا ہے"""
    import gdown
    print("Google Drive سے ویڈیو ڈاؤن لوڈ ہو رہی ہے...")
    gdown.download(url=link, output=output, quiet=False, fuzzy=True)
    print("ڈاؤن لوڈ مکمل:", output)


def stream_to_facebook_and_youtube(video_path: str) -> None:
    """
    ایک ہی ویڈیو کو بیک وقت دو مختلف فارمیٹس میں لائیو کرتا ہے:
      - Facebook: اصل (اورجنل) ریشو، کوئی تبدیلی نہیں
      - YouTube:  vertical 9:16 (1080x1920) میں crop کر کے
    """
    filter_complex = (
        "[0:v]split=2[fb_v][yt_pre];"
        "[yt_pre]scale=1080:-2,crop=1080:1920[yt_v]"
    )

    cmd = [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",      # ویڈیو بار بار لوپ ہوگی؛ ایک بار چلانے کے لیے یہ لائن ہٹا دیں
        "-i", video_path,
        "-filter_complex", filter_complex,

        # ---- Facebook output (اصل ریشو) ----
        "-map", "[fb_v]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "veryfast",
        "-maxrate", "3000k", "-bufsize", "6000k",
        "-pix_fmt", "yuv420p", "-g", "60",
        "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
        "-f", "flv", FACEBOOK_RTMP_URL,

        # ---- YouTube output (vertical 9:16) ----
        "-map", "[yt_v]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "veryfast",
        "-maxrate", "3000k", "-bufsize", "6000k",
        "-pix_fmt", "yuv420p", "-g", "60",
        "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
        "-f", "flv", YOUTUBE_RTMP_URL,
    ]

    print("Facebook (horizontal) اور YouTube (vertical) پر لائیو اسٹریم شروع ہو رہی ہے...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("اسٹریمنگ ناکام ہوگئی:", e)
        sys.exit(1)


if __name__ == "__main__":
    download_from_drive(GOOGLE_DRIVE_LINK, LOCAL_VIDEO_PATH)
    stream_to_facebook_and_youtube(LOCAL_VIDEO_PATH)
