from server_local.classes.character import Character
from .functions import nlp, audio, db, anim
# import ast
# from classes import character, context

class Params:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)    

def restart():
    db.clear()    

def initialize():
    db.initialize()


def animate_character(text,sessionID,characterID, primitivePath):
    """
    This function is used to animate a character based on the text input
    """
    # Fetch session data from DB
    sessionData = db.fetch_session_data(sessionID)
    
    # Generate response
    CharacterName = db.fetch_character_schema(characterID)["characterName"]
    print(sessionData)
    updatedHistory = sessionData["history"]+f"\n{CharacterName}:{text}\n"
    responseEmotion = nlp.get_emotion(text)
    # Update history
    db.update_session_data(sessionID, updatedHistory)
    
    # Generate wav
    wavPath = audio.generate_wav(text, "en-US-TonyNeural", responseEmotion,outputPath="/scripts/ai/ai_")
    
    # Execute animation
    anim.animate(wavPath, primitivePath)

    # audio.cleanup(wavPath, outputPath)

    # Format response
    responseData = {"responseText": text}

def get_response(promptText, sessionID, characterID, primitivePath):
    """
    This function is used to get a response from the server for a given prompt
    """

    params = Params()

    params.promptText = promptText
    params.sessionID = sessionID
    params.characterID = characterID
    
    # Fetch character schema from DB
    characterSchema = db.fetch_character_schema(params.characterID)
    
    # Fetch session data from DB
    sessionData = db.fetch_session_data(params.sessionID)
    
    # Generate response
    textResponse, updatedHistory = nlp.generate_response(params.promptText, characterSchema, sessionData)
    responseEmotion = nlp.get_emotion(textResponse)
    # Update history
    db.update_session_data(params.sessionID, updatedHistory)
    
    # Generate wav
    wavPath = audio.generate_wav(textResponse, "en-US-TonyNeural", responseEmotion)
    
    # Execute animation
    anim.animate(wavPath, primitivePath)

    # audio.cleanup(wavPath, outputPath)

    # Format response
    responseData = {"responseText": textResponse}
#     response = send_from_directory(directory='data', filename='audio.mp3')
#     response.data = responseData
    
    return responseData


def create_character(characterName, characterDescription):
    """
    This function is used to create a character by saving the character schema in the database
    """

    params = Params()

    params.characterName = characterName
    params.characterDescription = characterDescription
        
    # Create character schema
    characterSchema = {
        "characterName": params.characterName,
        "characterDescription": params.characterDescription,
#         "parameterValues": params.parameterValues
                    }
    
    # Save character schema in DB
    db.save_character_schema(characterSchema)
    
    # Format response
    responseDict = characterSchema
#     response.data = {
#         "characterID": characterSchema["characterID"],
#         "characterDescription": characterSchema["characterDescription"],
#         "parameterValues": characterSchema["parameterValues"]
#                     }
    
    return responseDict


def create_session(sessionName, sessionDescription, characterIDList):
    """
    This function is used to create a session by saving the session schema in the database
    """

    params = Params()

    params.sessionName = sessionName
    params.sessionDescription = sessionDescription
    params.characterIDList = characterIDList

    # Create session data
#     characterDescriptions = [dict(db.fetch_character_schema(characterID))["characterDescription"] for characterID in params.characterIDList]
    characterDescriptions = [db.fetch_character_schema(characterID)["characterDescription"] for characterID in params.characterIDList]
    for characterID in params.characterIDList:
        print(characterID)
        print(db.fetch_character_schema(characterID))
    sessionData = {
        "sessionName": params.sessionName,
        "sessionDescription": params.sessionDescription,
        "characterIDList": params.characterIDList,
        "initialHistory": params.sessionDescription + " " + " ".join(characterDescriptions)
                    }
    
    # Save character schema in DB
    db.save_session_data(sessionData)
    
    # Format response
    responseDict = sessionData
    
    return responseDict

def get_history(sessionID):
    return db.fetch_session_data(sessionID)["history"]