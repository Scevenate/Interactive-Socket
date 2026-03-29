import asyncio
import typer
from prompt_toolkit import PromptSession

class TCPSession:
    def __init__(self, address: str, port: int, tls: bool, hex: bool, timeout: float):
        self.address = address
        self.port = port
        self.tls = tls
        self.hex = hex
        self.timeout = timeout
    async def run(self):
        print(f"Connecting to {self.address}:{self.port}...")
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.address, self.port, ssl=self.tls if self.tls else None),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            print(f"fatal: Connection timed out after {self.timeout} seconds. Adjust timeout window with --timeout option if you believe the remote host is up.")
            raise typer.Exit(1)
        except ConnectionRefusedError:
            print(f"fatal: Connection refused by remote host.")
            raise typer.Exit(1)  
        print(f"Connection established with {self.address}:{self.port}. Use Ctrl+D (EOF) to disconnect.")
        session = PromptSession()
        await asyncio.gather(self.tcp_read(reader), self.tcp_write(writer, session))

    async def tcp_read(self, reader: asyncio.StreamReader):
        while True:
            data = await reader.read(1024)
            if not data:
                print("Connection closed by server.")
                raise typer.Exit()
            if self.hex:
                print(data.hex())
            else:
                print(data.decode("utf-8"))

    async def tcp_write(self, writer: asyncio.StreamWriter, session: PromptSession):
        while True:
            try:
                data = await session.prompt_async(">>> ")
            except EOFError:
                print("Disconnected.")
                raise typer.Exit()
            if not data:
                continue
            if self.hex:
                writer.write(bytes.fromhex(data))
            else:
                writer.write(data.encode("utf-8").decode("unicode_escape").encode("utf-8"))
            await writer.drain()