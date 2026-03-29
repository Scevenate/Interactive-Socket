import typer
from TCPSession import TCPSession
import asyncio

app = typer.Typer()

@app.command()
def tcp(address: str = typer.Argument(help="IP address / domain name of the server."),
        port: int = typer.Argument(min=1, max=65535, help="Port number of the server."),
        hex: bool = typer.Option(False, help="Use hex IO instead of plain text."),
        tls: bool = typer.Option(False, help="Establish a TLS connection."),
        timeout: float = typer.Option(3.0, help="Timeout when establishing connection.")):
    print("Interactive Socket v0.2.0, Scevenate (c) 2026")
    asyncio.run(TCPSession(address, port, tls, hex, timeout).run())

if __name__ == "__main__":
    app()