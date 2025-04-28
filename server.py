from textual_serve.server import Server

server = Server("poetry run python main.py")
server.serve()
