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
    # Obtiene metadatos del archivo en Telegram
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    # Valida el hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {message_id}")
        raise InvalidHash

    # URL para streaming y descarga
    stream_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{str(message_id)}")
    download_url = stream_url  # Mismo enlace para descarga

    # Detecta tipo MIME
    file_type = str(file_data.mime_type.split('/')[0].strip())
    file_size_str = ""

    # Obtiene tamaño real si es necesario
    async with aiohttp.ClientSession() as session:
        async with session.get(stream_url) as resp:
            file_size_str = humanbytes(int(resp.headers.get('Content-Length', 0)))

    # Carga la plantilla
    template_path = "WebStreamer/template/req.html"
    async with aiofiles.open(template_path, mode='r') as f:
        html = await f.read()

    # Reemplaza variables manualmente (sin .format para evitar errores de CSS)
    html = (
        html.replace("{{ file_name }}", file_data.file_name)
            .replace("{{ file_size }}", file_size_str)
            .replace("{{ file_id }}", f"{secure_hash}{message_id}")
            .replace("{{ mime_type }}", file_data.mime_type)
            .replace("{{ download_url }}", download_url)
    )

    return html
