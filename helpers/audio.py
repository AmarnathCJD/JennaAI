from aiohttp import ClientSession, ClientTimeout
import base64
import logging


async def AudTTS(text: str):
    async with ClientSession(timeout=ClientTimeout(total=10)) as session:
        async with session.post(
            f"https://audio.api.speechify.com/generateAudioFiles",
            json={
                "audioFormat": "mp3",
                "paragraphChunks": text_to_pragraph_chunks(text),
                "voiceParams": {
                    "name": "carly",
                    "engine": "speechify",
                    "languageCode": "en-US",
                },
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Content-Type": "application/json",
                "Accept-Base64": "true",
                "Accept-Encoding": "gzip, deflate, br",
            },
        ) as response:
            try:
                resp = await response.json()
                logging.getLogger("aud").info("audio generated")
                return base64.b64decode(resp["audioStream"])
            except Exception as e:
                logging.getLogger("aud").error(e)
                return e


def text_to_pragraph_chunks(text: str):
    return [text[i : i + 200] for i in range(0, len(text), 200)]
