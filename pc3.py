import asyncio
import time
from aiortc import RTCPeerConnection, RTCRtpSender
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaStreamError, MediaStreamTrack
import cv2
import av



async def main():
    pc1 = RTCPeerConnection()
    pc2 = RTCPeerConnection()

    relay = MediaRelay()
    webcam = MediaPlayer('default:none', 'avfoundation', options={'framerate': '30', 'video_size': '640x480'})
    pc1.addTrack(relay.subscribe(webcam.video))

    @pc2.on("track")
    async def on_track(track):
        while True:
            frame = await track.recv()
            cv2.imshow('Frame', frame.to_ndarray(format='bgr24'))
            cv2.waitKey(1)

    async def exchange_offer_answer():
        offer = await pc1.createOffer()
        await pc1.setLocalDescription(offer)
        await pc2.setRemoteDescription(pc1.localDescription)
        answer = await pc2.createAnswer()
        await pc2.setLocalDescription(answer)
        await pc1.setRemoteDescription(pc2.localDescription)

    async def check_connection_state():
        while pc1.connectionState != "connected" and pc2.connectionState != "connected":
            await asyncio.sleep(0.1)

        while pc1.connectionState == "connected" and pc2.connectionState == "connected":
            await asyncio.sleep(0.1)
        
        
        
    await asyncio.gather(exchange_offer_answer(), check_connection_state())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())