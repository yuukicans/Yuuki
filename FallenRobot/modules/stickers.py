import math
import os
import urllib.request as urllib
from html import escape
from io import BytesIO

import requests
from bs4 import BeautifulSoup as bs
from PIL import Image
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    TelegramError,
    Update,
)
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html

from FallenRobot import dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler

combot_stickers_url = "https://combot.org/telegram/stickers?q="


def sticker_count(bot: Bot, pname: str) -> int:
    hmm = bot._request.post(
        f"{bot.base_url}/getStickerSet",
        {
            "name": pname,
        },
    )
    return len(hmm["stickers"])


def stickerid(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        update.effective_message.reply_text(
            "Hey "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", The sticker id you are replying is :\n <code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get id sticker",
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )


def cb_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    split = msg.text.split(" ", 1)
    if len(split) == 1:
        msg.reply_text("Provide some name to search for pack.")
        return
    text = requests.get(combot_stickers_url + split[1]).text
    soup = bs(text, "lxml")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    titles = soup.find_all("div", "sticker-pack__title")
    if not results:
        msg.reply_text("No results found :(.")
        return
    reply = f"Stickers for *{split[1]}*:"
    for result, title in zip(results, titles):
        link = result["href"]
        reply += f"\n• [{title.get_text()}]({link})"
    msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


def getsticker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        is_anim = msg.reply_to_message.sticker.is_animated
        sticker_data = bot.get_file(file_id).download(out=BytesIO())
        sticker_data.seek(0)
        filename = "animated_sticker.tgs.hmm_" if is_anim else "sticker.png"

        bot.send_document(
            update.effective_chat.id,
            document=sticker_data,
            filename=filename,
        )
    else:
        update.effective_message.reply_text(
            "ᴛᴏʟᴏɴɢ ʙᴀʟᴀs sᴛɪᴄᴋᴇʀ ᴀɢᴀʀ sᴀʏᴀ ʙɪsᴀ ᴍᴇɴᴀᴍʙᴀʜᴋᴀɴ ᴋᴇ ᴘɴɢ."
        )


def kang(update: Update, context: CallbackContext):
    msg = update.effective_message
    user = update.effective_user
    args = context.args
    packnum = 0
    packname = "a" + str(user.id) + "_by_" + context.bot.username
    packname_found = 0
    max_stickers = 120
    while packname_found == 0:
        try:
            if sticker_count(context.bot, packname) >= max_stickers:
                packnum += 1
                packname = (
                    "a"
                    + str(packnum)
                    + "_"
                    + str(user.id)
                    + "_by_"
                    + context.bot.username
                )
            else:
                packname_found = 1
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = 1
    kangsticker = "kangsticker.png"
    is_animated = False
    file_id = ""

    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            file_id = msg.reply_to_message.sticker.file_id

        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("Yea, I can't kang that.")

        kang_file = context.bot.get_file(file_id)
        if not is_animated:
            kang_file.download("kangsticker.png")
        else:
            kang_file.download("kangsticker.tgs")

        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤔"

        if not is_animated:
            try:
                im = Image.open(kangsticker)
                maxsize = (512, 512)
                if (im.width and im.height) < 512:
                    size1 = im.width
                    size2 = im.height
                    if im.width > im.height:
                        scale = 512 / size1
                        size1new = 512
                        size2new = size2 * scale
                    else:
                        scale = 512 / size2
                        size1new = size1 * scale
                        size2new = 512
                    size1new = math.floor(size1new)
                    size2new = math.floor(size2new)
                    sizenew = (size1new, size2new)
                    im = im.resize(sizenew)
                else:
                    im.thumbnail(maxsize)
                if not msg.reply_to_message.sticker:
                    im.save(kangsticker, "PNG")
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open("kangsticker.png", "rb"),
                    emojis=sticker_emoji,
                )
                msg.reply_text(
                    f"ʙᴇʀʜᴀsʟ ᴍᴇɴᴀᴍʙᴀʜᴋᴀɴ sᴛɪᴄᴋᴇʀ ᴋᴇ [pack](t.me/addstickers/{packname})"
                    + f"\nEmoji is: {sticker_emoji}",
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN,
                )

            except OSError as e:
                msg.reply_text("I can only kang images m8.")
                print(e)
                return

            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        png_sticker=open("kangsticker.png", "rb"),
                    )
                elif e.message == "Sticker_png_dimensions":
                    im.save(kangsticker, "PNG")
                    context.bot.add_sticker_to_set(
                        user_id=user.id,
                        name=packname,
                        png_sticker=open("kangsticker.png", "rb"),
                        emojis=sticker_emoji,
                    )
                    msg.reply_text(
                        f"ʙᴇʀʜᴀsɪʟ ᴍᴇɴᴀᴍʙᴀʜᴋᴀɴ sᴛɪᴄᴋᴇʀ ᴋᴇ [pack](t.me/addstickers/{packname})"
                        + f"\nEmoji is: {sticker_emoji}",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                elif e.message == "ᴋᴇsᴀʟᴀʜᴀɴ sᴛɪᴄᴋᴇʀ ᴇᴍᴏᴊɪ":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Stickers_too_much":
                    msg.reply_text("Max packsize reached. Press F to pay respecc.")
                elif e.message == "sᴇʀᴠᴇʀ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ: sᴛɪᴄᴋᴇʀ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ (500)":
                    msg.reply_text(
                        "ʙᴇʀʜᴀsɪʟ ᴍᴇɴᴀᴍʙᴀʜᴋᴀɴ sᴛɪᴄᴋᴇʀ ᴋᴇ [pack](t.me/addstickers/%s)"
                        % packname
                        + "\n"
                        "Emoji is:" + " " + sticker_emoji,
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                print(e)

        else:
            packname = "animated" + str(user.id) + "_by_" + context.bot.username
            packname_found = 0
            max_stickers = 50
            while packname_found == 0:
                try:
                    if sticker_count(context.bot, packname) >= max_stickers:
                        packnum += 1
                        packname = (
                            "animated"
                            + str(packnum)
                            + "_"
                            + str(user.id)
                            + "_by_"
                            + context.bot.username
                        )
                    else:
                        packname_found = 1
                except TelegramError as e:
                    if e.message == "Stickerset_invalid":
                        packname_found = 1
            try:
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    tgs_sticker=open("kangsticker.tgs", "rb"),
                    emojis=sticker_emoji,
                )
                msg.reply_text(
                    f"ʙᴇʀʜᴀsɪʟ ᴍᴇɴᴀᴍʙᴀʜᴋᴀɴ sᴛɪᴄᴋᴇʀ ᴋᴇ [pack](t.me/addstickers/{packname})"
                    + f"\nEmoji is: {sticker_emoji}",
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN,
                )
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        tgs_sticker=open("kangsticker.tgs", "rb"),
                    )
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "sᴇʀᴠᴇʀ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ: sᴛɪᴄᴋᴇʀ ᴛɪᴅᴀᴋ ᴅɪ ᴛᴇᴍᴜᴋᴀɴ (500)":
                    msg.reply_text(
                        "sᴛɪᴄᴋᴇʀ ʙᴇʀʜᴀsɪʟ ᴅɪ ᴛᴀᴍʙᴀʜᴋᴀɴ ᴋᴇ [pack](t.me/addstickers/%s)"
                        % packname
                        + "\n"
                        "Emoji is:" + " " + sticker_emoji,
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                print(e)

    elif args:
        try:
            try:
                urlemoji = msg.text.split(" ")
                png_sticker = urlemoji[1]
                sticker_emoji = urlemoji[2]
            except IndexError:
                sticker_emoji = "🤔"
            urllib.urlretrieve(png_sticker, kangsticker)
            im = Image.open(kangsticker)
            maxsize = (512, 512)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if im.width > im.height:
                    scale = 512 / size1
                    size1new = 512
                    size2new = size2 * scale
                else:
                    scale = 512 / size2
                    size1new = size1 * scale
                    size2new = 512
                size1new = math.floor(size1new)
                size2new = math.floor(size2new)
                sizenew = (size1new, size2new)
                im = im.resize(sizenew)
            else:
                im.thumbnail(maxsize)
            im.save(kangsticker, "PNG")
            msg.reply_photo(photo=open("kangsticker.png", "rb"))
            context.bot.add_sticker_to_set(
                user_id=user.id,
                name=packname,
                png_sticker=open("kangsticker.png", "rb"),
                emojis=sticker_emoji,
            )
            msg.reply_text(
                f"sᴛɪᴄᴋᴇʀ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ ᴋᴇ [pack](t.me/addstickers/{packname})"
                + f"\nEmoji is: {sticker_emoji}",
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )
        except OSError as e:
            msg.reply_text("ᴀᴋᴜ ʜᴀɴʏᴀ ʙɪsᴀ ᴋᴀɴɢ ɢᴀᴍʙᴀʀ ᴍ𝟾.")
            print(e)
            return
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                makepack_internal(
                    update,
                    context,
                    msg,
                    user,
                    sticker_emoji,
                    packname,
                    packnum,
                    png_sticker=open("kangsticker.png", "rb"),
                )
            elif e.message == "Sticker_png_dimensions":
                im.save(kangsticker, "PNG")
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open("kangsticker.png", "rb"),
                    emojis=sticker_emoji,
                )
                msg.reply_text(
                    "sᴛɪᴄᴋᴇʀ ʙᴇʀʜᴀsɪʟ ᴅɪ ᴛᴀᴍʙᴀʜᴋᴀɴ ᴋᴇ [pack](t.me/addstickers/%s)"
                    % packname
                    + "\n"
                    + "Emoji is:"
                    + " "
                    + sticker_emoji,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN,
                )
            elif e.message == "Invalid sticker emojis":
                msg.reply_text("Invalid emoji(s).")
            elif e.message == "Stickers_too_much":
                msg.reply_text("Max packsize reached. Press F to pay respecc.")
            elif e.message == "Internal Server Error: sticker set not found (500)":
                msg.reply_text(
                    "Sticker successfully added to [pack](t.me/addstickers/%s)"
                    % packname
                    + "\n"
                    "Emoji is:" + " " + sticker_emoji,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN,
                )
            print(e)
    else:
        packs = "sɪʟᴀʜᴋᴀɴ ʙᴀʟᴀs sᴛɪᴄᴋᴇʀ, ᴀᴛᴀᴜ ɢᴀᴍʙᴀʀ ᴜɴᴛᴜᴋ ᴍᴇɴɢᴇᴛᴀʜᴜɪ ɴʏᴀ!\nᴏʜ, ɴɢᴏᴍᴏɴɢ ɴɢᴏᴍᴏɴɢ ɪɴɪ ʀᴀɴsᴇʟᴍᴜ:\n"
        if packnum > 0:
            firstpackname = "a" + str(user.id) + "_by_" + context.bot.username
            for i in range(0, packnum + 1):
                if i == 0:
                    packs += f"[pack](t.me/addstickers/{firstpackname})\n"
                else:
                    packs += f"[pack{i}](t.me/addstickers/{packname})\n"
        else:
            packs += f"[pack](t.me/addstickers/{packname})"
        msg.reply_text(
            packs, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN
        )
    try:
        if os.path.isfile("kangsticker.png"):
            os.remove("kangsticker.png")
        elif os.path.isfile("kangsticker.tgs"):
            os.remove("kangsticker.tgs")
    except:
        pass


def makepack_internal(
    update,
    context,
    msg,
    user,
    emoji,
    packname,
    packnum,
    png_sticker=None,
    tgs_sticker=None,
):
    name = user.first_name
    name = name[:50]
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = " " + str(packnum)
        if png_sticker:
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name}s kang pack" + extra_version,
                png_sticker=png_sticker,
                emojis=emoji,
            )
        if tgs_sticker:
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name}s animated kang pack" + extra_version,
                tgs_sticker=tgs_sticker,
                emojis=emoji,
            )

    except TelegramError as e:
        print(e)
        if e.message == "ɴᴀᴍᴀ sᴇᴛ sᴛɪᴄᴋᴇʀ sᴜᴅᴀʜ ᴅɪ ɪsɪ":
            msg.reply_text(
                "ᴘᴀᴋᴇᴛ ᴀɴᴅᴀ ᴅɪᴛᴇᴍᴜᴋᴀɴ [here](t.me/addstickers/%s)" % packname,
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )
        elif e.message in ("Peer_id_invalid", "ʙᴏᴛ ᴅɪ ʙʟᴏᴋɪʀ ᴏʟᴇʜ ᴘᴇɴɢɢᴜɴᴀ"):
            msg.reply_text(
                "ʜᴜʙᴜɴɢɪ sᴀʏᴀ ᴅɪ ᴄʜᴀᴛ first.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴛᴀʀᴛ", url=f"t.me/{context.bot.username}"
                            )
                        ]
                    ]
                ),
            )
        elif e.message == "ᴋᴇsᴀʟᴀʜᴀɴ sᴇʀᴠᴇʀ ɪɴᴛᴇʀɴᴀʟ, sᴇᴛ sᴛɪᴄᴋᴇʀ ʏᴀɴɢ ᴅɪ ʙᴜᴀᴛ ᴛɪᴅᴀᴋ ᴅɪ ᴛᴇᴍᴜᴋᴀɴ (500)":
            msg.reply_text(
                "ᴘᴀᴋᴇᴛ sᴛɪᴄᴋᴇʀ ʙᴇʀʜᴀsɪʟ ᴅɪ ʙᴜᴀᴛ, ᴅᴀᴘᴀᴛᴋᴀɴ sᴇɢᴇʀᴀ [here](t.me/addstickers/%s)"
                % packname,
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )
        return

    if success:
        msg.reply_text(
            "ᴘᴀᴋᴇᴛ sᴛɪᴄᴋᴇʀ ʙᴇʀʜᴀsɪʟ ᴅɪ ʙᴜᴀᴛ, ᴅᴀᴘᴀᴛᴋᴀɴ sᴇɢᴇʀᴀ [here](t.me/addstickers/%s)"
            % packname,
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        msg.reply_text("ɢᴀɢᴀʟ ᴍᴇᴍʙᴜᴀᴛ ᴘᴀᴋᴇᴛ sᴛɪᴄᴋᴇʀ ᴀɴᴅᴀ, ᴍᴜɴɢᴋɪɴ ᴋᴀʀɴᴀ ʙʟᴀᴄᴋ ᴍᴀɢɪᴄ.")


__help__ = """
 ❍ /stickerid*:* ʙᴀʟᴀs sᴛɪᴄᴋᴇʀ ᴋᴇᴘᴀᴅᴀ sᴀʏᴀ ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴇʀɪ ᴛᴀʜᴜ ᴀɴᴅᴀ ɪᴅ ʙᴇʀᴋᴀsɴʏᴀ.
 ❍ /getsticker*:* ʙᴀʟᴀs sᴛɪᴄᴋᴇʀ ᴋᴇᴘᴀᴅᴀ sᴀʏᴀ ᴜɴᴛᴜᴋ ᴍᴇɴɢᴜɴɢɢᴀʜ ʙᴇʀᴋᴀs ᴘɴɢ ᴍᴇɴᴛᴀʜɴʏᴀ.
 ❍ /kang*:* ʙᴀʟᴀs sᴛɪᴄᴋᴇʀ ᴜɴᴛᴜᴋ ᴍᴇɴᴀᴍʙᴀʜ ᴋᴇ ᴘᴀᴋᴇᴛ ᴀɴᴅᴀ.
 ❍ /stickers*:* ᴛᴇᴍᴜᴋᴀɴ sᴛɪᴄᴋᴇʀ ᴜɴᴛᴜᴋ ɪsᴛɪʟᴀʜ ᴛᴇʀᴛᴇɴᴛᴜ ᴅɪ ᴄᴀᴛᴀʟᴏɢ sᴛɪᴄᴋᴇʀ ᴄᴏᴍʙᴏᴛ
"""

__mod_name__ = "sᴛɪᴄᴋᴇʀs"

STICKERID_HANDLER = DisableAbleCommandHandler("stickerid", stickerid, run_async=True)
GETSTICKER_HANDLER = DisableAbleCommandHandler("getsticker", getsticker, run_async=True)
KANG_HANDLER = DisableAbleCommandHandler("kang", kang, admin_ok=True, run_async=True)
STICKERS_HANDLER = DisableAbleCommandHandler("stickers", cb_sticker, run_async=True)

dispatcher.add_handler(STICKERS_HANDLER)
dispatcher.add_handler(STICKERID_HANDLER)
dispatcher.add_handler(GETSTICKER_HANDLER)
dispatcher.add_handler(KANG_HANDLER)
