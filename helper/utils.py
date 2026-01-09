# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔

import math, time, re, datetime, pytz, os
from config import Config, rkn
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ================= PROGRESS ================= #

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["▣" for _ in range(math.floor(percentage / 5))]),
            ''.join(["▢" for _ in range(20 - math.floor(percentage / 5))])
        )

        tmp = progress + rkn.RKN_PROGRESS.format(
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time else "0 s"
        )

        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close")]]
                )
            )
        except:
            pass


# ================= UTILS ================= #

def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    tmp = (
        ((str(days) + "ᴅ, ") if days else "") +
        ((str(hours) + "ʜ, ") if hours else "") +
        ((str(minutes) + "ᴍ, ") if minutes else "") +
        ((str(seconds) + "ꜱ, ") if seconds else "") +
        ((str(milliseconds) + "ᴍꜱ, ") if milliseconds else "")
    )
    return tmp[:-2]


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)


# ================= LOG ================= #

async def send_log(b, u):
    if Config.LOG_CHANNEL:
        curr = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        log_message = (
            "--Nᴇᴡ Uꜱᴇʀ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bᴏᴛ--\n\n"
            f"Uꜱᴇʀ: {u.mention}\n"
            f"Iᴅ: {u.id}\n"
            f"Uɴ: @{u.username}\n\n"
            f"Dᴀᴛᴇ: {curr.strftime('%d %B, %Y')}\n"
            f"Tɪᴍᴇ: {curr.strftime('%I:%M:%S %p')}\n\n"
            f"By: {b.mention}"
        )
        await b.send_message(Config.LOG_CHANNEL, log_message)


# ================= PREFIX / SUFFIX ================= #

def add_prefix_suffix(input_string, prefix='', suffix=''):
    pattern = r'(?P<filename>.*?)(\.\w+)?$'
    match = re.search(pattern, input_string)

    if match:
        filename = match.group('filename')
        extension = match.group(2) or ''
        prefix_str = f"{prefix} " if prefix else ""
        suffix_str = f" {suffix}" if suffix else ""
        return f"{prefix_str}{filename}{suffix_str}{extension}"

    return input_string


# ================= CLEANUP ================= #

async def remove_path(*paths):
    for path in paths:
        if path and os.path.lexists(path):
            os.remove(path)


# ================= METADATA (FIXED) ================= #
# ✅ WORKS WITH DICT (NEW SYSTEM)
# ✅ ALSO SUPPORTS STRING (OLD SYSTEM)
def metadata_text(metadata):
    """
    Accepts:
    - dict (NEW custom metadata system)
    - str  (OLD flag based system)

    Returns:
    author, title, video_title, audio_title, subtitle_title
    """

    # ✅ NEW SYSTEM (DICT)
    if isinstance(metadata, dict):
        return (
            metadata.get("author"),
            metadata.get("title"),
            metadata.get("video"),
            metadata.get("audio"),
            metadata.get("subtitle")
        )

    # ✅ OLD SYSTEM (STRING) - optional support
    if isinstance(metadata, str):
        author = title = video_title = audio_title = subtitle_title = None
        flags = [i.strip() for i in metadata.split('--')]

        for f in flags:
            if f.startswith("change-author"):
                author = f.replace("change-author", "").strip()
            elif f.startswith("change-title"):
                title = f.replace("change-title", "").strip()
            elif f.startswith("change-video-title"):
                video_title = f.replace("change-video-title", "").strip()
            elif f.startswith("change-audio-title"):
                audio_title = f.replace("change-audio-title", "").strip()
            elif f.startswith("change-subtitle-title"):
                subtitle_title = f.replace("change-subtitle-title", "").strip()

        return author, title, video_title, audio_title, subtitle_title

    # ❌ fallback
    return None, None, None, None, None
    # ================= TIME UTILS ================= #

def get_seconds(time_string: str) -> int:
    """
    Converts time like:
    1d -> seconds
    2h -> seconds
    30m -> seconds
    45s -> seconds
    """
    if not time_string:
        return 0

    time_string = time_string.lower().strip()

    try:
        if time_string.endswith("d"):
            return int(time_string[:-1]) * 86400
        if time_string.endswith("h"):
            return int(time_string[:-1]) * 3600
        if time_string.endswith("m"):
            return int(time_string[:-1]) * 60
        if time_string.endswith("s"):
            return int(time_string[:-1])
        return int(time_string)
    except ValueError:
        return 0