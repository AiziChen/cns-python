import asyncio
import socket
import logging
from tools import *
import uvloop
import udp
import tcp


async def handle_client_streams(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    sock: socket.socket = writer.get_extra_info('socket')
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    logging.info(f'Received a new connection {sock.getpeername}')
    respData = await reader.read(4096)
    print('resp: ', respData)
    if respData:
        if is_http_header(respData):
            writer.write(response_header(respData))
            if respData.find(b'httpUDP') == -1:
                await tcp.handle_tcp_connection(reader, writer, respData)
            else:
                await handle_client_streams(reader, writer)
        else:
            await udp.handle_udp_connection(reader, writer)
    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s]%(levelname)s - %(message)s')
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    # loop.set_debug(False)
    coro = asyncio.start_server(handle_client_streams, '0.0.0.0', 1080)
    loop.run_until_complete(coro)
    try:
        loop.run_forever()
    finally:
        loop.close()
