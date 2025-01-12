"""System, A.K.A S.Y.S"""
import json
import os


# create config folder if it doesn't exist
if not os.path.exists(os.path.join(os.path.expanduser("~"), ".aisysconfig")):
    os.mkdir(os.path.join(os.path.expanduser("~"), ".aisysconfig"))
    # create status.json file
    with open(os.path.join(os.path.expanduser("~"), ".aisysconfig", "status.json"), "w") as file:
        json.dump({
            "ollama_server": "http://localhost:11434",
            "ollama_model": "dolphin-llama3:8b",
            "corpus": os.path.join(os.path.expanduser("~"), ".aisysconfig", "corpus.txt"),
            "logs": os.path.join(os.path.expanduser("~"), ".aisysconfig", "comms.log"),
            "journal": os.path.join(os.path.expanduser("~"), ".aisysconfig", "journal.txt")
        }, file)

from . import int_tts as tts
from . import conversational as conv

def say(text: str):
    """Speak and print the given text"""
    print(text)
    tts.speak(text)


def main():
    """The main function"""
    # greet the user
    say("Hello! I am S.Y.S, a conversational assistant. How can I help you today?")
    # start the conversation
    while True:
        user_input = input("You: ")
        if user_input.startswith("/"):
            # command mode
            if user_input == "/exit":
                say("Goodbye!")
                break
            elif user_input.startswith("/setmodel"):
                model_name = user_input.split(" ")[1]
                conv.model = model_name
                with open("status.json", "w") as file:
                    conv.status["ollama_model"] = model_name
                    json.dump(conv.status, file)
                say(f"Model set to {model_name}, keep in mind that this model may not exist, so make sure that it "
                    f"does. also, make sure you downloaded it, that's important.")
        else:
            response = conv.respond_to_user_input(user_input)
            say(response)

if __name__ == "__main__":
    main()
