import asyncio
import socket
import logging
from tools import *
import udp
import tcp


async def handle_client(client: socket):
    loop = asyncio.get_event_loop()
    respData = await loop.sock_recv(client, 65536)
    if respData != b'':
        if is_http_header(respData):
            await loop.sock_sendall(client, response_header(respData))
            if respData.find(b'httpUDP') == -1:
                await tcp.handle_tcp_connection(client, respData)
            else:
                await handle_client(client)
        else:
            await udp.handle_udp_connection(client)
    client.close()


async def run_server():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s]%(levelname)s - %(message)s')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 1080))
    server.listen(256)
    server.setblocking(False)
    loop = asyncio.get_event_loop()
    while True:
        client, addr = await loop.sock_accept(server)
        logging.info(f"Accept new connection {addr}")
        loop.create_task(handle_client(client))

asyncio.run(run_server())
