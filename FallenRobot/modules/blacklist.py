import html
import re

from telegram import ChatPermissions, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, MessageHandler
from telegram.utils.helpers import mention_html

import FallenRobot.modules.sql.blacklist_sql as sql
from FallenRobot import LOGGER, dispatcher
from FallenRobot.modules.connection import connected
from FallenRobot.modules.disable import DisableAbleCommandHandler
from FallenRobot.modules.helper_funcs.alternate import send_message, typing_action
from FallenRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin
from FallenRobot.modules.helper_funcs.extraction import extract_text
from FallenRobot.modules.helper_funcs.misc import split_message
from FallenRobot.modules.helper_funcs.string_handling import extract_time
from FallenRobot.modules.log_channel import loggable
from FallenRobot.modules.sql.approve_sql import is_approved
from FallenRobot.modules.warns import warn

BLACKLIST_GROUP = 11


@user_admin
@typing_action
def blacklist(update, context):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    filter_list = "ʙᴇʀɪᴋᴜᴛ ɪɴɪ ᴀᴅᴀʟᴀʜ ᴅᴀғᴛᴀʀ ʙʟᴀᴄᴋʟɪsᴛ ᴅɪ <b>{}</b>:\n".format(chat_name)

    all_blacklisted = sql.get_chat_blacklist(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_blacklisted:
            filter_list += "<code>{}</code>\n".format(html.escape(trigger))
    else:
        for trigger in all_blacklisted:
            filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    # for trigger in all_blacklisted:
    #     filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(filter_list)
    for text in split_text:
        if filter_list == "ʙᴇʀɪᴋᴜᴛ ɪɴɪ ᴀᴅᴀʟᴀʜ ᴅᴀғᴛᴀʀ ʙʟᴀᴄᴋʟɪsᴛ ᴅɪ <b>{}</b>:\n".format(
            html.escape(chat_name)
        ):
            send_message(
                update.effective_message,
                "ʙᴇʟᴜᴍ ᴀᴅᴀ ᴅᴀғᴛᴀʀ ʙʟᴀᴄᴋʟɪsᴛ <b>{}</b>!".format(html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )
            return
        send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@user_admin
@typing_action
def add_blacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    reply_msg = msg.reply_to_message  # Ambil pesan yang di-reply

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if reply_msg:  # Jika ada pesan yang di-reply
        text = reply_msg.text
    else:
        words = msg.text.split(None, 1)
        if len(words) > 1:
            text = words[1]
        else:
            send_message(
                update.effective_message,
                "ʙᴇʀɪᴋᴀɴ sᴀʏᴀ ᴋᴀᴛᴀ-ᴋᴀᴛᴀ ᴜɴᴛᴜᴋ ᴅɪ ᴍᴀsᴜᴋᴀɴ ᴋᴇᴅᴀғᴛᴀʀ ʙʟᴀᴄᴋʟɪsᴛ.",
            )
            return

    to_blacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )
    
    for trigger in to_blacklist:
        sql.add_to_blacklist(chat_id, trigger.lower())

    if len(to_blacklist) == 1:
        send_message(
            update.effective_message,
            "ᴍᴇɴᴀᴍʙᴀʜ ᴋᴀᴛᴀ ʙʟᴀᴄᴋʟɪsᴛ : \n- <code>{}</code> \nᴅɪ ɢʀᴏᴜᴘs: <b>{}</b>!".format(
                html.escape(to_blacklist[0]), html.escape(chat_name)
            ),
            parse_mode=ParseMode.HTML,
        )
    else:
        send_message(
            update.effective_message,
            "ᴍᴇɴᴀᴍʙᴀʜ ᴋᴀᴛᴀ ʙʟᴀᴄᴋʟɪsᴛ: \n- <code>{}</code> \nᴅɪ ɢʀᴏᴜᴘs: <b>{}</b>!".format(
                len(to_blacklist), html.escape(chat_name)
            ),
            parse_mode=ParseMode.HTML,
        )


@user_admin
@user_admin
@typing_action
def unblacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )
        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_blacklist(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    "ᴍᴇɴɢʜᴀᴘᴜs ᴋᴀᴛᴀ ʙʟᴀᴄᴋʟɪsᴛ: \n- <code>{}</code> \nᴅɪ ɢʀᴏᴜᴘ <b>{}</b>!".format(
                        html.escape(to_unblacklist[0]), html.escape(chat_name)
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                send_message(
                    update.effective_message, "ᴋᴀᴛᴀ ɪɴɪ ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴅɪ ᴅᴀғᴛᴀʀ ʙʟᴀᴄᴋʟɪsᴛ!"
                )

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                "ᴍᴇɴɢʜᴀᴘᴜs ᴋᴀᴛᴀ ʙʟᴀᴄᴋʟɪsᴛ: \n- <code>{}</code> \nᴅɪ ɢʀᴜᴏᴘ <b>{}</b>!".format(
                    successful, html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "ᴋᴀᴛᴀ ɪɴɪ ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴅɪ ᴅᴀғᴛᴀʀ ʙʟᴀᴄᴋʟɪsᴛ, ᴊᴀᴅᴜ ᴛɪᴅᴀᴋ ᴀᴅᴀ ʏᴀɴɢ ᴅɪ ʜᴀᴘᴜs.",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "ᴍᴇɴɢʜᴀᴘᴜs ᴋᴀᴛᴀ ʙʟᴀᴄᴋʟɪsᴛ: \n- <code>{}</code> ᴅɪ ɢʀᴏᴜᴘ : {} ᴛɪᴅᴀᴋ ᴀᴅᴀ, "
                "ᴊᴀᴅɪ ᴛɪᴅᴀᴋ ᴅɪ ʜᴀᴘᴜs.".format(
                    successful, len(to_unblacklist) - successful
                ),
                parse_mode=ParseMode.HTML,
            )
    else:
        send_message(
            update.effective_message,
            "ʙᴇʀɪᴋᴀɴ sᴀʏᴀ ᴋᴀᴛᴀ-ᴋᴀᴛᴀ ᴜɴᴛᴜᴋ ᴅɪ ʜᴀᴘᴜs ᴅᴀʀɪ ᴅᴀғᴛᴀʀ ʙʟᴀᴄᴋʟɪsᴛ!",
	    )

@loggable
@user_admin
@typing_action
def blacklist_mode(update, context):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "ᴘᴇʀɪɴᴛᴀʜ ɪɴɪ ᴄᴜᴍᴀɴ ʙɪsᴀ ᴅɪ ɢʀᴏᴜᴘs ʙᴜᴋᴀɴ ᴅɪ ʀᴏᴏᴍ ᴄʜᴀᴛ",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "do nothing"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "ᴍᴇɴɢʜᴀᴘᴜs ʙʟ "
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "warn the sender"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "mute the sender"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "kick the sender"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "ban the sender"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """It looks like you tried to set time value for blacklist but you didn't specified time; Try, `/blacklistmode tban <timevalue>`.
				
Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """Invalid time value!
Example of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "temporarily ban for {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """It looks like you tried to set time value for blacklist but you didn't specified  time; try, `/blacklistmode tmute <timevalue>`.

Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """Invalid time value!
Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "temporarily mute for {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "I only understand: off/del/warn/ban/kick/mute/tban/tmute!",
            )
            return ""
        if conn:
            text = "Changed blacklist mode: `{}` in *{}*!".format(
                settypeblacklist, chat_name
            )
        else:
            text = "Changed blacklist mode: `{}`!".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode="markdown")
        return (
            "<b>{}:</b>\n"
            "<b>Admin:</b> {}\n"
            "Changed the blacklist mode. will {}.".format(
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
                settypeblacklist,
            )
        )
    else:
        getmode, getvalue = sql.get_blacklist_setting(chat.id)
        if getmode == 0:
            settypeblacklist = "do nothing"
        elif getmode == 1:
            settypeblacklist = "delete"
        elif getmode == 2:
            settypeblacklist = "warn"
        elif getmode == 3:
            settypeblacklist = "mute"
        elif getmode == 4:
            settypeblacklist = "kick"
        elif getmode == 5:
            settypeblacklist = "ban"
        elif getmode == 6:
            settypeblacklist = "temporarily ban for {}".format(getvalue)
        elif getmode == 7:
            settypeblacklist = "temporarily mute for {}".format(getvalue)
        if conn:
            text = "Current blacklistmode: *{}* in *{}*.".format(
                settypeblacklist, chat_name
            )
        else:
            text = "Current blacklistmode: *{}*.".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)


@user_not_admin
def del_blacklist(update, context):
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    bot = context.bot
    to_match = extract_text(message)
    if not to_match:
        return
    if is_approved(chat.id, user.id):
        return
    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_blacklist(chat.id)
    for trigger in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            try:
                if getmode == 0:
                    return
                elif getmode == 1:
                    try:
                        message.delete()
                    except BadRequest:
                        pass
                elif getmode == 2:
                    try:
                        message.delete()
                    except BadRequest:
                        pass
                    warn(
                        update.effective_user,
                        chat,
                        ("Using blacklisted trigger: {}".format(trigger)),
                        message,
                        update.effective_user,
                    )
                    return
                elif getmode == 3:
                    message.delete()
                    bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"Muted {user.first_name} for using Blacklisted word: {trigger}!",
                    )
                    return
                elif getmode == 4:
                    message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        bot.sendMessage(
                            chat.id,
                            f"Kicked {user.first_name} for using Blacklisted word: {trigger}!",
                        )
                    return
                elif getmode == 5:
                    message.delete()
                    chat.ban_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        f"Banned {user.first_name} for using Blacklisted word: {trigger}",
                    )
                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.ban_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        f"Banned {user.first_name} until '{value}' for using Blacklisted word: {trigger}!",
                    )
                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        until_date=mutetime,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"Muted {user.first_name} until '{value}' for using Blacklisted word: {trigger}!",
                    )
                    return
            except BadRequest as excp:
                if excp.message != "Message to delete not found":
                    LOGGER.exception("Error while deleting blacklist message.")
            break


def __import_data__(reply_text, data):
    # set chat blacklist
    blacklist = data.get("blacklist", {})
    for trigger in blacklist:
        sql.add_to_blacklist(reply_text, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_blacklist_chat_filters(chat_id)
    return "There are {} blacklisted words.".format(blacklisted)


def __stats__():
    return "• {} Bʟᴀᴄᴋʟɪsᴛ ᴛʀɪɢᴇʀs, ᴀᴄʀᴏss {} ᴄʜᴀᴛs.".format(
        sql.num_blacklist_filters(), sql.num_blacklist_filter_chats()
    )


__mod_name__ = "ʙʟᴀᴄᴋʟɪsᴛ"

__help__ = """
ᴍᴏᴅᴜʟᴇ ɪɴɪ ʙᴇʀғᴜɴɢsɪ ᴜɴᴛᴜᴋ ᴍᴇᴍғɪʟᴛᴇʀ ᴋᴀᴛᴀ ᴋᴀᴛᴀ ʏᴀɴɢ ʙᴇʀsɪғᴀᴛ ᴍᴇɴɢᴀɴɢɢᴜ ᴅᴀɴ ʙᴇʀɢᴜɴᴀ ᴜɴᴛᴜᴋ ᴍᴇɴɢʜɪɴᴅᴀʀɪ ᴅᴀʀɪ sᴘᴀᴍᴍᴇʀ!

*ɴᴋᴛᴇs*: ᴋᴀᴛᴀ ʙʟᴀᴄᴋʟɪsᴛ ᴛɪᴅᴀᴋ ʙᴇʀғᴜɴɢsɪ ʙᴀɢɪ ᴀᴅᴍɪɴ.


 ❍ /blacklist*:* ᴍᴇʟɪʜᴀᴛ ᴅᴀғᴛᴀʀ ᴋᴀᴛᴀ ʏᴀɴɢ ᴅɪ ʙʟᴀᴄᴋʟɪsᴛ.

Aᴅᴍɪɴ Oɴʟʏ:
 ❍ /bl or /addbl <triggers>*:* ᴄᴏʙᴀɪɴ ᴀᴊᴀ sᴇɴᴅɪʀɪ.
 ❍ /un or /unbl <triggers>*:* ᴄᴏʙᴀɪɴ ᴀᴊᴀ sᴇɴᴅɪʀɪ.
 ❍ /blacklistmode <off/del/warn/ban/kick/mute/tban/tmute>*:* ᴄᴏʙᴀɪɴ ᴀᴊᴀ sᴇɴᴅɪʀɪ.
"""

BLACKLIST_HANDLER = DisableAbleCommandHandler(
    "blacklist", blacklist, pass_args=True, admin_ok=True, run_async=True
)
ADD_BLACKLIST_HANDLER = CommandHandler("bl", add_blacklist, run_async=True)
UNBLACKLIST_HANDLER = CommandHandler("unbl", unblacklist, run_async=True)
BLACKLISTMODE_HANDLER = CommandHandler(
    "blacklistmode", blacklist_mode, pass_args=True, run_async=True
)
BLACKLIST_DEL_HANDLER = MessageHandler(
    (Filters.text | Filters.command | Filters.sticker | Filters.photo)
    & Filters.chat_type.groups,
    del_blacklist,
    allow_edit=True,
    run_async=True,
)

dispatcher.add_handler(BLACKLIST_HANDLER)
dispatcher.add_handler(ADD_BLACKLIST_HANDLER)
dispatcher.add_handler(UNBLACKLIST_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_DEL_HANDLER, group=BLACKLIST_GROUP)

__handlers__ = [
    BLACKLIST_HANDLER,
    ADD_BLACKLIST_HANDLER,
    UNBLACKLIST_HANDLER,
    BLACKLISTMODE_HANDLER,
    (BLACKLIST_DEL_HANDLER, BLACKLIST_GROUP),
	]
