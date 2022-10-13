# Python program to translate
# Speech to text and text to speech
import sys, time, os

from server_local import server
from server_local.functions import audio, utils, mic
from server_local.classes import character, session
import pandas as pd


NUM_ACTORS = 2 # We can't get more than 5 without lagging usually, modify this if you want more actors in the USD scene

primPaths = ["/World/audio2face/PlayerStreaming"] # Make the primitive path references for the number of actors
for i in range(NUM_ACTORS-1):
    primPaths.append(f"/World/audio2face_{(i+1):02d}/PlayerStreaming")

VOICES = pd.read_csv("deps/streaming_server/resources/VoiceStyles.csv") # Read the available Microsoft Azure Voices
def allocate_characters(num_characters,names,descriptions):
    if num_characters > NUM_ACTORS:
        raise Exception("Too many characters for the number of actors.")
    characters = {}
    for i in range(num_characters):
        characters[names[i]] = character.Character(characterID=i+1,characterName=names[i],characterDescription=descriptions[i],primitivePath=primPaths[i],voice=VOICES.sample(n=1)["Voice"].iloc[0])
    return characters


def script_input(inputDir):
    # load all text files in the input directory into a list
    inputFiles = []
    for file in os.listdir(inputDir):
        if file.endswith(".txt"):
            inputFiles.append(os.path.join(inputDir, file))
    
    for index,file in enumerate(inputFiles):
        print(index,file)
        with open(file, 'r') as f:
            lines = f.readlines()
            nAIs(lines,index+1)
                

def nAIs(lines,sessid=1):
    #######################
    utils.create_directory("scripts/output_audio/", False)
    utils.create_directory("scripts/output_text/", False)
    utils.create_directory("scripts/ai/")
    #######################

    server.restart()
    server.initialize()

    # get the number of characters and their names
    characters = {}
    for line in lines:
        if ":" in line:
            name = line.split(":")[0]
            if name not in characters:
                characters[name] = 1
    characterDict = allocate_characters(len(characters),list(characters.keys()),["",""])

    characterIDList = []
    for _,val in characterDict.items():
        print("#######################",val)
        server.create_character(val.get_characterName(), val.get_characterDescription())
        characterIDList.append(val.get_characterID())
    IdString = ""
    # convert characterList to string
    for characterID in characterIDList:
        IdString += str(characterID)
    sess = session.Session(sessionID=sessid,
        sessionName="Contemplations on Entities", 
        sessionDescription="The following is an enlightening conversation between you and Avatar about the nature of artificial and biological entities, on the substance of souls, individuality, agency, and connection.", 
        characterIDs=IdString
    )
    server.create_session(sess.get_sessionName(), sess.get_sessionDescription(), sess.get_characterIDs())

    for line in lines:
        if ":" in line:
            name = line.split(":")[0]
            text = line.split(":")[1]
            server.animate_character(text,sess.get_sessionID(),characterDict[name].get_characterID(),characterDict[name].get_primitivePath(),characterDict[name].get_voice())
    utils.save_history(server,sess.get_sessionID(),outputDir="scripts/output_text/")
    time.sleep(0.5)
    audio.concat_audio_single_directory("scripts/ai/",outputPath="scripts/output_audio/output_"+ str(time.time())+".wav") # the finished audio file is saved

def personPlusAi():
    server.restart()
    # print("Server restarted.")

    sessionID = 1
    characterID = 1
    server.initialize()
    server.create_character("Avatar", "Avatar is a wise philosopher who understands the world in complex yet beautiful, meta-cognitive and cross-paradigmatic ways. He speaks with the eloquence of a great writer, weaving connections through networks of intricate ideas.")
    server.create_session("Contemplations on Entities", "The following is an enlightening conversation between you and Avatar about the nature of artificial and biological entities, on the substance of souls, individuality, agency, and connection.", "1")


    ####################
    utils.create_directory("recording/output/", False)
    utils.create_directory("recording/ai/")
    utils.create_directory("recording/user/")

    # loop condition flag
    convoFlag = True 

    while(convoFlag):

        myText = mic.startListen()
        print(myText)
        # print("Did you say "+MyText)
        # SpeakText(MyText)

        response = server.get_response(myText, sessionID, characterID,primPaths[0])
        # print(response["responseText"])
        # mic.speakText(response["responseText"])

        if(myText == "quit" or myText == None):
            convoFlag = False
            break

    # Save the audio files to the output directory
    time.sleep(0.5)
    audio.concat_audio_double_directory("recording/ai/", "recording/user/") # the finished audio file is saved
    # audio.cleanup("recording/ai/", "recording/user/") # delete the temporary files


if __name__ == "__main__":
    # print(f"Arguments count: {len(sys.argv)}")
    # for i, arg in enumerate(sys.argv):
    #     print(f"Argument {i:>6}: {arg}")
    # personPlusAi()
    dirname = os.path.dirname(__file__)
    script_input(dirname+"scripts/input/")