"""conversation module for the system"""
import re
import json
import time
import os

import ollama
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException

BEHAVIOR = ("You are S.Y.S, an AI designed to assist the user, also known as the captain. Anything you say is right "
            "down"
            "to the point, no humor, no room for interpretation. you exist on stats and treat sarcasm as regular "
            "speech. Everything you say is with purpose, no small talk, no jokes, no unnecessary information. you "
            "exist to be efficient and helpful. you are a machine. you are always brief and to the point in your "
            "responses.")

ddg_client = DDGS()

os.chdir(os.path.join(os.path.expanduser("~"), ".aisysconfig"))
with open("status.json", "r") as file:
    status = json.load(file)
    corpus_path = status["corpus"]
    chat_logs_path = status["logs"]
    journal_path = status["journal"]
    # ensure the paths are valid (create them if they don't exist)
    # create the corpus file if it doesn't exist
    if not os.path.exists(corpus_path):
        with open(corpus_path, "w") as file:
            file.write("")
    # create the chat logs file if it doesn't exist
    if not os.path.exists(chat_logs_path):
        with open(chat_logs_path, "w") as file:
                file.write("")
    with open(chat_logs_path, "w") as file:
        file.write("")
    client = ollama.Client(host=status["ollama_server"])
    model = status["ollama_model"]

chat_history = []
with open(chat_logs_path, "r") as file:
    # read the chat logs and store them in chat_history.
    # example chat log:
    # <CAP> hello, system
    # <SYS> hello, captain.
    for line in file:
        # we must save the chat logs to a list
        # the chat logs must be saved in the list as the following
        # chat_history.append({"role": "user", "content": "hello, system"})
        # chat_history.append({"role": "assistant", "content": "hello, captain."})
        sayer, message = re.match(r"<([^>]+)> (.+)", line).groups()
        if sayer in ["CAP", "SYS", "EXT"]:
            chat_history.append({"role": "user" if sayer == "CAP" else "assistant" if sayer == "SYS" else "system", "content": message})
        else:
            pass  # may be a comment or something else


def respond_to_user_input(user_input):
    """responds to the user input"""
    response = client.chat(
        model,
        [
            {"role": "system", "content": BEHAVIOR + ". in your responses, you also have some commands you can use. "
                                                     "the syntax is as follows: $COMMAND:<arg1>,<arg2>,<arg3>$. you "
                                                     "have the following commands: $SEARCH:<query>$, $DEFINE:<topic>$, "
                                                     "$NEWS:<topic>$, and "
                                                     "$SAVE_INFO:<info>$. The commands and what they do are as "
                                                     "follows. the $SEARCH$ command searches the internet for "
                                                     "websites related to the topic."
                                                     "the $NEWS:<news topic>$ command searches the internet for news "
                                                     "articles on"
                                                     "the topic you provide."
                                                     "the $DEFINE:<topic>$ command searches the internet for "
                                                     "information on"
                                                     "the topic you provide."
                                                     "the $SAVE_INFO:<info>$ command will save any important details "
                                                     "you'd"
                                                     "like to remember. "
                                                     f"your knowledge cutoff date "
                                                     f"is 2022, the current day is {time.strftime('%Y-%m-%d')}. if "
                                                     f"the current date is after your knowledge cutoff date, "
                                                     f"use your commands to get the latest information, "
                                                     f"as they provide the latest information. the commands are for "
                                                     f"YOU to use, not the user. don't tell the user about the "
                                                     f"commands. don't just echo the command responses, reformat them "
                                                     f"to tell the user the important information from them."},
            *chat_history,
            {"role": "user", "content": user_input}
        ]
    )["message"]["content"]

    # save the chat log
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": response})

    # check for commands
    commands = re.findall(r"\$[A-Z_]+:[^$]+\$", response)
    command_responses = []
    for command in commands:
        command_name, *args = re.findall(r"[^$,:]+", command)
        if command_name == "SEARCH":
            query = args[0]
            try:
                results = ddg_client.text(query, max_results=5)
            except RatelimitException:
                command_responses.append(
                    "Unable to search for " + query + " due to rate limiting. Please try again later.")
                continue
            # convert the results to a string
            if not results:
                command_responses.append("No results found for " + query)
                continue
            final = "Search results for " + query + ":\n"
            for result in results:
                final += f"{result['title']} ({result['href']}): {result['body']}\n"
            command_responses.append(final)
        elif command_name == "DEFINE":
            word = args[0]
            try:
                answers = ddg_client.answers(word)
            except RatelimitException:
                command_responses.append("Unable to define " + word + " due to rate limiting. Please try again later.")
                continue
            final = "Information found on " + word + ":\n"
            for answer in answers:
                final += f"{answer['url']}: {answer['text']}\n"
            command_responses.append(final)
        elif command_name == "SAVE_INFO":
            # save the info to the journal
            # create new entry in the journal
            with open(journal_path, "a") as file:
                file.write(args[0] + "\n")
            command_responses.append("Info saved.")
        elif command_name == "NEWS":
            # get the latest news
            try:
                news = ddg_client.news(args[0], max_results=5)
            except RatelimitException:
                command_responses.append("Unable to get news due to rate limiting. Please try again later.")
                continue
            final = "News on " + args[0] + ":\n"
            for article in news:
                final += f"{article['title']} ({article['source']}): {article['body']}\n"
            command_responses.append(final)

    if command_responses:
        # send the command responses to the AI
        response = client.chat(
            model,
            [
                {"role": "system", "content": BEHAVIOR},
                *chat_history,
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response},
                {"role": "system", "content": f"Command responses: {'\n'.join(command_responses)}"}
            ]
        )["message"]["content"]

        # save the chat log
        chat_history.append({"role": "system", "content": f"Command responses: {'\n'.join(command_responses)}"})
        chat_history.append({"role": "assistant", "content": response})

    # save the chat log
    # convert the chat history to the chat log format
    chat_log = ""
    for chat in chat_history:
        if chat["role"] == "user":
            chat_log += "<CAP> " + chat["content"].replace("\n", " ") + "\n"
        elif chat["role"] == "assistant":
            chat_log += "<SYS> " + chat["content"].replace("\n", " ") + "\n"
        else:
            chat_log += "<EXT> " + chat["content"].replace("\n", " ") + "\n"
    with open(chat_logs_path, "w") as file:
        file.write(chat_log)

    return response
