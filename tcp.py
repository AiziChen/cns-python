import asyncio
import socket
import logging
from tools import *


async def tcp_forward(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    sub = 0
    while True:
        data = await reader.read(12288)
        if not data:
            break
        data = bytearray(data)
        sub = xor_cipher(data, sub)
        writer.write(data)
    writer.close()


async def handle_tcp_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, data: bytes):
    logging.info('handing tcp session')
    host = get_proxy_host(data)
    if not host:
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
                f'Proxy address [{host}] ResolveTCP() error'.encode('utf8'))
            await writer.drain()
            return
        if sreader and swriter:
            try:
                ssock: socket.socket = swriter.get_extra_info('socket')
                ssock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 0)
                ssock.setblocking(False)

                asyncio.create_task(tcp_forward(sreader, writer))
                await tcp_forward(reader, swriter)
            except:
                pass
            finally:
                swriter.close()
                await swriter.wait_closed()
        # else:
        #     pass
