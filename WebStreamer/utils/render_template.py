import urllib.parse
import aiofiles
import logging
from WebStreamer.vars import Var
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash

async def render_page(message_id, secure_hash):
    """
    Render the HTML page for the download with a 10-second countdown.
    """
    # Get file metadata from Telegram
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))

    # Validate the hash
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"Link hash: {secure_hash} - Expected: {file_data.unique_id[:6]}")
        raise InvalidHash

    # Build the download URL
    download_url = urllib.parse.urljoin(Var.URL, f"dl/{secure_hash}{str(message_id)}")

    # Path to the HTML template
    template_path = "WebStreamer/template/req.html"

    # Read template
    async with aiofiles.open(template_path, mode='r') as f:
        html = await f.read()

    # Replace placeholders with actual values
    html = html.replace("{{ file_name }}", file_data.file_name)
    html = html.replace("{{ download_url }}", download_url)

    return html
