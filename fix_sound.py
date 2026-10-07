import wave
import math
import struct

sample_rate = 44100
duration = 0.6
frequency = 450
volume = 0.8

with wave.open("sounds/false_start.wav", "w") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate

        # Descending warning tone
        freq = frequency - 250 * (t / duration)

        sample = volume * math.sin(
            2 * math.pi * (frequency * t - 125 * t * t / duration)
        )

        # Fade out to prevent clicking
        sample *= 1 - t / duration

        value = int(sample * 32767)

        wav.writeframes(
            struct.pack("<h", value)
        )

print("False-start sound regenerated successfully!")