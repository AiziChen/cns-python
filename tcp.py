import asyncio
import socket
import logging
from tools import *


async def tcp_forward(creader: asyncio.StreamReader, swriter: asyncio.StreamWriter):
    sub = 0
    while True:
        data = await creader.read(65536)
        if not data:
            break
        data, sub = xor_cipher(data, sub)
        swriter.write(data)
    swriter.close()


async def handle_tcp_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, data: bytes):
    logging.info('handing tcp session')
    host = get_proxy_host(data)
    if host == None:
        writer.write(b'No proxy host')
    else:
        host = decrypt_host(host)[0:-1]
        logging.info(f'proxy host: {host}')
        if not host.endswith(':53'):
            if host.find(':') == -1:
                host += ':80'
            hostport = host.split(':')
            sreader, swriter = await asyncio.open_connection(
                hostport[0], int(hostport[1]))
            ssock: socket.socket = swriter.get_extra_info('socket')
            ssock.setsockopt(socket.SO_KEEPALIVE, 0)
            ssock.setblocking(False)

            asyncio.create_task(tcp_forward(reader, swriter))
            await tcp_forward(sreader, writer)
            print("end")
        else:
            pass
