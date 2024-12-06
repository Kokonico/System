"""System, A.K.A Central Comamand And Control System (CCACS)"""
from System import int_tts as tts

class System:
    def __init__(self):
        tts.speak("Boot sequence initiated")
        tts.speak("Boot sequence complete, all systems operational. Hello, Captain.")


if __name__ == "__main__":
    System()
