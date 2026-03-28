import os
import socket
import tempfile
import unittest
from unittest.mock import patch

from epaper.utils.watchdog import sd_notify


class TestSdNotify(unittest.TestCase):
    def test_does_nothing_when_notify_socket_not_set(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("NOTIFY_SOCKET", None)
            # Must not raise
            sd_notify("WATCHDOG=1")

    def test_sends_message_to_filesystem_socket(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sock_path = os.path.join(tmpdir, "notify.sock")
            server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            server.bind(sock_path)
            server.settimeout(1)

            with patch.dict(os.environ, {"NOTIFY_SOCKET": sock_path}):
                sd_notify("READY=1")

            data = server.recv(64)
            server.close()
            self.assertEqual(data, b"READY=1")

    def test_sends_watchdog_ping(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sock_path = os.path.join(tmpdir, "notify.sock")
            server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            server.bind(sock_path)
            server.settimeout(1)

            with patch.dict(os.environ, {"NOTIFY_SOCKET": sock_path}):
                sd_notify("WATCHDOG=1")

            data = server.recv(64)
            server.close()
            self.assertEqual(data, b"WATCHDOG=1")

    def test_silently_ignores_missing_socket_env(self):
        env_without_socket = {
            k: v for k, v in os.environ.items() if k != "NOTIFY_SOCKET"
        }
        with patch.dict(os.environ, env_without_socket, clear=True):
            sd_notify("READY=1")  # must not raise


if __name__ == "__main__":
    unittest.main()
