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
    # Obtiene metadatos del archivo desde Telegram
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    # Verifica que el hash sea válido
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash para mensaje con ID {message_id}")
        raise InvalidHash

    # Construye URL para streaming/descarga
    download_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{message_id}")

    # Detecta el tipo MIME y el tamaño
    mime_type = file_data.mime_type or "application/octet-stream"
    async with aiohttp.ClientSession() as session:
        async with session.head(download_url) as resp:
            size_bytes = int(resp.headers.get('Content-Length', 0))
            size_human = humanbytes(size_bytes)

    # Ruta a la plantilla HTML
    template_path = "WebStreamer/template/req.html"

    async with aiofiles.open(template_path, mode='r') as f:
        html = await f.read()

    # Rellena la plantilla
    html = html.format(
        filename=file_data.file_name,
        mime_type=mime_type,
        size=size_human,
        download_url=download_url
    )

    return html
