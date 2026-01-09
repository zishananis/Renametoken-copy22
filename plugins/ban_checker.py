from pyrogram import Client, filters
import datetime
from helper.database import digital_botz


@Client.on_message(filters.private, group=-1)
async def ban_user_checker(bot, message):
    user_id = message.from_user.id

    ban_status = await digital_botz.get_ban_status(user_id)

    if not ban_status:
        return

    if ban_status.get("is_banned"):
        try:
            ban_date = datetime.datetime.fromisoformat(
                ban_status.get("banned_on")
            ).date()
        except Exception:
            ban_date = datetime.date.today()

        duration = ban_status.get("ban_duration", 0)

        # 0 = permanent ban
        if duration == 0 or (datetime.date.today() - ban_date).days < duration:
            await message.reply(
                "Sorry Sir 😔 You are Banned!\n"
                "Please Contact - @sitaratoons_support"
            )
            return  # ⛔ yahin ruk jao, aage koi command nahi chalegi