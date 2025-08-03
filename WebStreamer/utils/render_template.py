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
    """
    Renderiza la plantilla HTML con reproductor o descarga según tipo de archivo.
    """

    # Obtiene metadatos desde Telegram
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    # Verifica hash seguro
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message ID {message_id}")
        raise InvalidHash

    # URL directa para streaming/descarga
    download_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{message_id}")

    # Si es video o audio → usa req.html con reproductor
    if file_data.mime_type.startswith(("video", "audio")):
        template_path = "WebStreamer/template/req.html"

        async with aiofiles.open(template_path, mode='r', encoding='utf-8') as f:
            html = await f.read()

        heading = (
            'Watch ' + file_data.file_name
            if file_data.mime_type.startswith("video")
            else 'Listen ' + file_data.file_name
        )

        # Reemplaza variables en la plantilla
        html = html.format(
            heading=heading,
            filename=file_data.file_name,
            download_url=download_url
        )

    else:
        # Para otros tipos de archivo → plantilla de descarga simple
        template_path = "WebStreamer/template/dl.html"

        async with aiofiles.open(template_path, mode='r', encoding='utf-8') as f:
            html = await f.read()

        # Obtiene tamaño del archivo
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as resp:
                file_size = humanbytes(int(resp.headers.get('Content-Length', 0)))

        heading = 'Download ' + file_data.file_name

        html = html.format(
            heading=heading,
            filename=file_data.file_name,
            size=file_size,
            download_url=download_url
        )

    return html
