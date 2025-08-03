import urllib.parse
import aiofiles
import logging
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash

async def render_page(message_id, secure_hash):
    # Obtiene metadatos del archivo
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    # Valida el hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {message_id}")
        raise InvalidHash

    # URL de descarga directa
    download_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{str(message_id)}")

    # Obtener tamaño en formato legible
    async with aiofiles.open('dummy', mode='r'):  # Evita error si no usas esta linea, o ignórala si no tienes otro método
        pass

    # Para obtener tamaño, hacemos una petición HEAD
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.head(download_url) as resp:
            content_length = resp.headers.get('Content-Length')
            file_size = humanbytes(int(content_length)) if content_length else "Unknown size"

    # Lee la plantilla req.html
    template_path = "WebStreamer/template/req.html"
    async with aiofiles.open(template_path, mode='r') as f:
        html = await f.read()

    # Reemplaza variables en la plantilla
    html = html.replace("{{ file_name }}", file_data.file_name)
    html = html.replace("{{ file_size }}", file_size)
    html = html.replace("{{ download_url }}", download_url)

    return html
