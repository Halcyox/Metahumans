import pathlib
import sys, time, os
import pandas as pd
import typing
import random
import logging
import io

import xragents
from xragents import setting, scene
from xragents import audio, utils, cast
from xragents.types import Character
from xragents.scene import Scene

class InputModality:
    def get_line():
        pass

def personPlusAi(chr: Character):
    history = []
    """This is a basic conversation between you and an AI. Choose your session description and what characters you want."""
    text_only = input("Text only? [Y/n]").lower() != "n" # ask for text_only flag
    with scene.make_scene(id=utils.next_session(),
                    name="Contemplations on Entities",
                    description=f"The following is an enlightening conversation between you and {chr.name} about the nature of artificial and biological entities, on the substance of souls, individuality, agency, and connection.",
                    characters=[chr], 
                    text_only=text_only
                    ) as sess:
        
        # Create directories to temporarily store audio files
        utils.create_audio_directories()

        # Convo loop starts here
        shouldntExit = True 
        logging.info("This is an example info log!")
        print(f"You are now talking with {chr.name}!")
        print(f"Conversation description: {sess.description}")
        print(f"{chr.name}: {chr.desc} ")
        while True: # Loops until "quit" keyword or silence is detected
            # if we have text_only flag set on, we don't record audio
            if not sess.text_only:
                latest_record = audio.listen_until_quiet_again() # Audio based user input
            else:
                latest_record = audio.ListenRecord(io.BytesIO(), pathlib.Path("dummy_file.wav"), input(f"<{len(sess.history)/4}/2048> You: ")) # Text based user input
            #print(latest_record.spoken_content)

            if(latest_record.spoken_content == "quit" or latest_record.spoken_content is None): # Trigger for ending convo, will then concatenate
                break

            latest_record.file_handle.close()
            sess.user_provided_input(latest_record)
            response = sess.make_speak(chr, chr.primitivePath)
            history.append(setting.DialogHistory(response))
            #print(f"{chr.name}: {response}")

        # Save the audio files to the output directory
        #time.sleep(0.5) # time pause for audio files to be written properly (prevents error)
        if not sess.text_only:
            audio.concat_audio_double_directory("recording/ai/", "recording/user/") # the finished audio file is saved
            audio.cleanup("recording/ai/", "recording/user/") # delete the temporary files

        return history
    
from xragents.database import conversation_history
from flask import request

def personPlusAiWeb(chr: Character):
    # Get the entire conversation history so far as a single string
    history_string = conversation_history.get_history_string()
    """This is a basic conversation between you and an AI. The conversation is initiated by the frontend."""
    text_only = True # Since we're getting text from the frontend
    with scene.make_scene(id=utils.next_session(),
                    name="Contemplations on Entities",
                    description=f"The following is an enlightening conversation between you and {chr.name} about the nature of artificial and biological entities, on the substance of souls, individuality, agency, and connection.",
                    characters=[chr], 
                    text_only=text_only
                    ) as sess:
        
        # Create directories to temporarily store audio files
        utils.create_audio_directories()

        # Convo loop starts here
        shouldntExit = True 
        logging.info("This is an example info log!")
        print(f"You are now talking with {chr.name}!")
        print(f"Conversation description: {sess.description}")
        print(f"{chr.name}: {chr.desc} ")
        
        # Here we're getting the text from the frontend client instead of listening for audio
        user_text = request.json['text'] 

        # Add the user's message to the conversation history
        # conversation_history.add_message(f"You: {user_text}")

        # Concatenate the conversation history and the user's message to form the prompt
        prompt = f"{history_string}\nYou: {user_text}"

        latest_record = audio.ListenRecord(io.BytesIO(), pathlib.Path("dummy_file.wav"), prompt) # Text based user input

        if(latest_record.spoken_content == "quit" or latest_record.spoken_content is None): # Trigger for ending convo, will then concatenate
            return

        latest_record.file_handle.close()
        sess.user_provided_input(latest_record)
        response = sess.make_speak(chr, chr.primitivePath)
        sess.report_histfrag(f"{chr.name}: {response}") # append to history
        # history.append(setting.DialogHistory(response))
        conversation_history.add_message(f"You: {user_text}") # user response
        conversation_history.add_message(f"{chr.name}: {response}") # ai response

        # Save the audio files to the output directory
        if not sess.text_only:
            audio.concat_audio_single_directory("recording/ai/", "recording/user/") # the finished audio file is saved
            audio.cleanup("recording/ai/", "recording/user/") # delete the temporary files

        return


# def twoAiPlusPerson(chr1: Character, chr2: Character):
#     history = []
#     """This is a basic conversation between you and an AI. Choose your session description and what characters you want."""
#     with scene.make_scene(id=utils.next_session(),
#                     name="Contemplations on Entities",
#                     description=f"The following is an entertaining convo between {chr1.name} and {chr2.name} about the nature of artificial and biological entities, on the substance of souls, individuality, agency, and connection.",
#                     characters=[chr1, chr2],
#                     text_only=True,
#                     ) as sess:
#         # Create directories
#         utils.create_directory("recording/output/", False) # Output should not be cleared
#         utils.create_directory("recording/ai/") # Clears temporary files there
#         utils.create_directory("recording/user/") # Clears temporary files there

#         shouldntExit = True # conversation will loop until user wants to exit
#         print(f"You are now talking with {chr1.name} and {chr2.name}!")
#         print(f"Conversation description: {sess.description}")
#         #print(f"{chr.name}: {chr.desc} ")
#         while shouldntExit: # Keeps looping and listening to the user and gets input from AI as long as "quit" is not said by user
#             latest_record = audio.listen_until_quiet_again() # Audio based user input
#             #latest_record = audio.ListenRecord(io.BytesIO(), pathlib.Path("dummy_file.wav"), input("You: ")) # Text based user input
#             #print(latest_record.spoken_content)

#             if(latest_record.spoken_content == "quit" or latest_record.spoken_content is None): # Trigger for ending convo, will then concatenate
#                 shouldntExit = False
#                 break

#             latest_record.file_handle.close()

#             for chr in sess.characters:
#                 response = sess.make_speak(chr, chr.primitivePath)
#                 history.append(setting.DialogHistory(response))

#             #print(f"{chr.name}: {response}")

#         # Save the audio files to the output directory
#         #time.sleep(0.5) # time pause for audio files to be written properly (prevents error)
#         audio.concat_audio_double_directory("recording/ai/", "recording/user/") # the finished audio file is saved
#         audio.cleanup("recording/ai/", "recording/user/") # delete the temporary files

#         return history

def twoAiPlusPerson(chr1: Character, chr2: Character):
    history = []
    """This is a basic conversation between you and an AI. Choose your session description and what characters you want."""
    # with scene.make_scene(id=utils.next_session(),
    #                 name="Contemplations on Entities",
    #                 description=f"The following is an entertaining convo between {chr1.name} and {chr2.name} about the nature of artificial and biological entities, on the substance of souls, individuality, agency, and connection.",
    #                 characters=[chr1, chr2],
    #                 text_only=True,
    #                 ) as sess:
        
    with scene.make_scene(id=utils.next_session(),
                    name="Horrible debate between two strange characters.",
                    description=f"The following is a spirited intellectual conversation between {chr1.name} and {chr2.name} about artificial intelligence, the nature of the cosmos, Homo Sapiens, and life itself.",
                    characters=[chr1, chr2],
                    text_only=True,
                    ) as sess:
        

        # Create directories
        utils.create_directory("recording/output/", False) # Output should not be cleared
        utils.create_directory("recording/ai/") # Clears temporary files there
        utils.create_directory("recording/user/") # Clears temporary files there

        shouldntExit = True # conversation will loop until user wants to exit
        print(f"You are now talking with {chr1.name} and {chr2.name}!")
        print(f"Conversation description: {sess.description}")
        #print(f"{chr.name}: {chr.desc} ")
        while shouldntExit: # Keeps looping and listening to the user and gets input from AI as long as "quit" is not said by user
            # latest_record = audio.listen_until_quiet_again() # Audio based user input
            # latest_record = audio.ListenRecord(io.BytesIO(), pathlib.Path("dummy_file.wav"), input("You: ")) # Text based user input
            #print(latest_record.spoken_content)
        
            # if(latest_record.spoken_content == "quit" or latest_record.spoken_content is None): # Trigger for ending convo, will then concatenate
            #     shouldntExit = False

            # latest_record.file_handle.close()

            for chr in sess.characters:
                response = sess.make_speak(chr, chr.primitivePath)
                history.append(setting.DialogHistory(response))

            #print(f"{chr.name}: {response}")

        # Save the audio files to the output directory
        #time.sleep(0.5) # time pause for audio files to be written properly (prevents error)
        # audio.concat_audio_double_directory("recording/ai/", "recording/user/") # the finished audio file is saved
        # audio.cleanup("recording/ai/", "recording/user/") # delete the temporary files

        return history
    
# def interactive_conversation(scene: Scene):
#     """This is a basic conversation between you and n numbers of AI. Choose your session description and what characters you want."""
#     history = []
#     with scene as sess:
#         # Create directories
#         utils.create_directory("recording/output/", False) # Output should not be cleared
#         utils.create_directory("recording/ai/") # Clears temporary files there
#         utils.create_directory("recording/user/") # Clears temporary files there

#         shouldntExit = True # conversation will loop until user wants to exit
#         print(f"You are now talking with {chr1.name} and {chr2.name}!")
#         print(f"Conversation description: {sess.description}")
#         #print(f"{chr.name}: {chr.desc} ")
#         while shouldntExit: # Keeps looping and listening to the user and gets input from AI as long as "quit" is not said by user
#             # latest_record = audio.listen_until_quiet_again() # Audio based user input
#             # latest_record = audio.ListenRecord(io.BytesIO(), pathlib.Path("dummy_file.wav"), input("You: ")) # Text based user input
#             #print(latest_record.spoken_content)
        
#             # if(latest_record.spoken_content == "quit" or latest_record.spoken_content is None): # Trigger for ending convo, will then concatenate
#             #     shouldntExit = False

#             # latest_record.file_handle.close()

#             for chr in sess.characters:
#                 response = sess.make_speak(chr, chr.primitivePath)
#                 history.append(setting.DialogHistory(response))

#             #print(f"{chr.name}: {response}")

#         # Save the audio files to the output directory
#         #time.sleep(0.5) # time pause for audio files to be written properly (prevents error)
#         # audio.concat_audio_double_directory("recording/ai/", "recording/user/") # the finished audio file is saved
#         # audio.cleanup("recording/ai/", "recording/user/") # delete the temporary files

#         return history
    