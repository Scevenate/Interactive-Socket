__version__ = "0.3.1"

import typer
import asyncio
from .tcp import TCPSession
from .udp import UDPSession

app = typer.Typer()

@app.command()
def tcp(address: str = typer.Argument(help="IP address / domain name of the server."),
        port: int = typer.Argument(min=1, max=65535, help="Port number of the server."),
        tls: bool = typer.Option(False, "-t", "--tls", help="Establish a TLS connection."),
        silent: bool = typer.Option(False, "-s", "--silent", help="Disable stdout prompting, stdout will only print socket output."),
        hex: bool = typer.Option(False, "-x", "--hex", help="Use hex IO instead of plain text."),
        timeout: float = typer.Option(3.0, "-T", "--timeout", help="Timeout when establishing connection.")):
    """
    Start an interactive TCP session.
    This command establishes a TCP connection and forwards it to stdin & stdout.
    """
    silent or print(f"Interactive Socket v{__version__}, Scevenate (c) 2026")
    asyncio.run(TCPSession(address, port, tls, silent, hex, timeout).run())

@app.command()
def udp(address: str = typer.Argument(help="IP address / domain name of the server."),
        port: int = typer.Argument(min=1, max=65535, help="Port number of the server."),
        silent: bool = typer.Option(False, "-s", "--silent", help="Disable stdout prompting, stdout will only print socket output."),
        hex: bool = typer.Option(False, "-x", "--hex", help="Use hex IO instead of plain text.")):
    """
    Start an interactive UDP session.
    This command creates a UDP endpoint and allows stdin & stdout interaction.
    """
    silent or print(f"Interactive Socket v{__version__}, Scevenate (c) 2026")
    asyncio.run(UDPSession(address, port, silent, hex).run())
