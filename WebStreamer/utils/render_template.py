# This file is a part of TG-FileStreamBot

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

# Ruta a la carpeta raíz de plantillas
BASE_TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../template'))

async def render_page(message_id, secure_hash):
    # Obtiene datos del archivo desde Telegram
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f'link hash: {secure_hash} - {file_data.unique_id[:6]}')
        logging.debug(f"Invalid hash for message with - ID {message_id}")
        raise InvalidHash

    # URL pública que servirá el bot
    src = urllib.parse.urljoin(Var.URL, f'{secure_hash}{str(message_id)}')
    media_type = str(file_data.mime_type.split('/')[0].strip())

    # VIDEO
    if media_type == 'video':
        template_path = os.path.join(BASE_TEMPLATE_DIR, 'req.html')
        async with aiofiles.open(template_path) as r:
            heading = f'Watch {file_data.file_name}'
            tag = media_type
            html = (await r.read()).replace('tag', tag) % (heading, file_data.file_name, src)

    # AUDIO
    elif media_type == 'audio':
        template_path = os.path.join(BASE_TEMPLATE_DIR, 'req.html')
        async with aiofiles.open(template_path) as r:
            heading = f'Listen {file_data.file_name}'
            tag = media_type
            html = (await r.read()).replace('tag', tag) % (heading, file_data.file_name, src)

    # DESCARGA
    else:
        template_path = os.path.join(BASE_TEMPLATE_DIR, 'dl.html')
        async with aiofiles.open(template_path) as r:
            async with aiohttp.ClientSession() as s:
                async with s.get(src) as u:
                    heading = f'Download {file_data.file_name}'
                    file_size = humanbytes(int(u.headers.get('Content-Length')))
                    html = (await r.read()) % (heading, file_data.file_name, src, file_size)

    return html
