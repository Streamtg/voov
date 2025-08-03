import urllib.parse
import aiofiles
import logging
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash

async def render_page(message_id, secure_hash):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash: {secure_hash} expected {file_data.unique_id[:6]}")
        raise InvalidHash

    stream_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{str(message_id)}")
    download_url = stream_url
    mime_type = file_data.mime_type or "application/octet-stream"

    if file_data.mime_type.split('/')[0].strip() in ['video', 'audio']:
        template_path = "WebStreamer/template/req.html"
        async with aiofiles.open(template_path, mode='r') as f:
            html = await f.read()

        heading = (
            "Watch " + file_data.file_name
            if mime_type.startswith("video")
            else "Listen " + file_data.file_name
        )

        html = html.format(
            heading=heading,
            filename=file_data.file_name,
            src=stream_url,
            download_url=download_url,
            mime_type=mime_type
        )
    else:
        # Aquí puedes incluir la plantilla de descarga, si lo necesitas
        template_path = "WebStreamer/template/dl.html"
        async with aiofiles.open(template_path, mode='r') as f:
            html = await f.read()
        html = html.format(
            heading="Download " + file_data.file_name,
            filename=file_data.file_name,
            download_url=download_url
        )

    return html
