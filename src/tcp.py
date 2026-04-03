import asyncio
import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import sys

class TCPSession:
    """
    An interactive TCP session.
    The session establishes a TCP connection and forwards the socket to stdin / stdout for interaction.
    """
    def __init__(self, address: str, port: int, tls: bool = False, silent: bool = False, hex: bool = False, timeout: float = 3.0):
        """
        Initialize the TCP session.
        silent: Disables stdout prompting, stdout will only print socket output.
        hex: Whether to use hex IO.
        timeout: The timeout for establishing connection.
        """
        self.address = address
        self.port = port
        self.tls = tls
        self.silent = silent
        self.hex = hex
        self.timeout = timeout
    async def run(self):
        """
        Start the asynchronous TCP session.
        Establishes connection and adds read & write tasks to the event loop.
        """
        self.silent or print(f"Connecting to {self.address}:{self.port}...")
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.address, self.port, ssl=self.tls if self.tls else None),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            print(f"fatal: Connection timed out after {self.timeout} seconds. Adjust timeout window with --timeout option if you believe the remote host is up.", file=sys.stderr)
            raise typer.Exit(1)
        except ConnectionRefusedError:
            print("fatal: Connection refused by remote host.", file=sys.stderr)
            raise typer.Exit(1)  
        self.silent or print(f"Connection established with {self.address}:{self.port}. Use Ctrl+D (EOF) to disconnect.")
        await asyncio.gather(self._tcp_read(reader), self._tcp_write(writer))

    async def _tcp_read(self, reader: asyncio.StreamReader):
        """
        Read data and print to stdout.
        """
        while True:
            data = await reader.read(4096)
            if not data:
                self.silent or print("Connection closed by server.")
                raise typer.Exit()
            if self.hex:
                print(data.hex())
            else:
                print(data.decode("utf-8"))

    async def _tcp_write(self, writer: asyncio.StreamWriter):
        """
        Wait for stdin. Sends data to the server.
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
                self.silent or print("Disconnected.")
                raise typer.Exit()
            if not data:
                continue
            if self.hex:
                try:
                    data = bytes.fromhex(data)
                except ValueError:
                    print("error: Invalid hex string.", file=sys.stderr)
                    continue
                writer.write(data)
            else:
                writer.write(data.encode("utf-8").decode("unicode_escape").encode("utf-8"))
            await writer.drain()