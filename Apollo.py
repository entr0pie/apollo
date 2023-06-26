#!/bin/python3

from abc import ABC 
from json import dumps 
from copy import deepcopy

from urllib.parse import urlparse, quote_plus
import socket

default_headers: dict = {"Connection":"close", "User-Agent":"Apollo"} 

class HTTPMessage(ABC):
    """Abstract class representing a HTTP Message.
    Use only the Response and Request classes.
    """

    start_line: str = "" 
    headers: dict = {} 
    body: str = "" 
    http_version: str = ""
    
    def fromRaw(self, raw_message: str):
        """Turns a HTTP Message string into a object"""

        lines: list = raw_message.splitlines()
        self.start_line = lines[0]
        body_separator: int = lines.index("")

        headers: list = [lines[h] for h in range(1, body_separator)]
        
        for header in headers:
            key, value = header.split(':', 1)
            self.headers[key] = value.strip()

        for b in range(body_separator + 1, len(lines)):
            self.body += lines[b] + "\n"

class Response(HTTPMessage):
    """Server response. Used by the Request class."""

    status_code: int = 0
    status_message: str = ""

    def __init__(self, raw_response: str):
        self.fromRaw(raw_response)

    def fromRaw(self, raw_response: str):
        super().fromRaw(raw_response)
        start_elements: list = self.start_line.split(' ')
        
        self.http_version = start_elements[0] 
        self.status_code = int(start_elements[1])
        self.status_message = start_elements[2]
    
    def print(self):
        text: str = ""
        text += f"> {self.http_version} {self.status_code} {self.status_message}\n"

        for key, value in self.headers.items():
            text += f"> {key}: {value}\n"

        text += "\n"

        text += self.body 
        print(text) 

class Request(HTTPMessage):
    """Client Request."""
    
    method: str = "GET"
    path: str = "/"
    http_version: str = "HTTP/1.1"
    headers = deepcopy(default_headers)
    
    def fromRaw(self, raw_request: str):
        """Reads a request in string format and maps it"""
        
        super().fromRaw(raw_request)
        start_elements: list = self.start_line.split(' ')

        self.method = start_elements[0]
        self.path = start_elements[1] 
        self.http_version = start_elements[2]

    def fromURL(self, url: str):
        """Creates a basic request based in a url"""
        
        parsed_url = urlparse(url)
        self.headers['Host'] = parsed_url.netloc
        self.path = parsed_url.path if parsed_url.path != "" else "/"

    def _mountRequest(self) -> bytes:
        """Returns a byte string of the Request. Data to be sent in the send() method."""
        
        request: str = f"{self.method} {self.path} {self.http_version}\r\n"
        contains_body: bool = bool(self.body != "")
        
        if 'Content-Length' not in self.headers.keys() and contains_body: 
            self.headers['Content-Length'] = len(self.body)

        for key, value in self.headers.items():
            request += f"{key}: {value}\r\n"
        
        request += "\r\n"
        
        if contains_body:
            request += self.body 
        
        request += "\n"

        return request.encode()

    def encodeBody(self, data: dict) -> str:
        """Encode the body of a request. Returns the 
        encoded string."""

        body: str = ""
        content_type: str = self.headers['Content-Type']

        if content_type == "application/x-www-form-urlencoded":        
            for key, value in data.items():
                body += f"{key}={quote_plus(value)}&"
        
            return body[:-1]

        if content_type == "application/json":
            return dumps(data)

    def send(self) -> Response:
        """Requests the server, returning a Response object.
        Raises ConnectionRefusedError."""
        
        valid_request: bool = self.headers['Host'] and self.method and self.http_version 
        if not valid_request:
            raise Exception("Malformed request (Missing Host, Method and/or HTTP Version)")

        request_text: bytes = self._mountRequest()
        client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(((self.headers['Host']), 80))
        
        client.sendall(request_text)
        
        buffer_size: int = 4096
        response: bytes = b""

        while True:
            chunk = client.recv(buffer_size)
            if len(chunk) == 0:
                break
            response += chunk
        
        client.close()

        return Response(response.decode('latin-1'))

    def print(self):
        text: str = ""
        text += f"> {self.method} {self.path} {self.http_version}\n"
        for key, value in self.headers.items():
            text += f"> {key}: {value}\n"

        text += "\n"
        text += self.body

        print(text)

def fromFile(file_path: str) -> Request:
    """Makes a request based on a file. Returns a response object.
    Raises FileNotFoundError if the path specified was not found"""

    file_content = open(file_path, 'r').read()
    request: Request = Request()
    request.fromRaw(file_content)
    
    return request

def get(url: str, headers: dict = default_headers) -> Response:
    """Sends a GET request through a URL"""
    
    req: Request = Request()
    req.fromURL(url)
    
    for key, value in headers.items():
        req.headers[key] = value 

    return req.send()

def post(url: str, headers: dict = default_headers, data: dict = {}) -> Response:
    """POST request a server through URL"""

    req: Request = Request() 
    req.method = "POST"
    req.fromURL(url)
    
    for key, value in headers.items():
        req.headers[key] = value
   
    if 'Content-Type' not in req.headers.keys():
        req.headers['Content-Type'] = "application/x-www-form-urlencoded" 
    
    req.body = req.encodeBody(data)
    return req.send()
