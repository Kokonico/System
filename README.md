# System
> lil' ai buddy


***MAKE SURE TO READ (SETUP)[#setup] BEFORE RUNNING, OR ELSE IT WON'T WORK***

***TESTED FOR MACOS AND LINUX, WINDOWS MAY WORK BUT NO GUARANTEES***

## About
System / S.Y.S / AISYS is an AI agent I have been experimentally building for a while now. They can search recent news, surf the internet, and get you the information you need.

## Should I use this in my everyday life?
No. This is mostly highly experimental and doesn't have any real use cases, I'm just building it to learn more about AI and how it works.

## Setup
1. get python 3.13
3. use `pip3.13 install aisys`, ***MAKE SURE PACKAGE EXECUTABLES ARE IN YOUR PATH***
4. see if you have `espeak` installed on your machine, as it is used for text-to-speech. (you can verify this by running `espeak <text>` in the terminal), sys will still work without it, but you won't get any audio feedback.
2. get (ollama)[https://ollama.com] and ensure that the server is running on your machine.
3. browse the (models available on ollama)[https://ollama.com/search] and find the model you want to use. The default model for this project is `dolphin-llama3`
4. run `ollama run <model name>` in the terminal to start the model, ***WAIT FOR IT TO FINISH DOWNLOADING***
5. ctrl-d to exit the model.
6. run `aisys` in the terminal to start the AI agent.
7. if the AI model you selected is not the default, run the command `/setmodel <model name>` to change the model.
8. enjoy!

## How to run
1. run `aisys` in the terminal
2. type in your query
3. wait for the response

## Commands
- `/setmodel <model name>`: sets the model to the one specified
- `/exit`: exits the program