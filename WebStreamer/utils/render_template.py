# WebStreamer/utils/render_template.py

import os
import urllib.parse
import aiofiles
import logging
import aiohttp
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash

# Ruta absoluta a la carpeta de plantillas
BASE_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../template')

async def render_page(message_id, secure_hash):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    # Verifica hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {message_id}")
        raise InvalidHash

    # URL para reproducir el streaming
    stream_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{message_id}")

    media_type = file_data.mime_type.split('/')[0].strip()

    if media_type in ['video', 'audio']:
        # Plantilla para video/audio
        template_path = os.path.join(BASE_TEMPLATE_DIR, 'req.html')
        async with aiofiles.open(template_path, mode='r') as f:
            template = await f.read()
        heading = f"{'Watch' if media_type == 'video' else 'Listen'} {file_data.file_name}"
        tag = media_type
        # Inserta botón de descarga apuntando a /dl/
        html = template.replace('tag', tag) % (
            heading,
            heading,
            stream_url  # Fuente para el reproductor
        )
        # Agregamos botón al final
        html += f"""
        <div style="text-align:center;margin-top:20px;">
            <a href="{stream_url}" download>
                <button style="padding:10px 20px;font-size:16px;cursor:pointer;">
                    Descargar archivo
                </button>
            </a>
        </div>
        """
    else:
        # Plantilla para descarga directa
        template_path = os.path.join(BASE_TEMPLATE_DIR, 'dl.html')
        async with aiofiles.open(template_path, mode='r') as f:
            template = await f.read()

        # Obtener tamaño del archivo
        async with aiohttp.ClientSession() as session:
            async with session.head(stream_url) as resp:
                size_bytes = int(resp.headers.get('Content-Length', 0))
                file_size = humanbytes(size_bytes)

        heading = f"Download {file_data.file_name}"
        html = template % (
            heading,
            file_data.file_name,
            stream_url,
            file_size
        )

    return html
