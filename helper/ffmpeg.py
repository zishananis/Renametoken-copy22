import subprocess
import json
from helper.utils import metadata_text


def change_metadata(input_file: str, output_file: str, metadata: dict) -> bool:
    """
    Apply metadata to media file using FFmpeg
    ✔ Supports MULTIPLE video/audio/subtitle streams
    """

    author, title, video_title, audio_title, subtitle_title = metadata_text(metadata)
    artist = metadata.get("artist") if isinstance(metadata, dict) else None

    # ---------- FFPROBE (GET STREAM INFO) ----------
    try:
        probe = subprocess.check_output(
            [
                "ffprobe",
                "-v", "error",
                "-show_streams",
                "-print_format", "json",
                input_file
            ]
        )
        streams = json.loads(probe).get("streams", [])
    except Exception as e:
        print("FFprobe Error:", e)
        return False

    # ---------- BASE FFMPEG CMD ----------
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-map", "0",
        "-c", "copy"
    ]

    # ---------- GLOBAL METADATA ----------
    if title:
        cmd += ["-metadata", f"title={title}"]
    if author:
        cmd += ["-metadata", f"author={author}"]
    if artist:
        cmd += ["-metadata", f"artist={artist}"]

    # ---------- STREAM METADATA (ALL STREAMS) ----------
    v_i = a_i = s_i = 0

    for stream in streams:
        codec_type = stream.get("codec_type")

        if codec_type == "video" and video_title:
            cmd += ["-metadata:s:v:%d" % v_i, f"title={video_title}"]
            v_i += 1

        elif codec_type == "audio" and audio_title:
            cmd += ["-metadata:s:a:%d" % a_i, f"title={audio_title}"]
            a_i += 1

        elif codec_type == "subtitle" and subtitle_title:
            cmd += ["-metadata:s:s:%d" % s_i, f"title={subtitle_title}"]
            s_i += 1

    # ---------- OPTIONAL COMMENT ----------
    cmd += ["-metadata", "comment=Added by @FileRename4GbSTRobot"]

    # ---------- OUTPUT ----------
    cmd.append(output_file)

    print("FFmpeg CMD:", cmd)

    # ---------- RUN ----------
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print("FFmpeg Error:\n", e.stderr.decode())
        return False