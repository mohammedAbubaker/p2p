import asyncio
import math
import socket
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
import cv2
from av import VideoFrame
from aiortc import RTCIceCandidate, RTCIceGatherer
from aiortc.contrib.media import MediaPlayer, MediaRecorder, MediaBlackhole
import json

import os

import numpy

ROOT = os.path.dirname(__file__)

class FlagVideoStreamTrack(VideoStreamTrack):
    """
    A video track that returns an animated flag.
    """

    def __init__(self):
        super().__init__()  # don't forget this!
        self.counter = 0
        height, width = 480, 640

        # generate flag
        data_bgr = numpy.hstack(
            [
                self._create_rectangle(
                    width=213, height=480, color=(255, 0, 0)
                ),  # blue
                self._create_rectangle(
                    width=214, height=480, color=(255, 255, 255)
                ),  # white
                self._create_rectangle(width=213, height=480, color=(0, 0, 255)),  # red
            ]
        )

        # shrink and center it
        M = numpy.float32([[0.5, 0, width / 4], [0, 0.5, height / 4]])
        data_bgr = cv2.warpAffine(data_bgr, M, (width, height))

        # compute animation
        omega = 2 * math.pi / height
        id_x = numpy.tile(numpy.array(range(width), dtype=numpy.float32), (height, 1))
        id_y = numpy.tile(
            numpy.array(range(height), dtype=numpy.float32), (width, 1)
        ).transpose()

        self.frames = []
        for k in range(30):
            phase = 2 * k * math.pi / 30
            map_x = id_x + 10 * numpy.cos(omega * id_x + phase)
            map_y = id_y + 10 * numpy.sin(omega * id_x + phase)
            self.frames.append(
                VideoFrame.from_ndarray(
                    cv2.remap(data_bgr, map_x, map_y, cv2.INTER_LINEAR), format="bgr24"
                )
            )

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = self.frames[self.counter % 30]
        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame

    def _create_rectangle(self, width, height, color):
        data_bgr = numpy.zeros((height, width, 3), numpy.uint8)
        data_bgr[:, :] = color
        return data_bgr




class WebCamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture("SampleVideo_1280x720_1mb.mp4")

    async def next_frame(self):
        pts, _ = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            return None
        return VideoFrame.from_ndarray(frame, format="bgr24")

async def main():

    pc = RTCPeerConnection()
    pc.addTrack(FlagVideoStreamTrack())
    
    @pc.on("icecandidate")
    def on_icecandidate(candidate):
        print("on_icecandidate", candidate)
    
    @pc.on("connectionstatechange")
    def on_connectionstatechange():
        print(pc.connectionState)
    
    @pc.on("iceconnectionstatechange")
    def on_iceconnectionstatechange():
        print(pc.iceConnectionState)

    

        
    async def message_server(message):
        if (message != "close") and (message != "p1gib"):
            message = "1" + message
        s = socket.socket()
        port = 1232
        s.connect(('localhost', port))
        s.send(message.encode())
        response  = s.recv(4000)
        s.close()
        return response

    # create an offer and attach it to pc
    await pc.setLocalDescription(await pc.createOffer())
    # convert local description to dictionary
    data = pc.localDescription.__dict__
    # convert dictionary to json
    data = json.dumps(data)
    # send offer to peer
    offer_response = (await message_server(data)).decode()
    if (offer_response) != "ACK":
        raise Exception("Offer not accepted")
    
    # attempt to retrieve p2info
    p2_info = (await message_server("p1gib")).decode()
    while (p2_info == ""):
        await asyncio.sleep(0.1)
        p2_info = (await message_server("p1gib")).decode()

    answer_data = json.loads(p2_info)
    answer = RTCSessionDescription(answer_data["sdp"], answer_data["type"])    
    await pc.setRemoteDescription(answer)

    while pc.connectionState != "connected":
        await asyncio.sleep(1)  

    # close server
    await message_server("close")


loop = asyncio.get_event_loop()
loop.run_until_complete(main()) 
