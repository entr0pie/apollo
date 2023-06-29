#!/bin/python3

from Apollo.base import Request

req = Request()
req.headers['Host'] = 'example.com'
print(req.send().headers)
