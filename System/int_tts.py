"""tts wrapper for System TTS"""
import os

def speak(text):
    """uses the espeak command to speak the given text"""
    # write the text to a file
    with open("tts.txt", "w") as file:
        file.write(text)
    # use the espeak command to read the file
    os.system("espeak -v en-us -f tts.txt")
    os.remove("tts.txt")
