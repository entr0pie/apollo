#!/bin/python3

from os import getcwd, listdir
from os.path import join as join_path
from socket import socket 
from socket import AF_INET as IPv4
from socket import SOCK_STREAM as TCP 
from threading import Thread
import logging 

from Apollo.base import Request, Response

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

class Server:
    def __init__(self, bind_address: tuple[str, int] = ("0.0.0.0", 8000), static_path: str = 'static'):
        self.address: tuple[str, int] = bind_address
        self.static_path: str = join_path(getcwd(), static_path)
        self.allowed_files: list = listdir(self.static_path)

    def handleRequest(self, conn: socket, addr: tuple[str, int]) -> Request:
        logging.debug('Reading the request')
        request = Request()
        data: bytes = request.recv(conn)
        request.unmarsh(data.decode())
        return request

    def findStatic(self, resource: str) -> str:
        resource = "index.html" if resource == "/" else resource
        resource = resource[1:] if resource[0] == "/" else resource
        
        if resource not in self.allowed_files:
            raise FileNotFoundError(resource) 

        file: str = open(join_path(self.static_path, resource), 'r').read()
        return file

    def handleClient(self, conn, addr):
        request = self.handleRequest(conn, addr)
        
        try:
            file = self.findStatic(request.path)
            response = Response(status_code=200, status_message="OK", headers={"Server":"Apollo"}, body=file)
            response.status_code = 200 
            response.status_message = "OK"
            response.headers["Server"] = "Apollo"
            response.body = file
            response.send(conn)
            conn.close()

        except FileNotFoundError:
            response = Response(status_code=404, status_message="Not found", headers={"Server":"Apollo"}, body="Not found")
            response.send(conn)
            conn.close()

        logging.info(f"({addr[0]}:{addr[1]}) [{response.status_code}] {request.method} {request.path} - {response.status_message}")


    def run(self):
        server = socket(IPv4, TCP)
        server.bind(self.address)
        server.listen(1)
        
        logging.info(f"Server started at port {self.address[1]}")
        
        try:
            while True:
                client_conn, client_addr = server.accept()
                logging.debug(f"Received connection from {client_addr[0]}:{client_addr[1]}")
                thread = Thread(target=self.handleClient, args=(client_conn, client_addr))
                thread.start()

        except KeyboardInterrupt:
            server.close()

