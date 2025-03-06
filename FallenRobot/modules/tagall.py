import asyncio

from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from FallenRobot import telethn as client

spam_chats = []


@client.on(events.NewMessage(pattern="^/all ?(.*)"))
@client.on(events.NewMessage(pattern="^@all ?(.*)"))
async def mentionall(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond(
            "ᴍᴏᴅᴜʟᴇ ɪɴɪ ᴄᴜᴍᴀɴ ʙɪꜱᴀ ᴅɪ ᴘᴀᴋᴇ ᴅɪ ɢᴄ ᴀᴛᴀᴜ ᴅɪ ᴄʜ ᴍᴇᴋ!"
        )

    is_admin = False
    try:
        partici_ = await client(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("ʜᴀɴʏᴀ ᴀᴅᴍɪɴ ʏᴀɴɢ ʙɪsᴀ ᴘʀᴏsᴇs ᴛᴀɢ ᴀʟʟ!")

    if event.pattern_match.group(1) and event.is_reply:
        return await event.respond("ʙᴇʀɪᴋᴀɴ ᴍɪɴɪᴍᴀʟ 𝟷 ᴋᴀᴛᴀ ᴜɴᴛᴜᴋ ᴘʀᴏsᴇs ᴛᴀɢᴀʟʟ")
    elif event.pattern_match.group(1):
        mode = "text_on_cmd"
        msg = event.pattern_match.group(1)
    elif event.is_reply:
        mode = "text_on_reply"
        msg = await event.get_reply_message()
        if msg == None:
            return await event.respond(
                "sᴀʏᴀ ᴛɪᴅᴀᴋ ʙɪsᴀ ᴘʀᴏsᴇs ᴛᴀɢ ᴀʟʟ ᴜɴᴛᴜᴋ ᴘᴇsᴀɴ ʟᴀᴍᴀ! (ᴘᴇsᴀɴ ʏᴀɴɢ ᴅɪ ᴋɪʀɪᴍ sᴇʙᴇʟᴜᴍ sᴀʏᴀ ᴍᴀsᴜᴋ ᴋᴇ ɢʀᴏᴜᴘ"
            )
    else:
        return await event.respond(
            "ʀᴇᴘʟʏ ᴘᴇꜱᴀɴ ᴍᴀɴᴀ ʏᴀɴɢ ᴍᴀᴜ ᴅɪ ᴛᴀɢᴀʟʟ ᴍᴇᴋ!"
        )

    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ""
    async for usr in client.iter_participants(chat_id):
        if not chat_id in spam_chats:
            break
        usrnum += 1
        usrtxt += f"❍ [{usr.first_name}](tg://user?id={usr.id})\n"
        if usrnum == 5:
            if mode == "text_on_cmd":
                txt = f"{msg}\n\n{usrtxt}"
                await client.send_message(chat_id, txt)
            elif mode == "text_on_reply":
                await msg.reply(usrtxt)
            await asyncio.sleep(3)
            usrnum = 0
            usrtxt = ""
    try:
        spam_chats.remove(chat_id)
    except:
        pass


@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
    if not event.chat_id in spam_chats:
        return await event.respond("ɢᴀ ᴀᴅᴀ ʏᴀɴɢ ʜᴀʀᴜs ɢᴡ ʙᴇʀʜᴇɴᴛɪɪɴ ᴛᴏᴅ...__")
    is_admin = False
    try:
        partici_ = await client(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("ʜᴀɴʏᴀ ᴀᴅᴍɪɴ ʏᴀɴɢ ᴅᴀᴘᴀᴛ ᴍᴇɴᴊᴀʟᴀɴᴋᴀɴ ᴘʀɪɴᴛᴀʜ ɪɴɪ")

    else:
        try:
            spam_chats.remove(event.chat_id)
        except:
            pass
        return await event.respond("ᴛᴀɢ ᴀʟʟ ᴍᴇɴᴛɪᴏɴ ʙᴇʀʜᴇɴᴛɪ")


__mod_name__ = "ᴛᴀɢ ᴀʟʟ"
__help__ = """
*ʜᴀɴʏᴀ ᴜɴᴛᴜᴋ ᴀᴅᴍɪɴ*

❍ /all '(ʀᴇᴘʟʏ ᴘᴇsᴀɴ ʏᴀɴɢ ᴍᴀᴜ ᴅɪ ᴛᴀɢ ᴀʟ) ᴜɴᴛᴜᴋ ᴘʀᴏsᴇs ᴍᴇ ᴛᴀɢ ᴀʟʟ ᴍᴇᴍʙᴇʀ ɢʀᴏᴜᴘ.'
"""
