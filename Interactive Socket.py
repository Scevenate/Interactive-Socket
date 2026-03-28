import typer
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

app = typer.Typer()

@app.command()
def tcp(address: str = typer.Argument(help="IP address / domain name of the server."),
        port: int = typer.Argument(min=1, max=65535, help="Port number of the server."),
        hex: bool = typer.Option(False, help="Use hex IO instead of plain text."),
        tls: bool = typer.Option(False, help="Establish a TLS connection."),
        timeout: float = typer.Option(3.0, help="Timeout when establishing connection.")):
    print("Interactive Socket v0.2.0, Scevenate (c) 2026")
    with patch_stdout():
        asyncio.run(tcp_session(address, port, tls, hex, timeout))

async def tcp_session(address: str, port: int, tls: bool, hex: bool, timeout: float):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(address, port, ssl=tls if tls else None),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        print(f"fatal: Connection timed out after {timeout} seconds. Adjust timeout window with --timeout option if you believe the remote host is up.")
        raise typer.Exit(1)
    except ConnectionRefusedError:
        print(f"fatal: Connection refused by remote host.")
        raise typer.Exit(1)  
    print(f"Connection established with {address}:{port}. Use Ctrl+D (EOF) to disconnect.")
    session = PromptSession()
    await asyncio.gather(tcp_read(reader, hex), tcp_write(writer, hex, session))

async def tcp_read(reader: asyncio.StreamReader, hex: bool):
    while True:
        data = await reader.read(1024)
        if not data:
            print("Connection closed by server.")
            raise typer.Exit()
        if hex:
            print(data.hex())
        else:
            print(data.decode("utf-8"))

async def tcp_write(writer: asyncio.StreamWriter, hex: bool, session: PromptSession):
    while True:
        try:
            data = await session.prompt_async(">>> ")
        except EOFError:
            print("Disconnected.")
            raise typer.Exit()
        if not data:
            continue
        if hex:
            writer.write(bytes.fromhex(data))
        else:
            writer.write(data.encode("utf-8").decode("unicode_escape").encode("utf-8"))
        await writer.drain()

if __name__ == "__main__":
    app()