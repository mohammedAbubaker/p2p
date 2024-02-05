import asyncio
import socket
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaBlackhole, MediaRelay
import json

import cv2

async def main():
    pc = RTCPeerConnection()

    relay = MediaRelay()
    webcam = MediaPlayer(
            '0',
            format = 'avfoundation',
            options = {
                'video_size': '640x480',
                'framerate': '30'
            }
    )

    pc.addTrack(relay.subscribe(webcam.video))


    @pc.on("connectionstatechange")
    def on_connectionstatechange():
        print(pc.connectionState)

    async def negotiate():
        await pc.setLocalDescription(await pc.createOffer())
        data = pc.localDescription.__dict__
        data = json.dumps(data)
        await message_server(data)

        retrieve_answer = (await message_server("p1gib")).decode()
        while retrieve_answer == "":
            await asyncio.sleep(0.1)
            retrieve_answer = (await message_server("p1gib")).decode()
        
        retrieve_answer = json.loads(retrieve_answer)
        answer = RTCSessionDescription(retrieve_answer['sdp'], retrieve_answer['type'])
        await pc.setRemoteDescription(answer)
        await message_server("close")
    
    async def check_connection_state():
        while pc.connectionState != "connected":
            await asyncio.sleep(0.1)

        while pc.connectionState == "connected":
            await asyncio.sleep(0.1)


    async def message_server(message):
        if (message != "close") and (message != "p1gib"):
            message = "1" + message
        s = socket.socket()
        port = 1230
        s.connect(('c116171.wlan.net.ed.ac.uk', port))
        s.send(message.encode())
        response  = s.recv(4000)
        s.close()
        return response
    
    await asyncio.gather(negotiate(), check_connection_state())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
