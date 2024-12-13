import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import logging


class Microphone:
    def __init__(self, rate=16000, chunk_size=4096):
        self.rate = rate
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )
        self.log = logging.getLogger("mic")

    def read(self):
        return self.stream.read(self.chunk_size, exception_on_overflow=False)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


def record_to_file(duration_secs, filename="output.wav", rate=16000, chunk_size=4096):
    mic = Microphone(rate=rate, chunk_size=chunk_size)
    frames = []

    mic.log.info(f"recording for {duration_secs} seconds...")
    for _ in range(0, int(rate / chunk_size * duration_secs)):
        frames.append(mic.read())

    mic.close()

    wf = wave.open(filename, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(mic.p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()

    mic.log.info(f"recording saved to {filename}")
    return filename


def plot_waveform(filename):
    wf = wave.open(filename, "rb")
    signal = wf.readframes(-1)
    signal = np.frombuffer(signal, dtype=np.int16)
    plt.plot(signal)
    plt.show()


duration = 5
output_file = "output.wav"
record_to_file(duration_secs=duration, filename=output_file)
plot_waveform(output_file)
