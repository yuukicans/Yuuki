import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

from FallenRobot import BOT_NAME, BOT_USERNAME, dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler


def handwrite(update: Update, context: CallbackContext):
    message = update.effective_message
    if message.reply_to_message:
        text = message.reply_to_message.text
    else:
        text = update.effective_message.text.split(None, 1)[1]
    m = message.reply_text("ᴍᴇɴᴜʟɪꜱ ᴛᴇxᴛ ᴀɴᴅᴀ...")
    req = requests.get(f"https://api.sdbots.tk/write?text={text}").url
    message.reply_photo(
        photo=req,
        caption=f"""
ʙᴇʀʜᴀꜱɪʟ ᴍᴇɴᴜʟɪꜱ ᴛᴇxᴛ 💘

✨**ᴅɪᴛᴜʟɪs ᴏʟᴇʜ :** [{BOT_NAME}](https://t.me/{BOT_USERNAME})
✨**ᴘᴇʀᴍɪɴᴛᴀᴀɴ ᴅᴀʀɪ :** {update.effective_user.first_name}
❄ **ʟɪɴᴋ :** `{req}`""",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("• ᴛᴇʟᴇɢʀᴀᴩʜ •", url=req),
                ],
            ]
        ),
    )
    m.delete()


__help__ = """
 ᴍᴇɴᴜʟɪsᴋᴀɴ ᴛᴇᴋs ʏᴀɴɢ ᴅɪ ʙᴇʀɪᴋᴀɴ ᴘᴀᴅᴀ ʜᴀʟᴀᴍᴀɴ ᴋᴇʀᴛᴀs ᴅᴇɴɢᴀɴ ᴘᴇɴᴀ 🖊

❍ /write <text> *:*ᴍᴇɴᴜʟɪs ᴘᴇsᴀɴ ᴛᴇᴋs.
"""

WRITE_HANDLER = DisableAbleCommandHandler("write", handwrite, run_async=True)
dispatcher.add_handler(WRITE_HANDLER)

__mod_name__ = "ᴡʀɪᴛᴇᴛᴏᴏʟ"

__command_list__ = ["write"]
__handlers__ = [WRITE_HANDLER]
