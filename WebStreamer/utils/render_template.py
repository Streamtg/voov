import urllib.parse
import aiofiles
import logging
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

    # Streaming and download URLs
    stream_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{str(message_id)}")
    download_url = stream_url

    # Load the HTML template
    template_path = "WebStreamer/template/req.html"
    async with aiofiles.open(template_path, mode='r') as f:
        html_content = await f.read()

    heading = "Watch " + file_data.file_name if file_data.mime_type.startswith("video") else "Listen " + file_data.file_name

    # Use string.Template to avoid KeyError with CSS
    template = Template(html_content)
    html = template.safe_substitute(
        heading=heading,
        file_name=file_data.file_name,
        file_size=humanbytes(file_data.file_size),
        stream_url=stream_url,
        download_url=download_url,
        mime_type=file_data.mime_type
    )

    return html
