import urllib.parse
import aiofiles
import logging
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.server.exceptions import InvalidHash

async def render_page(message_id, secure_hash):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    if file_data.unique_id[:6] != secure_hash:
        raise InvalidHash

    # Correct stream URL
    stream_url = f"{Var.URL}dl/{secure_hash}{message_id}"
    download_url = stream_url

    template_path = "WebStreamer/template/req.html"
    async with aiofiles.open(template_path, mode='r') as f:
        html = await f.read()

    html = html.replace("{{ file_name }}", file_data.file_name)
    html = html.replace("{{ file_id }}", f"{secure_hash}{message_id}")
    html = html.replace("{{ mime_type }}", file_data.mime_type or "application/octet-stream")
    html = html.replace("{{ file_size }}", humanbytes(file_data.file_size))
    html = html.replace("{{ stream_url }}", stream_url)
    html = html.replace("{{ download_url }}", download_url)

    return html
