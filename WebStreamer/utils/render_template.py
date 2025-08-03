import urllib.parse
import aiofiles
import logging
import aiohttp
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash

async def render_page(message_id, secure_hash):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {message_id}")
        raise InvalidHash

    stream_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{str(message_id)}")
    download_url = stream_url

    # Decide el media tag según MIME type
    media_tag = ""
    main_type = file_data.mime_type.split('/')[0].strip() if file_data.mime_type else ""

    if main_type == "video":
        media_tag = f'<video src="{stream_url}" type="{file_data.mime_type}" controls></video>'
        heading = f"Watch {file_data.file_name}"
    elif main_type == "audio":
        media_tag = f'<audio src="{stream_url}" type="{file_data.mime_type}" controls></audio>'
        heading = f"Listen {file_data.file_name}"
    else:
        # Para otros archivos mostramos un mensaje o link directo
        async with aiohttp.ClientSession() as session:
            async with session.get(stream_url) as resp:
                file_size = humanbytes(int(resp.headers.get('Content-Length', 0)))
        heading = f"Download {file_data.file_name}"
        media_tag = f'<p>Archivo no reproducible en navegador.</p><p>Tamaño: {file_size}</p>'

    # Lee plantilla
    template_path = "WebStreamer/template/req.html"
    async with aiofiles.open(template_path, mode='r') as f:
        html = await f.read()

    # Formatea HTML con variables
    html = html.format(
        heading=heading,
        download_url=download_url,
        media_tag=media_tag
    )

    return html
