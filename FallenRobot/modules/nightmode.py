from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import functions, types
from telethon.tl.types import ChatBannedRights

from FallenRobot import BOT_NAME
from FallenRobot import telethn as tbot
from FallenRobot.events import register
from FallenRobot.modules.sql.night_mode_sql import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    elif isinstance(chat, types.InputPeerChat):
        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    else:
        return None


hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)
openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)


@register(pattern="^/nightmode")
async def close_ws(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply("🤦🏻‍♂️ᴀɴᴅᴀ ʙᴜᴋᴀɴ ᴀᴅᴍɪɴ, ᴅᴀɴ ᴀɴᴅᴀ ᴛɪᴅᴀᴋ ʙɪsᴀ ᴍᴇɴɢɢᴜɴᴀᴋᴀɴ ᴘᴇʀɪɴᴛᴀʜ ɪɴɪ...")
            return

    if not event.is_group:
        await event.reply("ᴀɴᴅᴀ ʜᴀɴʏᴀ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴋᴛɪᴘᴋᴀɴ ᴍᴏᴅᴇ ᴍᴀʟᴀᴍ ᴅɪ ɢʀᴜᴘ.")
        return
    if is_nightmode_indb(str(event.chat_id)):
        await event.reply("ᴏʙʀᴏʟᴀɴ ɪɴɪ ᴛᴇʟᴀʜ ᴍᴇɴɢᴀᴋᴛɪᴘᴋᴀɴ ᴍᴏᴅᴇ ᴍᴀʟᴀᴍ.")
        return
    add_nightmode(str(event.chat_id))
    await event.reply(
        f"ᴍᴇɴᴀᴍʙᴀʜ ᴏʙʀᴏʟᴀɴ {event.chat.title} ᴅᴇɴɢᴀɴ ɪᴅ {event.chat_id} ᴋᴇ ᴅᴀᴛᴀʙᴀsᴇ. **ɢʀᴜᴘ ɪɴɪ ᴅɪ ᴛᴜᴛᴜᴘ ᴘᴀᴅᴀ ᴘᴜᴋᴜʟ 𝟷𝟸 ᴘᴀɢɪ ᴅᴀɴ ᴀᴋᴀɴ ᴅɪʙᴜᴋᴀ ᴘᴀᴅᴀ ᴘᴜᴋᴜʟ 𝟶𝟼 ᴘᴀɢɪ**"
    )


@register(pattern="^/rmnight")
async def disable_ws(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply("🤦🏻‍♂️ᴀɴᴅᴀ ʙᴜᴋᴀɴ ᴀᴅᴍɪɴ, ᴅᴀɴ ᴀɴᴅᴀ ᴛɪᴅᴀᴋ ʙɪsᴀ ᴍᴇɴɢɢᴜɴᴀᴋᴀɴ ᴘᴇʀɪɴᴛᴀʜ ɪɴɪ...")
            return

    if not event.is_group:
        await event.reply("ᴀɴᴅᴀ ʜᴀɴʏᴀ ᴅᴀᴘᴀᴛ ᴍᴇɴᴏɴᴀᴋᴛɪᴘᴋᴀɴ ᴍᴏᴅᴇ ᴍᴀʟᴀᴍ ᴅɪ ɢʀᴜᴘ.")
        return
    if not is_nightmode_indb(str(event.chat_id)):
        await event.reply("ᴏʙʀᴏʟᴀɴ ɪɴɪ ʙᴇʟᴜᴍ ᴍᴇɴɢᴀᴋᴛɪᴘᴋᴀɴ ᴍᴏᴅᴇ ᴍᴀʟᴀᴍ.")
        return
    rmnightmode(str(event.chat_id))
    await event.reply(
        f"ᴏʙʀᴏʟᴀɴ ᴅɪ ʜᴀᴘᴜs  {event.chat.title} ᴅᴇɴɢᴀɴ ɪᴅ {event.chat_id} ᴅᴀʀɪ ᴅᴀᴛᴀʙᴀsᴇ."
    )


async def job_close():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                f"**ᴍᴏᴅᴇ ᴍᴀʟᴀᴍ ᴅɪ ᴍᴜʟᴀɪ**\n\n`ɢʀᴏᴜᴘ ᴛᴜᴛᴜᴘ sᴀᴍᴘᴀɪ ᴊᴀᴍ 𝟼 ᴘᴀɢɪ, ʜᴀɴʏᴀ ᴀᴅᴍɪɴ ʏᴀɴɢ ᴅᴀᴘᴀᴛ ᴍᴇɴɢɪʀɪᴍ ᴘᴇsᴀɴ ᴅɪ ᴄʜᴀᴛ ɪɴɪ.`\n\n__ᴅɪᴅᴜᴋᴜɴɢ ᴏʟᴇʜ {BOT_NAME}__",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=hehes
                )
            )
        except Exception as e:
            logger.info(f"ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇɴᴜᴛᴜᴘ ɢʀᴏᴜᴘ {warner} - {e}")


# Run everyday at 12am
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler.start()


async def job_open():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                f"**ᴍᴏᴅᴇ ᴍᴀʟᴀᴍ ʙᴇʀᴀᴋʜɪʀ**\n\nɢʀᴏᴜᴘ ᴅɪ ʙᴜᴋᴀ ʟᴀɢɪ sᴇᴋᴀʀᴀɴɢ sᴇᴍᴜᴀ ᴏʀᴀɴɢ ᴅᴀᴘᴀᴛ ᴍᴇɴɢɪʀɪᴍ ᴘᴇsᴀɴ ᴅᴀʟᴀᴍ ᴏʙʀᴏʟᴀɴ ɪɴɪ.\n__ᴅɪᴅᴜᴋᴜɴɢ ᴏʟᴇʜ {BOT_NAME}__",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=openhehe
                )
            )
        except Exception as e:
            logger.info(f"ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇᴍʙᴜᴋᴀ ɢʀᴜᴘ {warner.chat_id} - {e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_open, trigger="cron", hour=6, minute=1)
scheduler.start()

__help__ = """
*Admins Only*

❍ /nightmode*:* ᴍᴇɴᴀᴍʙᴀʜᴋᴀɴ ɢʀᴏᴜᴘ ᴋᴇ ɴɪɢʜᴛᴍᴏᴅᴇ ᴄʜᴀᴛ
 ❍ /rmnight*:* ᴍᴇɴɢʜᴀᴘᴜs ɢʀᴏᴜᴘ ᴅᴀʀɪ ɴɪɢʜᴛᴍᴏᴅᴇ ᴄʜᴀᴛ

*Note:* ᴏʙʀᴏʟᴀɴ ᴍᴏᴅᴇ ᴍᴀʟᴀᴍ ᴀᴋᴀɴ ᴅɪ ᴛᴜᴛᴜᴘ sᴇᴄᴀʀᴀ ᴏᴛᴏᴍᴀᴛɪs ᴘᴀᴅᴀ ᴘᴜᴋᴜʟ 𝟷𝟸 ᴍᴀʟᴀᴍ ᴅᴀɴ ᴅɪ ʙᴜᴋᴀ sᴇᴄᴀʀᴀ ᴏᴛᴏᴍᴀᴛɪs ᴘᴀᴅᴀ ᴘᴜᴋᴜʟ 𝟼 ᴘᴀɢɪ ᴜɴᴛᴜᴋ ᴍᴇɴᴄᴇɢᴀʜ sᴘᴀᴍ ᴅɪ ᴍᴀʟᴀᴍ ʜᴀʀɪ.
"""

__mod_name__ = "ɴɪɢʜᴛ"
