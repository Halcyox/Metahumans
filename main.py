# Importing necessary libraries
import sys
import time
import os
import pandas as pd
import random
import logging
from dataclasses import dataclass
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem
import xragents
from xragents import setting, scene
from xragents import audio, utils, cast, simulator, anim
from xragents.types import Character
from dataclass_csv import DataclassReader
from flask import Flask, request, jsonify
from flask_cors import CORS

# Flask app configuration for API handling
app = Flask(__name__)
CORS(app) # Enables cross-origin resource sharing

# Importing database modules from xragents
from xragents.database import conversation_history, transaction

# Route for handling conversation API requests
@app.route('/api/converse', methods=['POST'])
def converse():
    character = cast.Avatar # Customizable character selection
    simulator.personPlusAiWeb(character)
    print(conversation_history.print_history())
    return jsonify({'text': conversation_history.get_history()[-1]})

# Cleanup function for Flask app context
@app.teardown_appcontext
def teardown_appcontext(exception=None):
    conversation_history.close()

# Logging configuration
class CustomFormatter(logging.Formatter):
    # Color codes and format string for logging
    grey, yellow, red, bold_red, reset = "\x1b[38;20m", "\x1b[33;20m", "\x1b[31;20m", "\x1b[31;1m", "\x1b[0m"
    fmtstr = "%(asctime)s - %(name)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + fmtstr + reset,
        logging.INFO: red + fmtstr + reset,
        logging.WARNING: yellow + fmtstr + reset,
        logging.ERROR: grey + fmtstr + reset,
        logging.CRITICAL: bold_red + fmtstr + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Setting up the logger
logger = logging.getLogger("multiagency")
logger.setLevel(logging.DEBUG) # Log level can be adjusted here
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
logging.root = logger

# Configuration for scene characters
NUM_ACTORS = 2 # Maximum number of actors is 5 without performance issues
primPaths = ["/World/audio2face/PlayerStreaming"] # Primitive path references
for i in range(NUM_ACTORS-1):
    primPaths.append(f"/World/audio2face_{(i+1):02d}/PlayerStreaming")

# Reading voice styles from a CSV file
VOICES = pd.read_csv("deps/streaming_server/resources/VoiceStyles.csv")

def allocate_characters(num_characters:int,names:list[str],descriptions: list[str]) -> dict[str,Character]:
    """Allocates characters for the scene based on provided names and descriptions."""
    if num_characters > NUM_ACTORS:
        raise Exception("Too many characters for the number of actors.")
    characters = {}
    for i in range(num_characters):
        characters[names[i]] = Character(names[i], desc=descriptions[i], id=0,
                                         voice=VOICES.sample(n=1)["Voice"].iloc[0],
                                         primitivePath=primPaths[i])
    return characters

def conversation_from_txtfile_dir(dir):
    """
    Plays a conversation script stored as text files in a given directory.
    
    Args:
        dir (str): Directory containing text files with conversation scripts.
    """
    inputFiles = []
    for file in os.listdir(dir):
        if file.endswith(".txt"):
            inputFiles.append(os.path.join(dir, file))

    # Debug print to show all input files found
    print(f"dbg:{inputFiles}")

    for index, file in enumerate(inputFiles):
        print(index, file)
        with open(file, 'r') as f:
            lines = f.readlines()
            nAIs(lines, index + 1)

def conversation_from_audiofiles_dir(selected_show_integer:int):
    """
    Plays a conversation from audio clips that already have an entire script.

    Args:
        dir (str): Directory containing audio files with conversation scripts.
    
    Format is in directory folders with the following naming convention:
    Attempt # (Title of the conversation)

    Inside the folders, the audio files are named as follows:
    hal_1.wav, hal_3.wav, hal_5.wav, etc.
    sophia_2.wav, sophia_4.wav, sophia_6.wav, etc.

    Basically, we read the integers counting up and then play the corresponding audio files. This allows us to easily generate and the store the turns in the conversation.

    We call the animate directly from here, so we don't need to save the history.
    """
    primPathsList = ["/World/audio2face/PlayerStreaming", "/World/audio2face_01/PlayerStreaming"]
    # Define the animator function
    def animator(wavPath, primPathsList):
        anim.animate(wavPath, primPathsList)

    audio.play_wav_files(selected_show_integer, base_path="scripts/recorded_show/", animator_function=animator)
    

def nAIs(lines, sessid=1):
    """
    Plays a pre-written conversation from a list of lines, supporting multiple characters.
    Useful for testing audio-visual systems and scripted conversations.

    Args:
        lines (list of str): Lines of the script.
        sessid (int, optional): Session ID. Defaults to 1.

    Format of input file:
    Character1: Hello, how are you?
    Character2: I am fine, thank you.
    """
    # Create necessary output directories
    utils.create_directory("scripts/output_audio/", False)
    utils.create_directory("scripts/output_text/", False)
    utils.create_directory("scripts/ai/")

    # Extracting unique character names from the script
    characters = {}
    for line in lines:
        if ":" in line:
            name = line.split(":")[0]
            if name not in characters:
                characters[name] = 1

    # Allocating characters for the scene
    characters = allocate_characters(len(characters), list(characters.keys()), ["", ""])

    # Creating and managing the scene
    # TODO: Inform a server about our new scene some day!
    with scene.make_scene(id=0,
                          name="Contemplations on Entities",
                          description="An enlightening conversation about the nature of entities.",
                          characters=list(characters.values()),
                          text_only=False) as sess:
        for line in lines:
            if ":" in line:
                name, text = line.split(":", 1)
                sess.animate(characters[name], charLine=text)

        # Save conversation history
        sess.save_history(outputDir="scripts/output_text/")
        time.sleep(0.5)

        # Concatenate audio and save the output file
        audio.concat_audio_single_directory("scripts/ai/", outputPath="scripts/output_audio/output_" + str(time.time()) + ".wav")


# Console menu setup for interaction with the simulator
menu = ConsoleMenu("XRAgents", "Simulator Root Menu")

# Define functions to be called from the menu
def one_ai():
    """
    Starts the simulator with a single AI character.
    """
    watchTV = setting.InfiniteTelevision()
    print("Starting the simulator with one AI")
    simulator.personPlusAi(cast.KillerOfWorlds)
    simulator.conversation()

def two_ai():
    """
    Starts the simulator with two AI characters.
    """
    watchTV = setting.InfiniteTelevision()
    simulator.twoAiPlusPerson(cast.Avatar, cast.CarlSagan)

    # with open(input("file path to load:")) as f:
    #     reader = DataclassReader(f, scene.Scene)
    #     scene = next(reader)
    #     simulator.interactive_conversation(scene)

def play_recorded_show():
    """
    Plays a recorded show from a directory containing audio files.
    """
    selected_show_number = int(input("Enter the show number to play:"))
    conversation_from_audiofiles_dir(selected_show_number)

# Add options to the menu, FunctionItem returns a python function
one_ai_item = FunctionItem("Talk with an AI", one_ai)
two_ai_item = FunctionItem("Watch two AI talk together", two_ai)
play_recorded_show_item = FunctionItem("Play a recorded show", play_recorded_show)
menu.append_item(one_ai_item)
menu.append_item(two_ai_item)
menu.append_item(play_recorded_show_item)
    
# Define functions for file management
def clear_prompt_files():
    """
    Clears all prompt files with specific naming pattern from the current directory.
    """
    files_here = (o for o in os.listdir(".") if o.startswith("prompt-") and o.endswith(".txt"))
    for f in files_here:
        print(f"Removing {f}...", file=sys.stderr)
        os.remove(f)

def zip_prompt_files():
    """
    Zips all prompt files from the current directory and then clears them.
    """
    import zipfile
    files_here = (o for o in os.listdir(".") if o.startswith("prompt-") and o.endswith(".txt"))
    with zipfile.ZipFile(f"prompt-files-{time.time()}.zip", "w") as zip:
        for f in files_here:
            print(f"Adding {f}...", file=sys.stderr)
            zip.write(f)
    clear_prompt_files()

# Adding file management options to the menu
menu.append_item(FunctionItem("Zip prompt history", zip_prompt_files))

# Run Flask app if script is executed as the main program
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Display the menu for user interaction
menu.show()

