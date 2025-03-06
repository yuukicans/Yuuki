import html
import re
from typing import Optional

import telegram
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    DispatcherHandlerStop,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

from FallenRobot import TIGERS, WOLVES, dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler
from FallenRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from FallenRobot.modules.helper_funcs.extraction import (
    extract_text,
    extract_user,
    extract_user_and_text,
)
from FallenRobot.modules.helper_funcs.filters import CustomFilters
from FallenRobot.modules.helper_funcs.misc import split_message
from FallenRobot.modules.helper_funcs.string_handling import split_quotes
from FallenRobot.modules.log_channel import loggable
from FallenRobot.modules.sql import warns_sql as sql
from FallenRobot.modules.sql.approve_sql import is_approved

WARN_HANDLER_GROUP = 9
CURRENT_WARNING_FILTER_STRING = "<b>ғɪʟᴛᴇʀ ᴏʙʀᴏʟᴀɴ sᴀᴀᴛ ɪɴɪ ᴅᴀʟᴀᴍ ᴏʙʀᴏʟᴀɴ ɪɴɪ:</b>\n"


# Not async
def warn(
    user: User,
    chat: Chat,
    reason: str,
    message: Message,
    warner: User = None,
) -> str:
    if is_user_admin(chat, user.id):
        # message.reply_text("sɪᴀʟᴀɴ ᴀᴅᴍɪɴ, ᴍᴇʀᴇᴋᴀ ᴛᴇʀʟᴀʟᴜ ᴊᴀᴜʜ ᴜɴᴛᴜᴋ ᴅɪ ᴘᴜɴᴄʜ!")
        return

    if user.id in TIGERS:
        if warner:
            message.reply_text("Tigers cant be warned.")
        else:
            message.reply_text(
                "Tiger triggered an auto warn filter!\n I can't warn tigers but they should avoid abusing this.",
            )
        return

    if user.id in WOLVES:
        if warner:
            message.reply_text("Wolf disasters are warn immune.")
        else:
            message.reply_text(
                "Wolf Disaster triggered an auto warn filter!\nI can't warn wolves but they should avoid abusing this.",
            )
        return

    if warner:
        warner_tag = mention_html(warner.id, warner.first_name)
    else:
        warner_tag = "Automated warn filter."

    limit, soft_warn = sql.get_warn_setting(chat.id)
    num_warns, reasons = sql.warn_user(user.id, chat.id, reason)
    if num_warns >= limit:
        sql.reset_warns(user.id, chat.id)
        if soft_warn:  # punch
            chat.unban_member(user.id)
            reply = (
                f"<code>❕</code><b>ᴘᴜɴᴄʜ ᴇᴠᴇɴᴛ</b>\n"
                f"<code> </code><b>•  User:</b> {mention_html(user.id, user.first_name)}\n"
                f"<code> </code><b>•  Count:</b> {limit}"
            )

        else:  # ban
            chat.kick_member(user.id)
            reply = (
                f"<code>❕</code><b>Ban Event</b>\n"
                f"<code> </code><b>•  User:</b> {mention_html(user.id, user.first_name)}\n"
                f"<code> </code><b>•  Count:</b> {limit}"
            )

        for warn_reason in reasons:
            reply += f"\n - {html.escape(warn_reason)}"

        # message.bot.send_sticker(chat.id, BAN_STICKER)
        keyboard = None
        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN_BAN\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {warner_tag}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ʀᴇᴀsᴏɴ:</b> {reason}\n"
            f"<b>ᴄᴏᴜɴᴛs:</b> <code>{num_warns}/{limit}</code>"
        )

    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        " ʀᴇᴍᴏᴠᴇ ",
                        callback_data="rm_warn({})".format(user.id),
                    ),
                ],
            ],
        )

        reply = (
            f"<code>❕</code><b>Warn Event</b>\n"
            f"<code> </code><b>•  User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<code> </code><b>•  Count:</b> {num_warns}/{limit}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  Reason:</b> {html.escape(reason)}"

        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {warner_tag}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ʀᴇᴀsᴏɴ:</b> {reason}\n"
            f"<b>ᴄᴏᴜɴᴛs:</b> <code>{num_warns}/{limit}</code>"
        )

    try:
        message.reply_text(reply, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴘᴇsᴀɴ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ":
            # Do not reply
            message.reply_text(
                reply,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
                quote=False,
            )
        else:
            raise
    return log_reason


@user_admin_no_reply
@bot_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_warn\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        res = sql.remove_warn(user_id, chat.id)
        if res:
            update.effective_message.edit_text(
                "ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴅɪʜᴀᴘᴜs ᴏʟᴇʜ {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )
            user_member = chat.get_member(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNWARN\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
            )
        else:
            update.effective_message.edit_text(
                "ᴘᴇɴɢɢᴜɴᴀ sᴜᴅᴀʜ ᴛɪᴅᴀᴋ ᴍᴇᴍɪʟɪᴋɪ ᴘᴇʀɪɴɢᴀᴛᴀɴ.",
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin
@can_restrict
@loggable
def warn_user(update: Update, context: CallbackContext) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    warner: Optional[User] = update.effective_user

    user_id, reason = extract_user_and_text(message, args)
    if message.text.startswith("/d") and message.reply_to_message:
        message.reply_to_message.delete()
    if user_id:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user.id == user_id
        ):
            return warn(
                message.reply_to_message.from_user,
                chat,
                reason,
                message.reply_to_message,
                warner,
            )
        else:
            return warn(chat.get_member(user_id).user, chat, reason, message, warner)
    else:
        message.reply_text("ɪᴅ ᴘᴇɴɢɢᴜɴᴀ ɪɴɪ sᴇᴘᴇʀᴛɪɴʏᴀ ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ.")
    return ""


@user_admin
@bot_admin
@loggable
def reset_warns(update: Update, context: CallbackContext) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user

    user_id = extract_user(message, args)

    if user_id:
        sql.reset_warns(user_id, chat.id)
        message.reply_text("ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴛᴇʟᴀʜ ᴅɪ ᴀᴛᴜʀ ᴜʟᴀɴɢ!")
        warned = chat.get_member(user_id).user
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#RESETWARNS\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(warned.id, warned.first_name)}"
        )
    else:
        message.reply_text("ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴘᴇɴɢɢᴜɴᴀ ʏᴀɴɢ ᴅɪ ᴛᴜᴊᴜ!")
    return ""


def warns(update: Update, context: CallbackContext):
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user_id = extract_user(message, args) or update.effective_user.id
    result = sql.get_warns(user_id, chat.id)

    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = sql.get_warn_setting(chat.id)

        if reasons:
            text = (
                f"ᴜsᴇʀ ɪɴɪ ᴛᴇʟᴀʜ {num_warns}/{limit} ᴍᴇᴍᴘᴇʀɪɴɢᴀᴛᴋᴀɴ, ᴋᴀʀᴇɴᴀ ᴀʟᴀsᴀɴ ʙᴇʀɪᴋᴜᴛ ɪɴɪ:"
            )
            for reason in reasons:
                text += f"\n • {reason}"

            msgs = split_message(text)
            for msg in msgs:
                update.effective_message.reply_text(msg)
        else:
            update.effective_message.reply_text(
                f"ᴜsᴇʀ ᴛᴇʟᴀʜ {num_warns}/{limit} ᴍᴇᴍᴘᴇʀɪɴɢᴀᴛᴋᴀɴ, ᴛᴀᴘɪ ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴀʟᴀsᴀɴ ᴜɴᴛᴜᴋ ʜᴀʟ ᴛᴇʀsᴇʙᴜᴛ.",
            )
    else:
        update.effective_message.reply_text("ᴘᴇɴɢɢᴜɴᴀ ɪɴɪ ᴛɪᴅᴀᴋ ᴍᴇᴍɪʟɪᴋɪ ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴀᴘᴀᴘᴜɴ!")


# Dispatcher handler stop - do not async
@user_admin
def add_warn_filter(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(
        None,
        1,
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) >= 2:
        # set trigger -> lower, so as to avoid adding duplicate filters with different cases
        keyword = extracted[0].lower()
        content = extracted[1]

    else:
        return

    # Note: perhaps handlers can be removed somehow using sql.get_chat_filters
    for handler in dispatcher.handlers.get(WARN_HANDLER_GROUP, []):
        if handler.filters == (keyword, chat.id):
            dispatcher.remove_handler(handler, WARN_HANDLER_GROUP)

    sql.add_warn_filter(chat.id, keyword, content)

    update.effective_message.reply_text(f"ᴘᴇɴᴀɴɢᴀɴᴀɴ ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ ᴜɴᴛᴜᴋ '{keyword}'!")
    raise DispatcherHandlerStop


@user_admin
def remove_warn_filter(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(
        None,
        1,
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) < 1:
        return

    to_remove = extracted[0]

    chat_filters = sql.get_chat_warn_triggers(chat.id)

    if not chat_filters:
        msg.reply_text("ᴛɪᴅᴀᴋ ᴀᴅᴀ ғɪʟᴛᴇʀ ᴘᴇʀɪɴɢᴀᴛᴀɴ ʏᴀɴɢ ᴀᴋᴛɪᴘ ᴅɪsɪɴɪ!")
        return

    for filt in chat_filters:
        if filt == to_remove:
            sql.remove_warn_filter(chat.id, to_remove)
            msg.reply_text("ᴏᴋᴇ, ᴀᴋᴜ ᴀᴋᴀɴ ʙᴇʀʜᴇɴᴛɪ ᴍᴇᴍᴘᴇʀɪɴɢᴀᴛᴋᴀɴ ᴏʀᴀɴɢ ᴜɴᴛᴜᴋ ɪᴛᴜ.")
            raise DispatcherHandlerStop

    msg.reply_text(
        "ɪᴛᴜ ʙᴜᴋᴀɴ ғɪʟᴛᴇʀ ᴘᴇʀɪɴɢᴀᴛᴀɴ sᴀᴀᴛ ɪɴɪ - run /warnlist ᴜɴᴛᴜᴋ sᴇᴍᴜᴀ ғɪʟᴛᴇʀ ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴀᴋᴛɪᴘ.",
    )


def list_warn_filters(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    all_handlers = sql.get_chat_warn_triggers(chat.id)

    if not all_handlers:
        update.effective_message.reply_text("ʙᴇʀɪᴋᴀɴ sᴀʏᴀ ɴᴏᴍᴏʀ sᴇʙᴀɢᴀɪ ᴀʀɢᴜᴍᴇɴ!")
        return

    filter_list = CURRENT_WARNING_FILTER_STRING
    for keyword in all_handlers:
        entry = f" - {html.escape(keyword)}\n"
        if len(entry) + len(filter_list) > telegram.MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML)
            filter_list = entry
        else:
            filter_list += entry

    if filter_list != CURRENT_WARNING_FILTER_STRING:
        update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML)


@loggable
def reply_filter(update: Update, context: CallbackContext) -> str:
    chat: Optional[Chat] = update.effective_chat
    message: Optional[Message] = update.effective_message
    user: Optional[User] = update.effective_user

    if not user:  # Ignore channel
        return

    if user.id == 777000:
        return
    if is_approved(chat.id, user.id):
        return
    chat_warn_filters = sql.get_chat_warn_triggers(chat.id)
    to_match = extract_text(message)
    if not to_match:
        return ""

    for keyword in chat_warn_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            user: Optional[User] = update.effective_user
            warn_filter = sql.get_warn_filter(chat.id, keyword)
            return warn(user, chat, warn_filter.reply, message)
    return ""


@user_admin
@loggable
def set_warn_limit(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].isdigit():
            if int(args[0]) < 3:
                msg.reply_text("ᴍɪɴɪᴍᴀʟ ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴡᴀʀɴ ʟɪᴍɪᴛ 𝟹!")
            else:
                sql.set_warn_limit(chat.id, int(args[0]))
                msg.reply_text("ᴜᴘᴅᴀᴛᴇ ᴘᴇʀɪɴɢᴀᴛᴀɴ ʟɪᴍɪᴛ ᴋᴇ {}".format(args[0]))
                return (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#SET_WARN_LIMIT\n"
                    f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                    f"sᴇᴛ ᴘᴇʀɪɴɢᴀᴛᴀɴ ʟɪᴍɪᴛ ᴋᴇ <code>{args[0]}</code>"
                )
        else:
            msg.reply_text("ʙᴇʀɪᴋᴀɴ sᴀʏᴀ ɴᴏᴍᴏʀ sᴇʙᴀɢᴀɪ ᴀʀɢᴜᴍᴇɴ!")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)

        msg.reply_text("ʙᴀᴛᴀs ᴘᴇʀɪɴɢᴀᴛᴀɴ sᴀᴀᴛ ɪɴɪ {}".format(limit))
    return ""


@user_admin
def set_warn_strength(update: Update, context: CallbackContext):
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].lower() in ("on", "yes"):
            sql.set_warn_strength(chat.id, False)
            msg.reply_text("ᴛᴇʀʟᴀʟᴜ ʙᴀɴʏᴀᴋ ᴘᴇʀɪɴɢᴀᴛᴀɴ sᴇᴋᴀʀᴀɴɢ ᴀᴋᴀɴ ᴍᴇɴɢᴀᴋɪʙᴀᴛᴋᴀɴ ʙᴀɴ!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ᴛᴇʟᴀʜ ᴍᴇɴɢᴀᴋᴛɪᴘᴋᴀɴ ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴋᴇʀᴀs, ᴘᴇɴɢɢᴜɴᴀ ᴀᴋᴀɴ ᴍᴇɴᴅᴀᴘᴀᴛ ᴘᴜɴᴄʜ.(banned)"
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_warn_strength(chat.id, True)
            msg.reply_text(
                "ᴛᴇʀʟᴀʟᴜ ʙᴀɴʏᴀᴋ ᴘᴇʀɪɴɢᴀᴛᴀɴ sᴇᴋᴀʀᴀɴɢ ᴀᴋᴀɴ ᴍᴇɴɢᴀᴋɪʙᴀᴛᴋᴀɴ ᴘᴜɴᴄʜ ɴᴏʀᴍᴀʟ! ᴘᴇɴɢɢᴜɴᴀ ᴀᴋᴀɴ ᴅᴀᴘᴀᴛ ʙᴇʀɢᴀʙᴜɴɢ ʟᴀɢɪ sᴇᴛᴇʟᴀʜ.",
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ᴛᴇʟᴀʜ ᴍᴇɴᴏɴᴀᴋᴛɪᴘᴋᴀɴ ᴋᴜᴀᴛ punches. sᴀʏᴀ ᴀᴋᴀɴ ᴍᴇɴɢɢᴜɴᴀᴋᴀɴ ᴘᴜɴᴄʜ ɴᴏʀᴍᴀʟ ᴀᴅᴀ ᴘᴇɴɢɢᴜɴᴀ."
            )

        else:
            msg.reply_text("sᴀʏᴀ ʜᴀɴʏᴀ ᴍᴇɴɢᴇʀᴛɪ on/yes/no/off!")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)
        if soft_warn:
            msg.reply_text(
                "ᴘᴇʀɪɴɢᴀᴛᴀɴ sᴀᴀᴛ ɪɴɪ ᴅɪ ᴀᴛᴜʀ ᴋᴇ *ᴏᴜɴᴄʜ* ᴘᴇɴɢɢᴜɴᴀ ᴋᴇᴛɪᴋᴀ ᴍᴇʟᴀᴘᴀᴜɪ ʙᴀᴛᴀs .",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            msg.reply_text(
                "ᴘᴇʀɪɴɢᴀᴛᴀɴ sᴀᴀᴛ ɪɴɪ ᴅɪ ᴀᴛᴜʀ ᴋᴇ *ʙᴀɴ* ᴘᴇɴɢɢᴜɴᴀ ᴋᴇᴛɪᴋᴀ ᴍᴇʟᴀᴍᴘᴜɪ ʙᴀᴛᴀs.",
                parse_mode=ParseMode.MARKDOWN,
            )
    return ""


def __stats__():
    return (
        f"• {sql.num_warns()} overall ᴘᴇʀɪɴɢᴀᴛᴀɴ, ᴅɪsᴇʟᴜʀᴜʜ {sql.num_warn_chats()} ᴘᴇsᴀɴ.\n"
        f"• {sql.num_warn_filters()} ғɪʟᴛᴇʀ ᴘᴇʀɪɴɢᴀᴛᴀɴ, ᴅɪ sᴇʟᴜʀᴜʜ {sql.num_warn_filter_chats()} ᴘᴇsᴀɴ."
    )


def __import_data__(chat_id, data):
    for user_id, count in data.get("warns", {}).items():
        for x in range(int(count)):
            sql.warn_user(user_id, chat_id)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    num_warn_filters = sql.num_warn_chat_filters(chat_id)
    limit, soft_warn = sql.get_warn_setting(chat_id)
    return (
        f"ᴏʙʀᴏʟᴀɴ ɪɴɪ ᴍᴇᴍɪʟɪᴋɪ `{num_warn_filters}` ғɪʟᴛᴇʀ ᴘᴇʀɪɴɢᴀᴛᴀɴ. "
        f"ᴅɪʙᴜᴛᴜʜᴋᴀɴ `{limit}` ᴍᴇᴍᴘᴇʀɪɴɢᴀᴛᴋᴀɴ sᴇʙᴇʟᴜᴍ ᴘᴇɴɢɢᴜɴᴀ ᴍᴇɴᴅᴀᴘᴀᴛᴋᴀɴ *{'kicked' if soft_warn else 'banned'}*."
    )


__help__ = """
 ❍ `/warns <userhandle>`*:* ᴅᴀᴘᴀᴛᴋᴀɴ ɴᴏᴍᴏʀ ᴘᴇɴɢɢᴜɴᴀ, ᴅᴀɴ ᴀʟᴀsᴀɴ, ᴘᴇʀɪɴɢᴀᴛᴀɴ.
 ❍ `/warnlist`*:* ᴅᴀғᴛᴀʀ sᴇᴍᴜᴀ ғɪʟᴛᴇʀ ᴘᴇʀɪɴɢᴀᴛᴀɴ sᴀᴀᴛ ɪɴɪ

*Admins only:*
 ❍ `/warn <userhandle>`*:* ᴍᴇᴍᴘᴇʀɪɴɢᴀᴛɪ ᴘᴇɴɢɢᴜɴᴀ, sᴇᴛᴇʟᴀʜ 𝟹 ᴋᴀʟɪ ᴘᴇʀɪɴɢᴀᴛᴀɴ, ᴘᴇɴɢɢᴜɴᴀ ᴀᴋᴀɴ ᴅɪ ʙʟᴏᴋɪʀ ᴅᴀʀɪ ɢʀᴜᴘ.
 ❍ `/dwarn <userhandle>`*:* ᴍᴇᴍᴘᴇʀɪɴɢᴀᴛɪ ᴘᴇɴɢɢᴜɴᴀ, sᴇᴛᴇʟᴀʜ 𝟹 ᴋᴀʟɪ ᴘᴇʀɪɴɢᴀᴛᴀɴ, ᴘᴇɴɢɢᴜɴᴀ ᴀᴋᴀɴ ᴅɪ ʙʟᴏᴋɪʀ ᴅᴀʀɪ ɢʀᴜᴘ.
 ❍ `/resetwarn <userhandle>`*:* ᴍᴇɴɢᴀᴛᴜʀ ᴜʟᴀɴɢ ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴜɴᴛᴜᴋ ᴘᴇɴɢɢᴜɴᴀ.
 ❍ `/addwarn <keyword> <reply message>`*:* ᴍᴇɴɢᴀᴛᴜʀ ғɪʟᴛᴇʀ ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴘᴀᴅᴀ ᴋᴀᴛᴀ ᴋᴜɴᴄɪ ᴛᴇʀᴛᴇɴᴛᴜ, ᴊɪᴋᴀ ᴀɴᴅᴀ ɪɴɢɪɴ ᴋᴀᴛᴀ ᴋᴜɴᴄɪ ᴀɴᴅᴀ \
ᴍᴇɴᴊᴀᴅɪ sᴇʙᴜᴀʜ ᴋᴀʟɪᴍᴀᴛ ᴅᴇɴɢᴀɴ ᴛᴀɴᴅᴀ ᴋᴜᴛɪᴘ, sᴇᴘᴇʀᴛɪ : `/addwarn "very angry" ɪɴɪ ᴀᴅᴀʟᴀʜ ᴘᴇɴɢɢᴜɴᴀ ʏᴀɴɢ ᴍᴀʀᴀʜ`.
 ❍ `/nowarn <keyword>`*:* ʜᴇɴᴛɪᴋᴀɴ ғɪʟᴛᴇʀ ᴘᴇʀɪɴɢᴀᴛᴀɴ
 ❍ `/warnlimit <num>`*:* ᴍᴇɴɢᴀᴛᴜʀ ʟɪᴍɪᴛ ᴘᴇʀɪɴɢᴀᴛᴀɴ
 ❍ `/strongwarn <on/yes/off/no>`*:* ᴊɪᴋᴀ ᴅɪᴀᴛᴜʀ ᴋᴇ ᴀᴋᴛɪᴘ, ᴍᴇʟᴀᴍᴘᴀᴜɪ ʙᴀᴛᴀs ᴘᴇʀɪɴɢᴀᴛᴀɴ ᴀᴋᴀɴ ᴍᴇɴɢᴀᴋɪʙᴀᴛᴋᴀɴ ʟᴀʀᴀɴɢᴀɴ.
"""

__mod_name__ = "ᴡᴀʀɴs"

WARN_HANDLER = CommandHandler(
    ["warn", "dwarn"], warn_user, filters=Filters.chat_type.groups, run_async=True
)
RESET_WARN_HANDLER = CommandHandler(
    ["resetwarn", "resetwarns"],
    reset_warns,
    filters=Filters.chat_type.groups,
    run_async=True,
)
CALLBACK_QUERY_HANDLER = CallbackQueryHandler(
    button, pattern=r"rm_warn", run_async=True
)
MYWARNS_HANDLER = DisableAbleCommandHandler(
    "warns", warns, filters=Filters.chat_type.groups, run_async=True
)
ADD_WARN_HANDLER = CommandHandler(
    "addwarn", add_warn_filter, filters=Filters.chat_type.groups, run_async=True
)
RM_WARN_HANDLER = CommandHandler(
    ["nowarn", "stopwarn"],
    remove_warn_filter,
    filters=Filters.chat_type.groups,
    run_async=True,
)
LIST_WARN_HANDLER = DisableAbleCommandHandler(
    ["warnlist", "warnfilters"],
    list_warn_filters,
    filters=Filters.chat_type.groups,
    admin_ok=True,
    run_async=True,
)
WARN_FILTER_HANDLER = MessageHandler(
    CustomFilters.has_text & Filters.chat_type.groups,
    reply_filter,
    run_async=True,
)
WARN_LIMIT_HANDLER = CommandHandler(
    "warnlimit", set_warn_limit, filters=Filters.chat_type.groups, run_async=True
)
WARN_STRENGTH_HANDLER = CommandHandler(
    "strongwarn",
    set_warn_strength,
    filters=Filters.chat_type.groups,
    run_async=True,
)

dispatcher.add_handler(WARN_HANDLER)
dispatcher.add_handler(CALLBACK_QUERY_HANDLER)
dispatcher.add_handler(RESET_WARN_HANDLER)
dispatcher.add_handler(MYWARNS_HANDLER)
dispatcher.add_handler(ADD_WARN_HANDLER)
dispatcher.add_handler(RM_WARN_HANDLER)
dispatcher.add_handler(LIST_WARN_HANDLER)
dispatcher.add_handler(WARN_LIMIT_HANDLER)
dispatcher.add_handler(WARN_STRENGTH_HANDLER)
dispatcher.add_handler(WARN_FILTER_HANDLER, WARN_HANDLER_GROUP)
