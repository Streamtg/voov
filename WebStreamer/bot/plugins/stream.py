import asyncio
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import gen_link
from WebStreamer.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums.parse_mode import ParseMode

@StreamBot.on_message(
    filters.private
    & (
        filters.document
        | filters.video
        | filters.audio
        | filters.animation
        | filters.voice
        | filters.video_note
        | filters.photo
        | filters.sticker
    ),
    group=4,
)
async def private_receive_handler(c: Client, m: Message):
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        reply_markup, Stream_Text, stream_link = await gen_link(m=m, log_msg=log_msg, from_channel=False)

        # Cambia el texto para eliminar el link de descarga
        text_to_send = (
            f"**Requested by:** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n"
            f"**User ID:** `{m.from_user.id}`\n"
            f"🎬 Streaming link: {stream_link}"
        )
        await log_msg.reply_text(text=text_to_send, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)

        # También en la respuesta al usuario, eliminamos el botón o texto de descarga
        await m.reply_text(
            text=Stream_Text,  # Asegúrate que Stream_Text no contenga links de descarga, o actualiza gen_link para eso
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,  # Aquí podrías modificar gen_link para que el botón solo contenga streaming
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.value)}s")
        await asyncio.sleep(e.value)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=(
                f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.value)}s from "
                f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n"
                f"**User ID:** `{str(m.from_user.id)}`"
            ),
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN
        )

@StreamBot.on_message(filters.channel & (filters.document | filters.video), group=-1)
async def channel_receive_handler(bot, broadcast: Message):
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        reply_markup, Stream_Text, stream_link = await gen_link(m=broadcast, log_msg=log_msg, from_channel=True)

        # Solo enviamos streaming link, sin descarga
        await log_msg.reply_text(
            text=(
                f"**Channel Name:** `{broadcast.chat.title}`\n"
                f"**Channel ID:** `{broadcast.chat.id}`\n"
                f"🎬 Streaming URL: {stream_link}"
            ),
            quote=True,
            parse_mode=ParseMode.MARKDOWN
        )

        # Cambiamos el botón para que solo contenga el enlace de streaming
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎬 Watch / Stream", url=stream_link)]]
            )
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.value)}s")
        await asyncio.sleep(w.value)
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=(
                f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(w.value)}s from {broadcast.chat.title}\n\n"
                f"**Channel ID:** `{str(broadcast.chat.id)}`"
            ),
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"**#error_traceback:** `{e}`",
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN
        )
        print(f"Can't Edit Broadcast Message!\nError: {e}")

# Nota: Si usas gen_link, modifica ahí también para que no incluya el link de descarga en los textos ni botones.
