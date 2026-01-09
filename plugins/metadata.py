# (c) @RknDeveloperr
# Don't Remove Credit 😔

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from pyromod.exceptions import ListenerTimeout
from helper.database import digital_botz


# ================= CONSTANTS ================= #

DESC = {
    "title": "Descriptive title of the media",
    "author": "Author / Creator",
    "artist": "Artist name",
    "audio": "Audio stream title",
    "video": "Video stream title",
    "subtitle": "Subtitle title"
}


# ================= MAIN MENU ================= #

def main_menu(meta_on: bool):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👤 Set Metadata", callback_data="meta_set"),
                InlineKeyboardButton("👁 View Metadata", callback_data="meta_view")
            ],
            [
                InlineKeyboardButton("💡 Metadata Mode", callback_data="meta_toggle"),
                InlineKeyboardButton("✅" if meta_on else "❌", callback_data="meta_toggle")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="meta_close")
            ]
        ]
    )


# ================= SET MENU ================= #

SET_MENU = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Title", callback_data="edit_title"),
            InlineKeyboardButton("Author", callback_data="edit_author")
        ],
        [
            InlineKeyboardButton("Artist", callback_data="edit_artist"),
            InlineKeyboardButton("Audio", callback_data="edit_audio")
        ],
        [
            InlineKeyboardButton("Video", callback_data="edit_video"),
            InlineKeyboardButton("Subtitle", callback_data="edit_subtitle")
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="meta_back"),
            InlineKeyboardButton("❌ Close", callback_data="meta_close")
        ]
    ]
)


# ================= FIELD MENU ================= #

def field_menu(key):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏ Edit", callback_data=f"set_{key}"),
                InlineKeyboardButton("♻ Reset", callback_data=f"reset_{key}")
            ],
            [
                InlineKeyboardButton("⬅ Back", callback_data="meta_set"),
                InlineKeyboardButton("❌ Close", callback_data="meta_close")
            ]
        ]
    )


# ================= /metadata ================= #

@Client.on_message(filters.private & filters.command("metadata"))
async def metadata_cmd(bot: Client, message: Message):
    user_id = message.from_user.id
    await digital_botz.add_user(bot, message)

    mode = await digital_botz.get_metadata_mode(user_id)

    await message.reply_text(
        f"Hey {message.from_user.first_name} 👋\n\n"
        "🎛 Customize Metadata\n\n"
        "➜ Set and manage metadata for your media\n"
        "➜ Use the buttons below",
        reply_markup=main_menu(mode)
    )


# ================= CALLBACK HANDLER ================= #

@Client.on_callback_query(filters.regex(r"^(meta_|edit_|set_|reset_)"))
async def metadata_buttons(bot: Client, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data

    # ---- TOGGLE MODE ---- #
    if data == "meta_toggle":
        current = await digital_botz.get_metadata_mode(user_id)
        await digital_botz.set_metadata_mode(user_id, not current)

        await query.answer("Metadata mode updated")
        await query.message.edit_reply_markup(
            reply_markup=main_menu(not current)
        )

    # ---- OPEN SET MENU ---- #
    elif data == "meta_set":
        try:
            await query.message.edit(
                "🧩 Custom Metadata\n\nSelect a field to edit:",
                reply_markup=SET_MENU
            )
        except Exception:
            pass

    # ---- VIEW METADATA ---- #
    elif data == "meta_view":
        meta = await digital_botz.get_custom_metadata(user_id)
        await query.message.edit(
            "📋 Your Current Metadata\n\n"
            f"• Title: {meta.get('title') or 'Not Set'}\n"
            f"• Author: {meta.get('author') or 'Not Set'}\n"
            f"• Artist: {meta.get('artist') or 'Not Set'}\n"
            f"• Audio: {meta.get('audio') or 'Not Set'}\n"
            f"• Video: {meta.get('video') or 'Not Set'}\n"
            f"• Subtitle: {meta.get('subtitle') or 'Not Set'}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⬅ Back", callback_data="meta_back"),
                        InlineKeyboardButton("❌ Close", callback_data="meta_close")
                    ]
                ]
            )
        )

    # ---- BACK TO MAIN MENU ---- #
    elif data == "meta_back":
        mode = await digital_botz.get_metadata_mode(user_id)
        await query.message.edit_reply_markup(
            reply_markup=main_menu(mode)
        )

    # ---- CLOSE ---- #
    elif data == "meta_close":
        await query.message.delete()

    # ---- VIEW SINGLE FIELD ---- #
    elif data.startswith("edit_"):
        key = data.replace("edit_", "")
        meta = await digital_botz.get_custom_metadata(user_id)
        value = meta.get(key) or "Not Set"

        await query.message.edit(
            f"🧾 Variable: {key.capitalize()}\n\n"
            f"📖 Description: {DESC[key]}\n\n"
            f"📌 Current Value: {value}",
            reply_markup=field_menu(key)
        )

    # ---- EDIT FIELD (60s TIMER, STAY ON PAGE) ---- #
    elif data.startswith("set_"):
        key = data.replace("set_", "")

        try:
            ask = await bot.ask(
                chat_id=user_id,
                text=(
                    f"🧾 Variable: {key.capitalize()}\n\n"
                    f"📖 Description: {DESC[key]}\n\n"
                    "⏳ Please enter the new value within 60 seconds."
                ),
                filters=filters.text,
                timeout=60
            )

            # Save
            await digital_botz.set_custom_metadata(
                user_id, key, ask.text.strip()
            )
            # ✅ SUCCESS MESSAGE
            await query.answer(
                f"✅ {key.capitalize()} saved successfully",
                show_alert=True
            )
            # Fetch updated value
            meta = await digital_botz.get_custom_metadata(user_id)
            value = meta.get(key) or "Not Set"

            # 🔥 Stay on SAME field page
            await query.message.edit(
                f"🧾 Variable: {key.capitalize()}\n\n"
                f"📖 Description: {DESC[key]}\n\n"
                f"📌 Current Value: {value}",
                reply_markup=field_menu(key)
            )

        except ListenerTimeout:
            await bot.send_message(
                user_id,
                "⏰ Time expired!\nTap Edit again to retry."
            )

    # ---- RESET FIELD (STAY ON PAGE) ---- #
    elif data.startswith("reset_"):
        key = data.replace("reset_", "")
        await digital_botz.set_custom_metadata(user_id, key, None)

        await query.message.edit(
            f"🧾 Variable: {key.capitalize()}\n\n"
            f"📖 Description: {DESC[key]}\n\n"
            "📌 Current Value: Not Set",
            reply_markup=field_menu(key)
        )