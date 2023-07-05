import asyncio
import socket
import logging
from tools import *


async def tcp_forward(client: socket, server: socket):
    loop = asyncio.get_event_loop()
    sub = 0
    data = await loop.sock_recv(client, 1024)
    while data != b'':
        sub = xor_cipher(data, sub)
        await loop.sock_sendall(server, data)
    client.close()
    server.close()


async def handle_tcp_connection(client: socket, data: bytes):
    loop = asyncio.get_event_loop()
    host = get_proxy_host(data)
    if host == None:
        await loop.sock_sendall(client, b'No proxy host')
    else:
        host = decrypt_host(host)
        logging.info(f'proxy host: {host}')
        if not host.endswith(':53'):
            if host.find(':') == -1:
                host += ':80'
            hostport = host.split(':')
            sClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sClient.connect((hostport[0], hostport[1]))
            loop.create_task(tcp_forward(client, sClient))
            await tcp_forward(sClient, client)
        else:
            pass