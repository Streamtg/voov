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
    download_url = stream_url  # mismo enlace para descargar

    # Usamos solo la plantilla req.html con el botón con delay
    template_path = "WebStreamer/template/req.html"
    async with aiofiles.open(template_path, mode='r') as f:
        html = await f.read()

    # Calculamos tamaño archivo para mostrar info (opcional)
    async with aiohttp.ClientSession() as session:
        async with session.head(stream_url) as resp:
            file_size = humanbytes(int(resp.headers.get('Content-Length', 0)))

    # Valores para insertar en la plantilla
    heading = 'Watch ' + file_data.file_name if file_data.mime_type.startswith('video') else 'Listen ' + file_data.file_name
    mime_type = file_data.mime_type
    file_name = file_data.file_name

    # Renderizamos plantilla con format()
    html = html.format(
        heading=heading,
        file_name=file_name,
        file_size=file_size,
        src=stream_url,
        download_url=download_url,
        mime_type=mime_type
    )

    return html
