import asyncio
import socket 

async def main():
    # bind socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 1230
    s.bind(('c116171.wlan.net.ed.ac.uk', port))
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