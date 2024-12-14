from helpers import audio, genai, micro
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main():
    model = genai.Model()
    await model.establish_connection()

    while True:
        input("Press Enter to start recording...")
        import time

        a = time.time()
        mic = micro.Microphone()
        response = await model.send_audio(mic.record_to_bytes(3))

        gen = await audio.AudTTS(response)
        print(time.time() - a)
        await audio.speakAudio(gen)


import asyncio

asyncio.run(main())
