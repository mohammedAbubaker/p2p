import asyncio
import socket
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaBlackhole    
import json

async def main():

    pc = RTCPeerConnection()
    recorder = MediaBlackhole()

    @pc.on("icecandidate")
    def on_icecandidate(candidate):
        print("on_icecandidate", candidate)
    
    @pc.on("track")
    def on_track(track):
        print("Track %s received", track.kind)
        recorder.addTrack(track)


    async def message_server(message):
        if (message != "close") and (message != "p2gib"):
            message = "2" + message
        s = socket.socket()
        port = 1232
        s.connect(('localhost', port))
        s.send(message.encode())
        response  = s.recv(4000)
        s.close()
        return response
    
    retrieve_offer = (await message_server("p2gib")).decode()
    while (retrieve_offer == ""):
        await asyncio.sleep(0.1)
        retrieve_offer = (await message_server("p2gib")).decode()

    # convert retrieve_offer from json to object
    retrieve_offer = json.loads(retrieve_offer)
    # create RTCSessionDescription from offer
    offer = RTCSessionDescription(retrieve_offer["sdp"], retrieve_offer["type"])
    # set offer as remote description
    await pc.setRemoteDescription(offer)
    # create an answer
    answer = await pc.createAnswer()
    # set answer as local description
    await pc.setLocalDescription(answer)

    # convert local description to dictionary
    data = pc.localDescription.__dict__
    # convert dictionary to json
    data = json.dumps(data)

    await message_server(data)

    while pc.connectionState != "connected":
        await asyncio.sleep(1)

 


loop = asyncio.get_event_loop()
loop.run_until_complete(main())