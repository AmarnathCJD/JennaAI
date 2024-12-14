from google import genai
from google.genai.types import ContentDict, PartDict
from .config import GEMINI_KEY
from .micro import Microphone
import asyncio
import logging

client = genai.Client(api_key=GEMINI_KEY, http_options={"api_version": "v1alpha"})
config = {
    "response_modalities": ["TEXT"],
    "system_instruction": ContentDict(
        parts=[
            PartDict(text="Your name is 'Jenna'"),
            PartDict(text="You are A multi-functional, AI of Windows 11"),
            PartDict(text="Act witty and smart"),
        ],
        role="SYSTEM",
    ),
}


class Model:
    def __init__(self):
        self.model = "gemini-2.0-flash-exp"
        self.queue = asyncio.Queue()
        self.resp = asyncio.Queue()
        self.log = logging.getLogger("gen")

    async def start(self):
        try:
            async with client.aio.live.connect(
                model=self.model, config=config
            ) as session:
                task1 = asyncio.create_task(self.handle_queue(session))
                task2 = asyncio.create_task(self.receive_messages(session))

                await asyncio.gather(task1, task2)
        except Exception as e:
            self.log.error(e)

    async def handle_queue(self, session):
        while True:
            request = await self.queue.get()
            if request is None:
                break
            if "audio" in request:
                await session.send(
                    {"data": request["audio"], "mime_type": "audio/pcm"},
                    end_of_turn=request.get("end_of_turn", False),
                )
            else:
                await session.send(request["text"], end_of_turn=True)

    async def receive_messages(self, session):
        curr_text = ""

        async for message in session.receive():
            text = message.text if message.text else ""
            if not message.server_content.turn_complete:
                curr_text += text
            else:
                await self.resp.put(curr_text)
                curr_text = ""

    async def establish_connection(self):
        self.task = asyncio.create_task(self.start())

    async def send_message(self, text: str):
        await self.queue.put({"text": text})
        response = await self.resp.get()
        return response

    async def send_audio(self, audio: bytes):
        await self.queue.put({"audio": audio})
        response = await self.resp.get()
        return response

    async def record_audio(self, duration_secs):
        self.mic = Microphone()
        self.log.info(f"recording for {duration_secs} seconds...")
        last_iter = int(self.mic.rate / self.mic.chunk_size * duration_secs) - 1

        for _ in range(0, int(self.mic.rate / self.mic.chunk_size * duration_secs)):
            if _ == last_iter:
                await self.queue.put({"audio": self.mic.read(), "end_of_turn": True})
            else:
                await self.queue.put({"audio": self.mic.read()})

        self.log.info("recording finished")
        self.mic.close()

        response = await self.resp.get()
        return response
