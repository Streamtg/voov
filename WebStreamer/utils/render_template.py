import os
import urllib.parse
import aiofiles
import logging
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash


async def render_page(message_id, secure_hash):
    """
    Renderiza la plantilla req.html con los datos del archivo a reproducir.
    """

    # Obtiene info del archivo desde Telegram
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    # Valida hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f'link hash: {secure_hash} - {file_data.unique_id[:6]}')
        logging.debug(f"Invalid hash for message ID {message_id}")
        raise InvalidHash

    # URL para streaming/descarga
    src = urllib.parse.urljoin(Var.URL, f"{secure_hash}{str(message_id)}")
    
    # Determina tipo de etiqueta HTML
    mime_type_root = str(file_data.mime_type.split('/')[0]).strip()
    if mime_type_root == 'video':
        tag = 'video'
        heading = f"Ver {file_data.file_name}"
    elif mime_type_root == 'audio':
        tag = 'audio'
        heading = f"Escuchar {file_data.file_name}"
    else:
        # Si no es video/audio, usa descarga directa
        tag = 'video'
        heading = f"Descargar {file_data.file_name}"

    # Ruta absoluta al template
    template_path = os.path.join(os.path.dirname(__file__), "..", "template", "req.html")
    template_path = os.path.abspath(template_path)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template HTML no encontrado en {template_path}")

    # Lee y renderiza la plantilla
    async with aiofiles.open(template_path, mode='r') as f:
        html_template = await f.read()

    html = html_template.format(
        heading=heading,
        filename=file_data.file_name,
        src=src,
        tag=tag,
        download_url=src
    )

    return html
