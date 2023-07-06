import asyncio
import socket
import logging
from tools import *


async def tcp_forward(creader: asyncio.StreamReader, swriter: asyncio.StreamWriter):
    sub = 0
    while True:
        data = await creader.read(12288)
        if not data:
            break
        data, sub = xor_cipher(data, sub)
        swriter.write(data)
    swriter.close()
    await swriter.wait_closed()


async def handle_tcp_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, data: bytes):
    logging.info('handing tcp session')
    host = get_proxy_host(data)
    if host == None:
        writer.write(b'No proxy host')
        await writer.drain()
    else:
        host = decrypt_host(host)[0:-1]
        logging.info(f'proxy host: {host}')
        # if not host.endswith(':53'):
        if host.find(':') == -1:
            host += ':80'
        hostport = host.split(':')
        sfut = asyncio.open_connection(hostport[0], int(hostport[1]))
        try:
            sreader, swriter = await asyncio.wait_for(fut=sfut, timeout=6)
        except:
            writer.write(
                f'Proxy  address [{host}] ResolveTCP() error'.encode('utf8'))
            await writer.drain()
            return
        ssock: socket.socket = swriter.get_extra_info('socket')
        ssock.setsockopt(socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 0)
        ssock.setblocking(False)

        asyncio.create_task(tcp_forward(reader, swriter))
        await tcp_forward(sreader, writer)
        swriter.close()
        # else:
        #     pass
