from google import genai
from google.genai.types import ContentDict, PartDict
from config import GEMINI_KEY
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
                while True:
                    request = await self.queue.get()
                    if request is None:
                        break
                    if "audio" in request:
                        await session.send(
                            {"data": request["audio"], "mime_type": "audio/pcm"},
                            end_of_turn=True,
                        )
                    else:
                        await session.send(request["text"], end_of_turn=True)

                    resp = ""
                    async for message in session.receive():
                        resp += message.text if message.text else ""
                    await self.resp.put(resp)
        except Exception as e:
            self.log.error(e)

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


async def main():
    model = Model()
    await model.establish_connection()
    f = open("output.pcm", "rb")
    wav = f.read()
    f.close()
    # convert wav to pcm
    pcm_data = wav[44:]

    try:
        response = await model.send_audio(wav)
        print(response)
    finally:
        await model.queue.put(None)
        await model.task


asyncio.run(main())
