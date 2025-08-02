import os
import aiofiles
import urllib.parse
import aiohttp
import logging

from WebStreamer.bot import StreamBot
from WebStreamer.vars import Var
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash

BASE_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../../template')

async def render_page(message_id, secure_hash):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message ID {message_id}")
        raise InvalidHash

    src = urllib.parse.urljoin(Var.URL, f"{secure_hash}{message_id}")
    media_type = file_data.mime_type.split('/')[0].strip()

    if media_type in ['video', 'audio']:
        template_file = 'req.html'
    else:
        template_file = 'dl.html'

    template_path = os.path.join(BASE_TEMPLATE_DIR, template_file)
    async with aiofiles.open(template_path, mode='r') as f:
        template = await f.read()

    heading = ''
    file_size = ''
    if media_type in ['video', 'audio']:
        heading = f"{'Watch' if media_type == 'video' else 'Listen'} {file_data.file_name}"
        html = template.replace('tag', media_type) % (heading, heading, src)
    else:
        heading = f"Download {file_data.file_name}"
        async with aiohttp.ClientSession() as session:
            async with session.head(src) as resp:
                size_bytes = int(resp.headers.get('Content-Length', 0))
                file_size = humanbytes(size_bytes)
        html = template % (heading, heading, file_data.file_name, file_size, src)

    return html
