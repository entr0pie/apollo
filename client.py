#!/bin/python3 

from urllib.parse import urlparse
from Apollo.base import Request, Response

def get(url: str, headers: dict = {}, body: str = "") -> Response:
    """Do a GET request. Returns a Response object."""

    request = Request()
    
    parsed_url = urlparse(url)
    request.headers['Host'] = parsed_url.netloc
    request.path = parsed_url.path if parsed_url.path != "" else "/"

    for key, value in headers.items():
        request.headers[key] = value

    request.body = body
    return request.send()

def post(url: str, headers: dict = {}, data: dict = {}, json: dict = {}):
    
    if data == {} and json == {}:
        raise Exception("Both data and json parameters passed.")

    req: Request = Request() 
    req.method = "POST"
    req.fromURL(url)
    
    for key, value in headers.items():
        req.headers[key] = value
   
    if 'Content-Type' not in req.headers.keys():
        req.headers['Content-Type'] = "application/x-www-form-urlencoded" 
    
    req.body = req.encodeBody(data)
    return req.send()
print(get("http://example.com").headers)
