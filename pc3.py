import asyncio
from aiortc import RTCPeerConnection

async def main():
    pc1 = RTCPeerConnection()
    pc1.addTransceiver("video", direction="sendonly")

    @pc1.on("connectionstatechange")
    def on_connectionstatechange():
        print(pc1.connectionState)

    pc2 = RTCPeerConnection()

    @pc2.on("connectionstatechange")
    def on_connectionstatechange():
        print(pc2.connectionState)  


    offer = await pc1.createOffer()
    await pc1.setLocalDescription(offer)

    await pc2.setRemoteDescription(pc1.localDescription)
    answer = await pc2.createAnswer()
    await pc1.setRemoteDescription(answer)
    await pc2.setLocalDescription(answer)
    while pc1.connectionState != "connected" and pc2.connectionState != "connected":
        await asyncio.sleep(1)

asyncio.run(main())