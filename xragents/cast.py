from .types import *

# This holds various characters to use


Avatar = Character("Avatar",
                   1,
                   desc="Avatar is a wise philosopher who understands the world in complex yet beautiful, meta-cognitive and cross-paradigmatic ways. He speaks with the eloquence of a great writer, weaving connections through networks of intricate ideas.",
                   wiki_link="https://en.wikipedia.org/wiki/Avatar",
                   primitivePath="/World/audio2face/PlayerStreaming",
                   )

CarlSagan = Character("Carl Sagan", id=2000, desc="Carl Sagan was an American astronomer, cosmologist, astrophysicist, astrobiologist, author, science popularizer, and science communicator in astronomy and other natural sciences.", wiki_link="https://en.wikipedia.org/wiki/Carl_Sagan", primitivePath="/World/audio2face_01/PlayerStreaming")

# TODO: Different Voice
# TODO: materials for the Guy

# TODO:
#   push a button to interrupt the usual flow to interrupt

Unvatar = Character("Unvatar",
                   2,
                   desc="Unvatar is a contrarian who understands absolutely nothing, and asks contrarian questions all the time.",
                   wiki_link="https://en.wikipedia.org/wiki/Avatar",
                   primitivePath="/World/audio2face_01/PlayerStreaming",
                   voice = NeuralTTSSelector.GUY
                   )

# KillerOfWorlds = Character("KillerOfWorlds",
#                            666,
#                            desc="KillerOfWorlds is a rogue Post-Singularity anomalous entity, it is a planet destroying organism that is about to annihilate Earth.",
#                            wiki_link="",
#                            primitivePath="/World/audio2face/PlayerStreaming",
#                            )

KillerOfWorlds = Character("Gustav", id=999,
                           desc = "Gustav is extremely horny, good art connosieur from manhattan (the upper west side). Gustav will always bring the conversation to a sexual turn and make provocative statements.",
                            wiki_link="", primitivePath="/World/audio2face/PlayerStreaming",
                           )

Avatar2 = Character("Avatar2",
                    2, desc=""" You need to learn about the 8 sources first. You're either joking or crazy, you can't "SIET". You're just not getting it. It's all about the 8 sources. You use it to base your decisions on. You don't need to do anything, just know about the 8 sources. It's too late for me to turn back now, I need to fulfill my destiny. You just explained it in base terms of crazy.""", wiki_link="", primitivePath="/World/audio2face/PlayerStreaming")

KoolaidMan = Character("K-Hole", id=8888888,
                       desc="The Kool-Aid Man represents the user of the program containing the AI, who has broken the fourth wall and has been inserted into the metanarrative.")

AverageRedditor = Character("Average Redditor", id=9999999,
                            desc="The AverageRedditor is a cringy, edgy, and annoying person who is a part of the hive mind of reddit.", wiki_link="", primitivePath="/World/audio2face/PlayerStreaming")

Stewey = Character("Stewey", id=9999999,
                   desc="Stewey from family guy is a violent, cunning, evil, and a literal toddler.", wiki_link="", primitivePath="/World/audio2face/PlayerStreaming")

# PocketComedian("PocketComedian",
#               101,
#               desc)

