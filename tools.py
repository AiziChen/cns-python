import base64
import re

HEADERS = [b"GET", b"POST", b"HEAD", b"PUT", b"COPY", b"DELETE", b"MOVE",
           b"OPTIONS", b"LINK", b"UNLINK", b"TRACE", b"PATCH", b"WRAPPER"]


def is_http_header(data: bytes) -> bool:
    for header in HEADERS:
        if data.startswith(header):
            return True
    return False


def response_header(data: bytes) -> bytes:
    if data.find(b'WebSocket') != -1:
        return b'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: CuteBi Network Tunnel, (%>w<%)\r\n\r\n'
    elif data.startswith("CON"):
        return b'HTTP/1.1 200 Connection established\r\nServer: CuteBi Network Tunnel, (%>w<%)\r\nConnection: keep-alive\r\n\r\n'
    else:
        return b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nServer: CuteBi Network Tunnel, (%>w<%)\r\nConnection: keep-alive\r\n\r\n'


def xor_cipher(data: bytes, passSub: int = 0) -> tuple[bytes, int]:
    data = bytearray(data)
    dataLen = len(data)
    if dataLen <= 0:
        return passSub
    else:
        passLen = len("quanyec")
        pi = passSub
        for dataSub in range(dataLen):
            pi = (dataSub + passSub) % passLen
            data[dataSub] ^= ord("quanyec"[pi]) | pi
        return data, pi + 1


def decrypt_host(host: str) -> str:
    bytesHost = base64.decodebytes(host.encode('utf8'))
    bytesHost, _ = xor_cipher(bytesHost)
    return bytesHost.decode('utf8')


def get_proxy_host(header: bytes) -> str:
    matched = re.search('Meng:\s*(.+)\r\n', header.decode('utf8'))
    return matched and matched[1].strip()
