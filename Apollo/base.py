#!/bin/python3 

from abc import ABC, abstractmethod
from socket import socket 
from socket import AF_INET as IPv4
from socket import SOCK_STREAM as TCP
from socket import error as SocketError 

from json import loads 

default = loads(open('Apollo/default.json', 'r').read())

class HTTPMessage(ABC):
    """Generic HTTP message. Use Request and Response instead."""

    _start_line: list = [] 
    headers: dict = {}
    body: str = ""
    
    def marsh(self) -> bytes:
        """Converts the HTTP Message object to bytes, ready to be sent over a socket."""

        message: str = f"{self._start_line[0]} {self._start_line[1]} {self._start_line[2]}\r\n"
        contains_body: bool = self.body != ""
        
        if 'Content-Length' not in self.headers.keys() and contains_body: 
            self.headers['Content-Length'] = len(self.body)

        for key, value in self.headers.items():
            message += f"{key}: {value}\r\n"
        
        message += "\r\n"
        
        if contains_body:
            message += self.body 
        
        return message.encode()

    def unmarsh(self, raw_message: str):
        """Deserialize a generic HTTP message."""

        lines: list = raw_message.splitlines()
        self._start_line = lines[0].split(' ')
        body_separator: int = lines.index("")

        headers: list = [lines[h] for h in range(1, body_separator)]
        
        for header in headers:
            key, value = header.split(':', 1)
            self.headers[key] = value.strip()

        for b in range(body_separator + 1, len(lines)):
            self.body += lines[b] + "\n"

    def send(self, connection: socket) -> int:
        """Send the HTTP Message through a socket. Return the number of bytes sent. """
        
        message_bytes: bytes = self.marsh()
        return connection.sendall(message_bytes)
    
    @abstractmethod
    def recv(self, connection: socket) -> bytes:
        """Receives a HTTP Message through a socket. Returns the message in bytes."""
        pass

class Response(HTTPMessage):
    """Represents a HTTP response message."""

    def __init__(self, **attributes):
        available_keys: list = default['Response'].keys()
        given_keys: list = attributes.keys()

        for (default_key, default_value), (attr_key, attr_value) in zip(default['Response'], attributes):
            if attr_key in available_keys:
                setattr(self, attr_key, attr_value)
                continue
            if default_key not in given_keys:
                setattr(self, default_key, default_value)
    
    def unmarsh(self, raw_response: str):
        super().unmarsh(raw_response)
        self.http_version, self.status_code, self.status_message = self._start_line

    def send(self, connection: socket):
        self._start_line = [self.http_version, self.status_code, self.status_message]
        super().send(connection)

    def recv(self, connection: socket):
        """Receives a HTTP Message through a socket. Returns the message in bytes."""
        
        buffer_size = 1024  # Initial buffer size
        received_data = b""  # Initialize an empty byte string to store the received data

        while True:
            chunk = connection.recv(buffer_size)
            received_data += chunk

            if len(chunk) < buffer_size:
                break  # Break the loop if the received chunk is smaller than the buffer size

        return received_data.decode("latin-1") 

class Request(HTTPMessage):
    """Represents an HTTP request message."""
    
    _start_line = ["GET", "/", "HTTP/1.1"]
    headers = {"User-Agent":"Apollo", "Connection":"close"}
    
    method, path, http_version = _start_line 

    def unmarsh(self, raw_request: str):
        """Parses the raw HTTP request message and populates the request attributes."""
        
        super().unmarsh(raw_request)
        self.method, self.path, self.http_version = self._start_line

    def send(self) -> Response:
        """Send a Request. Return a Response object."""

        valid: bool = self.method and self.path and self.http_version and self.headers['Host']
        if not valid:
            raise Exception("Malformed request. Missing Method, Path, HTTP Version or Host header.")
        
        client = socket(IPv4, TCP)
        client.connect((self.headers['Host'], 80))
        super().send(client)

        response = Response()
        raw_response: bytes = response.recv(client) 
        response.unmarsh(raw_response)

        return response

    def recv(self, connection: socket):
        connection.setblocking(False)
        buffer_size: int = 1024
        data: bytes = b''

        while True:
            try:
                data += connection.recv(buffer_size)
                if not data:
                    break

            except SocketError:
                break

        return data
