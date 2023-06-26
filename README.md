# Apollo - Python Module for HTTP Requests Using Sockets

## Description

Apollo is a lightweight Python module that allows you to perform HTTP requests using only sockets. It provides a simplified way to interact with web servers. This project was developed as a demonstration for my blog post on low-level networking in Python (make sure to check it out!).

## Installation

To use Apollo, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/entr0pie/apollo 
```

2. Change to the project directory:

```bash
cd apollo
```

## Usage

Apollo is very similar to the requests library. You can use it in two ways: 

1. Using the main functions:

```python
from Apollo import get, post 

response = get("http://example.com")
print(response.status_code)  # Output: 200

response = post("http://localhost/", data={"username":"admin", "password":"12345"})
print(response.body)  # Output: 415


response = post("http://localhost/", data={"username":"admin", "password":"12345"}, headers={"Content-Type": "application/json"})
print(response.body)  # Output: 403
```

2. Building up your request by hand:

```python
from Apollo import Request 

request = Request()
request.method = "DELETE"
request.path = "/api/user/delete"

request.headers['User-Agent'] = "Secret Spy"
response = request.send()
print(response.status_code)  # Output: 204
```

To test it somewhere, go to the `server` directory and start the docker container:

```bash
cd server
docker compose up --build
```

## Known Limitations and Issues

This project was developed to a blog post on how to use sockets and interact with HTTP servers. That way, it isn't meant for daily use. 

Also, Apollo was not built to handle `keep-alive` connections. If you're requesting with it, make sure to use `Connection: close` with it.

## License

This project is under the [Unlicense](LICENSE) license.
