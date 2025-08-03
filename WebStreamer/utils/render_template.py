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

    # Valida hash de seguridad
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {message_id}")
        raise InvalidHash

    # URL para streaming directo y descarga
    stream_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{str(message_id)}")
    download_url = stream_url  # misma ruta para descargar

    # Obtener tamaño del archivo para mostrar en la plantilla
    async with aiohttp.ClientSession() as session:
        async with session.get(stream_url) as resp:
            file_size = humanbytes(int(resp.headers.get('Content-Length', 0)))

    # Plantilla para video/audio
    if file_data.mime_type.startswith("video") or file_data.mime_type.startswith("audio"):
        template_path = "WebStreamer/template/req.html"
        async with aiofiles.open(template_path, mode="r") as f:
            html = await f.read()

        html = html.format(
            filename=file_data.file_name,
            src=stream_url,
            mime_type=file_data.mime_type,
            size=file_size,
            download_url=download_url
        )
        return html

    # Plantilla para otros archivos (descarga directa)
    else:
        template_path = "WebStreamer/template/dl.html"
        async with aiofiles.open(template_path, mode="r") as f:
            html = await f.read()

        html = html.format(
            filename=file_data.file_name,
            src=stream_url,
            size=file_size,
            download_url=download_url
        )
        return html
