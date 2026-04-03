import asyncio
import typer
import socket
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import sys

class _UDPProtocol(asyncio.DatagramProtocol):
    """
    A simple UDP protocol.
    The protocol prints data from the remote port to stdout.
    """
    def __init__(self, address: str, port: int, silent: bool, hex: bool):
        self.address = address
        self.port = port
        self.silent = silent
        self.hex = hex
    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.silent or self.silent or print(f"Endpoints created for {self.address}:{self.port}. Use Ctrl+D (EOF) to destroy.")
    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        if addr != (self.address, self.port):
            return
        if self.hex:
            print(data.hex())
        else:
            print(data.decode("utf-8"))
    def error_received(self, exc: Exception) -> None:
        print(f"fatal: {exc}", file=sys.stderr)
        raise typer.Exit(1)

class UDPSession:
    """
    An interactive UDP session.
    The session sends / receives datagrams from the remote port and forwards data to stdin / stdout for interaction.
    """
    def __init__(self, address: str, port: int, silent: bool, hex: bool):
        """
        Initialize the UDP session.
        silent: Disables stdout prompting, stdout will only print socket output.
        hex: Whether to use hex IO.
        """
        self.address = address
        self.port = port
        self.silent = silent
        self.hex = hex
    async def run(self):
        """
        Start the asynchronous UDP session.
        Creates the UDP endpoint and adds write task to the event loop.
        """
        self.silent or print(f"Creating endpoints for {self.address}:{self.port}...")
        transport, protocol = await asyncio.get_event_loop().create_datagram_endpoint(lambda: _UDPProtocol(self.address, self.port, self.silent, self.hex), remote_addr=(self.address, self.port), family=socket.AF_INET)
        await self._udp_write(transport)

    async def _udp_write(self, transport: asyncio.DatagramTransport):
        """
        Wait for stdin. Sends data to the remote port.
        Stdout will be patched if not in silent mode.
        """
        session = PromptSession()
        while True:
            try:
                if self.silent:
                    data = await session.prompt_async()
                else:
                    with patch_stdout():
                        data = await session.prompt_async(f"{self.address}:{self.port} >>> ")
            except EOFError:
                self.silent or print("Destroyed.")
                raise typer.Exit()
            if not data:
                continue
            if self.hex:
                try:
                    data = bytes.fromhex(data)
                except ValueError:
                    print("error: Invalid hex string.", file=sys.stderr)
                    continue
                transport.sendto(data, (self.address, self.port))
            else:
                transport.sendto(data.encode("utf-8").decode("unicode_escape").encode("utf-8"), (self.address, self.port))