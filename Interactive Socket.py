from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Event
from typing import Literal, Optional
from ssl import create_default_context
from time import sleep

class ClientTCPSocket:
    """
    Start a wrapped client TCP socket.
    The socket starts connected, but does not actively detect if it's closed.
    """
    def __init__(self,
                 connect: tuple[str, int],
                 bind: Optional[tuple[str, int]]=None,
                 tls: bool=False,
                 encoding: Literal["utf-8", "hex"]="utf-8"
                 ):
        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        if bind:
            self.socket.bind(bind)
        self.socket.connect(connect)
        self.encoding: Literal["utf-8", "hex"] = encoding
        if tls:
            self.tls()
    def tls(self):
        self.socket = create_default_context().wrap_socket(self.socket)
    def setEncoding(self, encoding: Literal["utf-8", "hex"]):
        self.encoding = encoding
    def recv(self, bufsize: int, flags: int=0) -> str:
        match self.encoding:
            case "utf-8":
                return self.socket.recv(bufsize, flags).decode(encoding="utf-8")
            case "hex":
                return self.socket.recv(bufsize, flags).hex()
            case _:
                raise ValueError("Encoding not supported")
    def send(self, data: str, flags: int = 0) -> int:
        return self.socket.send(data.encode(encoding=self.encoding), flags)
    def close(self):
        self.socket.close()


class TCPSession(Thread):
    """
    The main thread for a TCP session.
    Responsible for parsing user input, execute derivatives and writing data.
    A socket is coupled with a daemon thread, which reads the socket and notices when the socket is closed.
    """
    def __init__(self, socket:ClientTCPSocket):
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
            if len(buffer) >= 2 and buffer[0] == ":":
                if buffer[1] != ":":
                    match buffer:
                        case ":exit":
                            exit(0)
                        case ":close":
                            self.socket.close()
                        case ":tls":
                            self.socket.tls()
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
    def __init__(self, socket:ClientTCPSocket, event: Event):
        super().__init__()
        self.socket = socket
        self.event = event
    def run(self):
        while not self.event.is_set():
            buffer = self.socket.recv(65535)
            if not buffer:
                self.event.set()
                print("\033[0mSocket Closed.", end="")
            else:
                print("\033[0m" + buffer + "\n>>> \033[1m", end="")

TCPSession(ClientTCPSocket(("example.com", 80))).run()