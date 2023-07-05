import base64
import re

HEADERS = [b"GET", b"POST", b"HEAD", b"PUT", b"COPY", b"DELETE", b"MOVE",
           b"OPTIONS", b"LINK", b"UNLINK", b"TRACE", b"PATCH", b"WRAPPER"]


def is_http_header(data: bytes) -> bool:
    for header in HEADERS:
        if header.startswith(data):
            return True
    return False


def response_header(data: bytes) -> bytes:
    if data.find(b'WebSocket') != -1:
        return b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: CuteBi Network Tunnel, (%>w<%)\r\n\r\n'
    elif data.startswith("CON"):
        return b'HTTP/1.1 200 Connection established\r\nServer: CuteBi Network Tunnel, (%>w<%)\r\nConnection: keep-alive\r\n\r\n'
    else:
        return b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nServer: CuteBi Network Tunnel, (%>w<%)\r\nConnection: keep-alive\r\n\r\n'


def xor_cipher(data: bytes, passSub: int = 0) -> int:
    dataLen = data.count
    if dataLen <= 0:
        return passSub
    else:
        passLen = "quanyec".count
        pi = passSub
        for dataSub in dataLen:
            pi = (dataSub + passSub) % passLen
            data[dataSub] ^= "quanyec"[pi] | pi
        return pi + 1


def decrypt_host(host: str) -> str:
    bytesHost = base64.decodebytes(host.encode('utf8'))
    xor_cipher(bytesHost)
    return bytesHost.decode('utf8')


def get_proxy_host(header: str) -> str:
    matched = re.search('Mengt:\s*(.+)\r\n', header)
    return matched and matched[2]
