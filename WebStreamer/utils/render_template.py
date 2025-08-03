import urllib.parse
import aiofiles
import logging
import aiohttp
from string import Template
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash

async def render_page(message_id, secure_hash):
    # Get file metadata from Telegram
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    # Validate hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {message_id}")
        raise InvalidHash

    # Streaming and download URL
    stream_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{str(message_id)}")
    download_url = stream_url  # same for download

    # Detect if it's video/audio
    if str(file_data.mime_type.split('/')[0].strip()) in ['video', 'audio']:
        template_path = "WebStreamer/template/req.html"

        async with aiofiles.open(template_path, mode='r') as f:
            html_content = await f.read()

        heading = 'Watch ' + file_data.file_name if file_data.mime_type.startswith('video') else 'Listen ' + file_data.file_name

        # Use Template instead of str.format()
        template = Template(html_content)
        html = template.safe_substitute(
            heading=heading,
            file_name=file_data.file_name,
            file_size=humanbytes(file_data.file_size),
            src=stream_url,
            mime_type=file_data.mime_type,
            download_url=download_url
        )

    else:
        # Fallback for files that are not video/audio
        template_path = "WebStreamer/template/dl.html"
        async with aiofiles.open(template_path, mode='r') as f:
            html_content = await f.read()

        async with aiohttp.ClientSession() as session:
            async with session.get(stream_url) as resp:
                file_size = humanbytes(int(resp.headers.get('Content-Length', 0)))

        heading = 'Download ' + file_data.file_name
        template = Template(html_content)
        html = template.safe_substitute(
            heading=heading,
            file_name=file_data.file_name,
            file_size=file_size,
            src=stream_url,
            mime_type=file_data.mime_type or "application/octet-stream",
            download_url=download_url
        )

    return html
