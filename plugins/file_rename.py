import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

from helper.utils import humanbytes
from helper.database import digital_botz


# ------------------- File Rename Start -------------------
@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def rename_start(client, message):
    user_id = message.from_user.id
    media = getattr(message, message.media.value)
    filesize = humanbytes(media.file_size)
    filename = media.file_name or "Unknown"
    extension_type = filename.rsplit(".", 1)[-1] if "." in filename else "NA"
    mime_type = media.mime_type or "NA"
    dcid = getattr(media, "dc_id", "NA")

    # Daily Limit Check
    user_data = await digital_botz.get_user_data(user_id)
    limit = user_data.get("uploadlimit", 0)
    used = user_data.get("used_limit", 0)
    remain = int(limit) - int(used)

    if limit > 0 and remain < media.file_size:
        used_percentage = (int(used) / int(limit)) * 100 if limit != 0 else 0
        return await message.reply_text(
            f"{used_percentage:.2f}% Of Daily Upload Limit {humanbytes(limit)}.\n\n"
            f"Media Size: {filesize}\nYour Used Daily Limit {humanbytes(used)}\n\n"
            f"You have only {humanbytes(remain)} left.\nPlease Buy Premium Plan.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🪪 Upgrade", callback_data="plans")]]
            ),
        )

    # Premium 2GB+ restriction
    if media.file_size > 2000 * 1024 * 1024 and not await digital_botz.has_premium_access(user_id):
        return await message.reply_text(
            "❌ Free Users can upload files up to 2GB.\n\nUpgrade to premium for 4GB support! /plans"
        )

    # Ask for new file name
    try:
        await message.reply_text(
            text=f"**__Media Info:__**\n\n"
            f"◈ Old Filename: `{filename}`\n"
            f"◈ Extension: `{extension_type.upper()}`\n"
            f"◈ Size: `{filesize}`\n"
            f"◈ MimeType: `{mime_type}`\n"
            f"◈ DC ID: `{dcid}`\n\n"
            f"✏️ Please send the new filename with extension (e.g. Movie.mp4).",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(True),
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await rename_start(client, message)


# ------------------- New Filename Reply -------------------
@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message
    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text.strip()
        file = await client.get_messages(message.chat.id, reply_message.id)
        media = getattr(file.reply_to_message, file.reply_to_message.media.value)

        # Add extension if missing
        if "." not in new_name:
            extn = media.file_name.rsplit(".", 1)[-1] if "." in media.file_name else "mkv"
            new_name = f"{new_name}.{extn}"

        # Ask Output Type
        button = [[InlineKeyboardButton("📁 Document", callback_data="upload_document")]]
        if file.reply_to_message.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton("🎥 Video", callback_data="upload_video")])
        elif file.reply_to_message.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")])

        await message.reply(
            text=f"**Select Output Type**\n\n**• New Filename:** `{new_name}`",
            reply_to_message_id=file.reply_to_message.id,
            reply_markup=InlineKeyboardMarkup(button),
        )
        await reply_message.delete()
        await message.delete()
