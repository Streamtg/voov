from aiohttp import web
from WebStreamer.utils.render_template import render_page
from WebStreamer.server.exceptions import InvalidHash, FIleNotFound
import re
import logging
import math
import mimetypes
import secrets
from WebStreamer.bot import multi_clients, work_loads
from WebStreamer.utils import ByteStreamer
from WebStreamer.vars import Var

routes = web.RouteTableDef()

@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            message_id = int(match.group(2))
        else:
            message_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        html = await render_page(message_id, secure_hash)
        return web.Response(text=html, content_type='text/html')

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))


class_cache = {}

@routes.get(r"/{path:\S+}", allow_head=True)
async def media_stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            message_id = int(match.group(2))
        else:
            message_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        range_header = request.headers.get("Range", None)
        index = min(work_loads, key=work_loads.get)
        faster_client = multi_clients[index]

        if Var.MULTI_CLIENT:
            logging.info(f"Client {index} is now serving {request.remote}")

        if faster_client in class_cache:
            tg_connect = class_cache[faster_client]
            logging.debug(f"Using cached ByteStreamer object for client {index}")
        else:
            logging.debug(f"Creating new ByteStreamer object for client {index}")
            tg_connect = ByteStreamer.ByteStreamer(faster_client)
            class_cache[faster_client] = tg_connect

        file_id = await tg_connect.get_file_properties(message_id)

        if file_id.unique_id[:6] != secure_hash:
            logging.debug(f"Invalid hash for message with ID {message_id}")
            raise InvalidHash

        file_size = file_id.file_size

        if range_header:
            from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
            from_bytes = int(from_bytes)
            until_bytes = int(until_bytes) if until_bytes else file_size - 1
        else:
            from_bytes = 0
            until_bytes = file_size - 1

        req_length = until_bytes - from_bytes + 1
        chunk_size = await ByteStreamer.chunk_size(req_length)
        offset = await ByteStreamer.offset_fix(from_bytes, chunk_size)
        first_part_cut = from_bytes - offset
        last_part_cut = (until_bytes % chunk_size) + 1
        part_count = math.ceil(req_length / chunk_size)

        body = tg_connect.yield_file(
            file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
        )

        mime_type = file_id.mime_type or mimetypes.guess_type(file_id.file_name)[0] or "application/octet-stream"
        file_name = file_id.file_name or f"{secrets.token_hex(2)}.unknown"
        disposition = "attachment"
        if mime_type.startswith("video") or mime_type.startswith("audio"):
            disposition = "inline"

        headers = {
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
        }

        status = 206 if range_header else 200

        response = web.Response(
            status=status,
            body=body,
            headers=headers,
        )

        if not range_header:
            response.headers.add("Content-Length", str(file_size))

        return response

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))
