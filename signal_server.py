import asyncio
import socket 

async def main():
    # bind socket
    s = socket.socket()
    port = 1232
    s.bind(('localhost', port))
    s.listen(5)

    p1_info = ""
    p2_info = ""

    while True:
        c, _ = s.accept()
        response = (c.recv(4000)).decode()
        
        if response == "close":
            c.close()
            break

        if response == "p1gib":
            c.send(p2_info.encode())
        
        if response == "p2gib":
            c.send(p1_info.encode())

        if response[0] == "1":
            p1_info = response[1:]
            c.send("ACK".encode())

        if response[0] == "2":
            p2_info = response[1:]
            c.send("ACK".encode())
        
        print(response)
    
asyncio.run(main()) 