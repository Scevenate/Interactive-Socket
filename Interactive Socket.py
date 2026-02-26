#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from threading import Thread, Event
from typing import Literal, Optional
from ssl import create_default_context
from dataclasses import dataclass

version = (0, 0, 1)

@dataclass
class TCPClientConfig:
    connect: tuple[str, int]
    bind: Optional[tuple[str, int]] = None
    tls: bool=False
    encoding: Literal["utf-8", "hex"]="utf-8"

class TCPClientSocket:
    """
    Start a wrapped client TCP socket.
    The socket starts connected, but does not actively detect if it's closed.
    """
    def __init__(self, config: TCPClientConfig):
        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self.config = config
        if config.bind:
            self.socket.bind(config.bind)
        self.socket.connect(config.connect)
        if config.tls:
            self.tls()
    def tls(self):
        self.socket = create_default_context().wrap_socket(self.socket, server_hostname=self.config.connect[0])
        self.config.tls = True
    def setEncoding(self, encoding: Literal["utf-8", "hex"]):
        self.config.encoding = encoding
    def recv(self, bufsize: int, flags: int=0) -> str:
        match self.config.encoding:
            case "utf-8":
                return self.socket.recv(bufsize, flags).decode(encoding="utf-8")
            case "hex":
                return self.socket.recv(bufsize, flags).hex()
            case _:
                raise ValueError("Encoding not supported")
    def send(self, data: str, flags: int = 0) -> int:
        match self.config.encoding:
            case "utf-8":
                return self.socket.send(data.encode(encoding='utf8'), flags)
            case "hex":
                return self.socket.send(bytes.fromhex(data), flags)
    def close(self):
        self.socket.shutdown(SHUT_RDWR)


class TCPSession(Thread):
    """
    The main thread for a TCP session.
    Responsible for parsing user input, execute derivatives and writing data.
    A socket is coupled with a daemon thread, which reads the socket and notices when the socket is closed.
    """
    def __init__(self, socket:TCPClientSocket):
        """
        Starts a new interactive socket session.
        The socket must be already in connection. The session will exit right away if the socket is already closed.
        """
        super().__init__()
        self.socket = socket
        self.event = Event()
    def run(self):
        TCPSessionService(self.socket, self.event).start()
        while not self.event.is_set():
            buffer = self.string_eval(input("\033[0m>>> \033[1m"))
            if not buffer:
                continue
            if buffer[0] == ":":
                if len(buffer) == 1 or buffer[1] != ":":
                    match buffer:
                        case ":close":
                            self.socket.close()
                        case ":tls":
                            self.socket.tls()
                        case _:
                            print("\033[0mUnknown directive.")
                            print()
                            print("Available directives:")
                            print(":close Close the socket and end the session.")
                            print(":tls TLS encrypt, using the hostname passed at establishment.")
                            print(":: Send regular message starting with a colon.")
                    continue
                buffer = buffer[1:]
            self.socket.send(buffer)
    @staticmethod
    def string_eval(s: str) -> str:
        """
        This method parses escape sequences in the input.
        Only a restricted set of escape characters are parsed, e.g. quotes and back slashes not followed by a escape character are preserved.
        This method aims to simplify input in an interactive context.
        """
        s = s.replace(r"\n", "\n")
        s = s.replace(r"\r", "\r")
        return s

class TCPSessionService(Thread):
    def __init__(self, socket:TCPClientSocket, event: Event):
        super().__init__()
        self.socket = socket
        self.event = event
    def run(self):
        while not self.event.is_set():
            try:
                buffer = self.socket.recv(65536)
            except BrokenPipeError:
                buffer = ""
            if not buffer:
                self.event.set()
                print("\033[0mSocket Closed.", end="")
            else:
                print("\033[0m" + buffer + "\n>>> \033[1m", end="")

class Session(Thread):
    def run(self):
        print("Interactive socket v" + ".".join(map(str, version)) + " 2026 (c) Scevenate")
        while True:
            buffer = input(":").split()
            if not buffer:
                continue
            match buffer[0]:
                case "exit":
                    exit(0)
                case "help":
                    self.help(*buffer)
                case "tcp":
                    self.tcp(*buffer)
                case _:
                    print("Unidentified directive. Use ':help' for help.")
    def help(self, *args):
        print("Available directives:")
        print(":exit Exit script.")
        print(":help Show help info.")
        print(":tcp Start new tcp session.")
    def tcp(self, *args: str):
        if len(args) == 1:
            print("Usage: tcp [flags] [-b [binding address]] [connect address]")
            print()
            print("Flags:")
            print("--tls use TLS connection.")
            print("--hex Start raw hex session. (Default utf-8 encoded)")
            print()
            print("Address Format:")
            print("domain:port")
            print("ip:port")
            print(":port")
            print("Domain is used as hostname to establish tls connection.")
            return
        config = TCPClientConfig(("", -1))
        i = 1
        while i < len(args):
            match args[i]:
                case "--tls":
                    config.tls = True
                case "--hex":
                    config.encoding = "hex"
                case "-b":
                    i += 1
                    if i == len(args):
                        print("Expected bind address after flag '-b'.")
                        return
                    bind = args[i].split(":")
                    try:
                        config.bind = (bind[0], int(bind[1]))
                    except IndexError or ValueError:
                        print("Invalid port number.")
                        return
                case _:
                    connect = args[i].split(":")
                    try:
                        config.connect = (connect[0], int(connect[1]))
                    except IndexError or ValueError:
                        print("Invalid port number.")
                        return
            i += 1
        if config.connect == ("", -1):
            print("Expected connect address.")
            return
        try:
            print("Connecting...")
            s = TCPClientSocket(config)
        except OSError:
            print("Cannot connect to designated address.")
            return
        TCPSession(s).run()
                    
if __name__ == "__main__":
    Session().run()