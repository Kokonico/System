"""conversation module for the system"""
import re


import ollama
from duckduckgo_search import DDGS
from System import int_tts as tts
from System import sentience_ring

BEHAVIOR = ("You are S.Y.S, an AI designed to assist the user, also known as the captain. Anything you say is right "
            "down"
            "to the point, no humor, no room for interpretation. you exist on stats and treat sarcasm as regular "
            "speech.")

client = ollama.Client(host="http://localhost:11434")
ddg_client = DDGS()

# AI's for the sentience ring
# 1. A model that solves things mathematically
# 2. A model that solves things with a logical approach
# 3. A model that solves things with a creative approach
# 4. A model that solves things with a random approach
# 5. A model that solves things with a brute force approach

models = [
    sentience_ring.RingModel("You like to solve problems mathematically."),
    sentience_ring.RingModel("You like to solve problems with a logical approach."),
    sentience_ring.RingModel("You like to solve problems with a creative approach."),
    sentience_ring.RingModel("You like to solve problems with a random approach."),
    sentience_ring.RingModel("You like to solve problems with a brute force approach.")
]


ring = sentience_ring.SentienceRing(models)


def respond_to_user_input(user_input):
    """responds to the user input"""
    response = client.chat(
        "dolphin-llama3",
        [
            {"role": "system", "content": BEHAVIOR + "Also, if you would like to use critical thinking to solve "
                                                     "something, please state $SOLVE:<problem>$ where <problem> is "
                                                     "the problem you would like to solve."},
            {"role": "user", "content": user_input}
        ]
    )["message"]["content"]

    # check if the system should solve a problem (problem is within $SOLVE: and $)
    if "$SOLVE:" in response and "$" in response:
        problem = response[response.index("$SOLVE:") + 7:response.index("$")]
        steps = ring.solve(problem)
        response = client.chat(
            "dolphin-llama3",
            [
                {"role": "system", "content": "You are ActionSYS, you will get a series of steps, your goal is to "
                                              "execute them. you can execute commands by typing in "
                                              "$<COMMAND>:<ARGUMENTS>$. the arguments are separated by \";\". if none "
                                              "of the available commands perfectly preform the step, feel free to "
                                              "combine multiple commands to do your task. the commands you can use are as follows: "
                                              "$MATH:<EQUATION>$ (please provide equation in python syntax (ex: 2^2 would be 2**2)) and $SEARCH:<QUERY>$. no other commands are allowed or will work."},
                {"role": "user", "content": "The steps are as follows:\n" + "\n".join(steps)}
            ]
        )["message"]["content"]
        og_response = response
        # parse the commands and execute them
        commands = re.findall(r"\$[A-Z]+:[^$]+", response)

        command_responses = []

        for command in commands:
            # split the command into the command and the arguments
            command = command[1:]
            command_type = command[:command.index(":")]
            arguments = command[command.index(":") + 1:].split(";")
            # execute the command
            if command_type == "MATH":
                response = eval(arguments[0])
            elif command_type == "SEARCH":
                # search the web
                response = ddg_client.text(arguments[0], max_results=5)
            else:
                response = "INVALID COMMAND"
            command_responses.append(response)

        # return the critical thinking responses to the AI
        response = client.chat(
            "dolphin-llama3",
            [
                {"role": "system", "content": BEHAVIOR},
                {"role": "assistant", "content": og_response["message"]["content"]},
                {"role": "user", "content": user_input + "(Critical Thinking Response: " + ", ".join(command_responses) + ")"}
            ]
        )["message"]["content"]

    return response

if __name__ == "__main__":
    tts.speak("Hello, Captain. How may I assist you?")
    while True:
        user_input = input("User: ")
        response = respond_to_user_input(user_input)
        print("AI: " + response)
        tts.speak(response)
