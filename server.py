import socket
import asyncio

async def send_message(message):
    PORT = 2024
    ADDR = "morbius.inf.ed.ac.uk"
    s = socket.socket()
    s.connect((ADDR, PORT))
    s.send(message.encode())
    response  = s.recv(4000)
    s.close()
    return response 

async def main():
    print(await send_message("yoooo g"))

asyncio.run(main())