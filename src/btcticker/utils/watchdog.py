import logging
import os
import socket


def sd_notify(message: str) -> None:
    """Send a notification to systemd via the sd_notify protocol.

    Does nothing when NOTIFY_SOCKET is not set (i.e. not running under systemd).
    Supports both filesystem paths and abstract Unix sockets (prefixed with '@').
    Silently logs and ignores socket errors so a bad NOTIFY_SOCKET never crashes the service.
    """
    notify_socket = os.environ.get("NOTIFY_SOCKET")
    if not notify_socket:
        return
    # Abstract sockets use '\0' as the first byte; systemd signals this with '@'
    addr = "\0" + notify_socket[1:] if notify_socket.startswith("@") else notify_socket
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), addr)
    except OSError:
        logging.warning("sd_notify failed (NOTIFY_SOCKET=%s)", notify_socket)
