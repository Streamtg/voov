import re
import time
import logging
import traceback
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from WebStreamer.bot import multi_clients, work_loads, StreamBot
from WebStreamer.vars import Var
from WebStreamer.server.exceptions import InvalidHash, FIleNotFound
from WebStreamer import utils, StartTime, __version__
from WebStreamer.utils.render_template import render_page

routes = web.RouteTableDef()

@routes.get("/status", allow_head=True)
async def status_handler(_):
    return web.json_response({
        "server_status": "running",
        "uptime": utils.get_readable_time(time.time() - StartTime),
        "telegram_bot": "@" + StreamBot.username,
        "connected_bots": len(multi_clients),
        "loads": dict(
            ("bot" + str(c + 1), l)
            for c, (_, l) in enumerate(
                sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
            )
        ),
        "version": __version__,
    })

@routes.get("/watch/{path}", allow_head=True)
async def watch_handler(request: web.Request):
    """
    Muestra la página HTML con reproductor y botón de descarga con contador.
    """
    try:
        path = request.match_info["path"]
        # Extraer hash y message_id del path
        match = re.match(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            message_id = int(match.group(2))
        else:
            # Por si solo viene ID sin hash (usar query param)
            message_id = int(re.search(r"(\d+)", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        html_content = await render_page(message_id, secure_hash)

        return web.Response(
            text=html_content,
            content_type="text/html",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Range, Content-Type, Accept",
            }
        )

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        # Request interrumpido por cliente, ignorar
        pass
    except Exception as e:
        traceback.print_exc()
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))
