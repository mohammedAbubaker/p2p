import asyncio
import socket
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaBlackhole, MediaRelay
import json

import cv2

async def main():
    pc = RTCPeerConnection()

    @pc.on("track")
    async def on_track(track):
        while True:
            frame = await track.recv()
            cv2.imshow('Frame', frame.to_ndarray(format='bgr24'))
            cv2.waitKey(1) 

    async def negotiate():
        retrieve_offer = (await message_server("p2gib")).decode()
        while (retrieve_offer == ""):
            await asyncio.sleep(0.1)
            retrieve_offer = (await message_server("p2gib")).decode()
        retrieve_offer = json.loads(retrieve_offer)
        offer = RTCSessionDescription(retrieve_offer["sdp"], retrieve_offer["type"])
        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        data = pc.localDescription.__dict__
        data = json.dumps(data) 
        await message_server(data)
    
    async def check_connection_state():
        while pc.connectionState != "connected":
            await asyncio.sleep(0.1)

        while pc.connectionState == "connected":
            await asyncio.sleep(0.1)


    async def message_server(message):
        if (message != "close") and (message != "p2gib"):
            message = "2" + message
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