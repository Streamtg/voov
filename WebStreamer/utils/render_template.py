import aiohttp
import jinja2
import urllib.parse
from FileStream.config import Telegram, Server
from FileStream.utils.database import Database
from FileStream.utils.human_readable import humanbytes

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

async def render_page(db_id):
    file_data = await db.get_file(db_id)
    src = urllib.parse.urljoin(Server.URL, f'dl/{file_data["_id"]}')
    file_size = humanbytes(file_data['file_size'])
    file_name = file_data['file_name'].replace("_", " ")
    mime_type = file_data.get('mime_type', 'application/octet-stream')

    if str(mime_type).split('/')[0].strip() != 'video':
        # Para archivos que no son video, obtener tamaño real del recurso remoto
        async with aiohttp.ClientSession() as session:
            async with session.head(src) as resp:
                if resp.status == 200:
                    content_length = resp.headers.get('Content-Length')
                    if content_length:
                        file_size = humanbytes(int(content_length))

    template_file = "FileStream/template/play.html" if mime_type.startswith('video/') else "FileStream/template/dl.html"

    with open(template_file) as f:
        template = jinja2.Template(f.read())

    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        mime_type=mime_type,
        file_id=file_data['_id']
    )
