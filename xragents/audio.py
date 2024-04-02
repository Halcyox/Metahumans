import collections
import os
import azure.cognitiveservices.speech as speechsdk
import pydub
from pydub import AudioSegment
import time
from pathlib import Path
import io
from dataclasses import dataclass

import typing
import speech_recognition as sr
import pyttsx3

import wave
import pyaudio
import soundfile as sf
import sys
import re
import librosa



def generate_wav(text, speaker, lang=None,outputPath=None):
    print(f"Trying to write to {outputPath}")
    """Generates a wav file from text using the Azure Cognitive Services Speech SDK."""
    if outputPath is None:
        outputPath = "recording/ai/ai_bad_fixme"
    #TODO:API TOKEN
    speech_config = speechsdk.SpeechConfig(subscription="bfc08e214f6c48cebcde668a433196d3", region="eastus")
    # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    wavname =  f"{int(time.time())}.wav" # the path of the current audio file
    wavPath = f"{outputPath}/{wavname}"#  os.path.join(outputPath,wavname)
    Path(outputPath).mkdir(parents=True, exist_ok=True)
    print(f"{wavPath} is the final destination")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=wavPath)

    # Set either the `SpeechSynthesisVoiceName` or `SpeechSynthesisLanguage`.
    speech_config.speech_synthesis_language = "en-US"
    speech_config.speech_synthesis_voice_name = speaker

    ssml_string = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US' xmlns:mstts='http://www.w3.org/2001/mstts'>
        <voice name='{speaker}'>
            <mstts:express-as type='angry'>
                {text}
            </mstts:express-as>
        </voice>
    </speak>
    """

    # Creates a speech synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    # synthesizer.speak_text(text)
    synthesizer.speak_ssml(ssml_string)

    return wavPath

from . import anim

def play_wav_files(attempt_number, base_path="scripts/recorded_show/", animator_function=None):
    """
    This will play all the WAV files in the attempt folder for the given attempt number.
    """
    # print current system path
    print(f"Current system path: {os.getcwd()}")

    pattern = re.compile(f"^Attempt {attempt_number}(\\b|[^\\\\/]*)")

    folders = next(os.walk(base_path))[1]
    attempt_folder = next((folder for folder in folders if pattern.match(folder)), None)

    if attempt_folder:
        attempt_path = os.path.join(base_path, attempt_folder)
        wav_files = sorted([f for f in os.listdir(attempt_path) if f.endswith('.wav')],
                           key=lambda x: int(re.search(r"(\d+)", x).group()))
        try: 
            for wav in wav_files:
                file_path = os.path.join(attempt_path, wav)
                print(f"Attempting to play: {file_path}")
                # Load the audio file with librosa
                data, samplerate = librosa.load(file_path, sr=None)  # Use the native sampling rate
                # Write the data to a temporary file
                temp_file = 'temp.wav'
                sf.write(temp_file, data, samplerate)

                # Now use pyaudio to play the temporary file
                wf = wave.open(temp_file, 'rb')
                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True)
                
                # If an animator function is provided, call it with the wav path
                # if animator_function:
                #     animator_function(file_path, "/World/audio2face/PlayerStreaming")  # You need to define primitive_path somewhere
                anim.animate(temp_file, "/World/audio2face/PlayerStreaming")

                # data = wf.readframes(1024)
                # while data:
                #     stream.write(data)
                #     data = wf.readframes(1024)

                # Make sure to close the stream and the file before deleting the temp file
                stream.stop_stream()
                stream.close()
                wf.close()  # Close the Wave_read object
                p.terminate()

                try:
                    os.remove(temp_file)  # Delete the temporary file
                except PermissionError as e:
                    print(f"Error removing temp file: {e}")

                time.sleep(2)  # Wait for 2 seconds between each file
        except KeyboardInterrupt:
            print("\nPlayback interrupted by user.")
            # Add any necessary cleanup here, like stopping streams, closing files, etc.
            if stream:
                stream.stop_stream()
                stream.close()
            if p:
                p.terminate()
            print("Playback stopped.")

    else:
        print(f"No attempt folder found for number: {attempt_number}")



# from elevenlabs import generate, play, save, set_api_key

# set_api_key("9cecaa41213d3b3a26d36a02f79cac9a")

# def generate_wav(text, speaker, lang=None, outputPath=None):
#     speaker = "Bella"
#     """Generates a wav file from text using the Eleven Labs API."""
#     if outputPath is None:
#         outputPath = "recording/ai/ai_bad_fixme"

#     audio = generate(text, voice=speaker)  # generate the audio

#     # Save the audio as an MP3 file first
#     mp3_name = f"{int(time.time())}.mp3"
#     mp3_path = f"{outputPath}/{mp3_name}"
#     Path(outputPath).mkdir(parents=True, exist_ok=True)
#     print(f"Trying to write to {mp3_path}")
#     save(audio, mp3_path)
#     print(f"Saved to {mp3_path}")

#     # Wait until the MP3 file is generated
#     while not os.path.exists(mp3_path):
#         time.sleep(1)

#     # Convert the MP3 to WAV with the desired properties
#     wav_name = f"{int(time.time())}.wav"
#     wav_path = f"{outputPath}/{wav_name}"
#     print(f"Trying to write to {wav_path}")
#     convert_to_wav(mp3_path, wav_path)

#     # Remove the temporary MP3 file (optional)
#     os.remove(mp3_path)

#     print(f"{wav_path} is the final destination")
#     return wav_path

def convert_to_wav(input_file_path, output_file_path, sample_rate=16000, channels=1):
    # Load the MP3 audio file using pydub
    print(f"Converting {input_file_path} to {output_file_path}")
    audio = AudioSegment.from_file(input_file_path, format="mp3")

    # Set the sample width and frame rate to match the requirements
    audio = audio.set_frame_rate(sample_rate).set_channels(channels).set_sample_width(2)

    print(f"Exporting to {output_file_path}")
    # Export the audio as WAV with wait=True to ensure file writing completion
    audio.export(output_file_path, format='wav', parameters=['-ac', str(channels)], wait=True)

def cleanup(wavPath, outputPath):
    """Deletes the temporary files in the wavPath and outputPath directories."""
    for f1,f2 in zip(os.listdir(wavPath), os.listdir(outputPath)):
        os.remove(wavPath + f1)
        os.remove(outputPath + f2)

def concat_audio_double_directory(aiPath, humanPath, outputPath=None):
    """Concatenates the audio files in the aiPath and humanPath directories into a single file."""
    print("Concatenating audio files...")
    aiPaths = [Path(aiPath) / f for f in os.listdir(aiPath) if f.endswith(".wav")]
    humanPaths = [Path(humanPath) / f for f in os.listdir(humanPath) if f.endswith(".wav")]
    # Concatenate the audio files, starting with the human Paths, alternating with the ai paths.
    audio = AudioSegment.empty()
    for i in range(len(humanPaths)-1):
        audio += AudioSegment.from_file(humanPaths[i])
        audio += AudioSegment.from_file(aiPaths[i])

    if outputPath is None: # default output path
        outputPath = "recording/output/output_" + str(time.time()) + ".wav"
    audio.export(outputPath, format="wav")

    print("Concatenated audio files to " + outputPath)
    return audio

def concat_audio_single_directory(path,outputPath=None):
    """Concatenates the audio files in the path directory into a single file."""
    print("Concatenating audio files...")
    paths = [Path(path) / f for f in os.listdir(path) if f.endswith(".wav")]
    # Concatenate the audio files, starting with the human Paths, alternating with the ai paths.
    audio = AudioSegment.empty()
    for i in range(len(paths)):
        time.sleep(0.1)
        audio += AudioSegment.from_file(paths[i])

    if outputPath is None: # default output path
        outputPath = "recording/output/output_" + str(time.time()) + ".wav"
    audio.export(outputPath, format="wav")

    print("Concatenated audio files to " + outputPath)
    return audio


# --------------------------------------------------------
# MICROPHONE INITIALIZATION
# --------------------------------------------------------

r = sr.Recognizer()
raw_source = sr.Microphone()
_calibrated_source = None
def calibrate():
    global _calibrated_source
    if _calibrated_source is None:
        _calibrated_source = raw_source.__enter__()
        print("Please be quiet while I calibrate for ambient noise...",)
        # wait for a second to let the recognizer
        # adjust the energy threshold based on
        # the surrounding noise level
        r.adjust_for_ambient_noise(_calibrated_source, duration=2)
        print("done initializing microphone!")
    return _calibrated_source

@dataclass
class ListenRecord:
    """Transcript of having listened to user input.

    :param file_handle:
      An open file object containing the raw audio data.
    :param path:
      A path where file_handle is stored.
    :param spoken_content:
      The text that was spoken by the user."""
    file_handle: typing.BinaryIO
    path: Path
    spoken_content: str

    def __str__(self):
        return self.spoken_content

def listen_until_quiet_again() -> ListenRecord:
    """This listens to one chunk of user input and stores in a file, then returns it."""
    try:
        obj = calibrate()
        print("Listening...") # The microphone is now listening for input

        audio2 = r.listen(obj, timeout=5 )

        # save the audio file to a folder in ./recording/ with the name being timestamped
        fileName = "recording/user/" + "Convo_" + str(time.time()) + ".wav"
        f = open(fileName, "wb")
        f.write(audio2.get_wav_data())
        f.seek(0)
        # Using google to recognize audio
        # TODO, replace with whisper
        MyText = r.recognize_google(audio2)
        MyText = MyText.lower()

        return ListenRecord(file_handle=f, spoken_content=MyText, path=Path(fileName))

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        raise e