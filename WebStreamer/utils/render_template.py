import urllib.parse
import aiofiles
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.server.exceptions import InvalidHash
from WebStreamer.vars import Var
from WebStreamer.utils.human_readable import humanbytes


async def render_page(message_id: int, secure_hash: str) -> str:
    # Obtener metadatos del archivo por message_id y canal BIN_CHANNEL
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(message_id))
    
    # Validar hash para evitar acceso no autorizado
    if file_data.unique_id[:6] != secure_hash:
        raise InvalidHash
    
    # URL de streaming o descarga
    src = urllib.parse.urljoin(Var.URL, f"{secure_hash}{message_id}")
    
    # Tipo de media (video, audio o otro)
    media_type = file_data.mime_type.split('/')[0].strip() if file_data.mime_type else "unknown"
    file_size_str = humanbytes(file_data.file_size)
    file_name = file_data.file_name
    
    # Leer plantilla HTML tipo Netflix
    async with aiofiles.open('/home/idies/voov/WebStreamer/template/req.html', mode='r') as f:
        template = await f.read()
    
    heading = ''
    player_tag = ''
    file_info = f"{file_name} - Tamaño: {file_size_str}"
    download_button = ''
    
    if media_type in ['video', 'audio']:
        heading = f"{'Ver' if media_type == 'video' else 'Escuchar'} {file_name}"
        player_tag = f'''
        <{media_type} id="player" playsinline controls crossorigin>
            <source src="{src}" type="{file_data.mime_type}">
            Tu navegador no soporta la reproducción de este archivo.
        </{media_type}>
        '''
    else:
        heading = f"Descargar {file_name}"
        file_info = f"{file_name} - Tipo: {file_data.mime_type or 'Desconocido'} - Tamaño: {file_size_str}"
        player_tag = ''
        download_button = f'<a class="download-btn" href="{src}" download="{file_name}">Descargar archivo</a>'
    
    # Renderizar plantilla con datos dinámicos
    html = template.format(
        heading=heading,
        player_tag=player_tag,
        file_info=file_info,
        download_button=download_button
    )
    return html
