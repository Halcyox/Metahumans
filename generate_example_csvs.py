import sys, time, os
import pandas as pd
import typing
import random, logging
from dataclasses import dataclass
from dataclass_csv import DataclassWriter

from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem

import xragents
from xragents import setting, scene
from xragents import audio, utils, cast, simulator
from xragents.types import Character

def main():
    # example_scene = scene.Scene(
    #     id=random.randint(0, 10),
    #     name="Avatar 3: The Search for More Money",
    #     description="James Camerons' newest hit single, Avatar 3, unrelated in any way to the previous instantiations because GPT-4 has no persistence or mutability!",
    #     characters=[cast.Avatar, cast.Avatar2, cast.KillerOfWorlds],
    #     text_only=True,
    # )

    example_scene = scene.Scene(
        id=random.randint(0, 10),
        name="Conversation between Stewey from Family Guy and Average Redditor",
        description="The following is an entertaining convo between Stewey from Family Guy and The Average Redditor about chocolate milk vs. hot chocolate.",
        characters=[cast.AverageRedditor, cast.Stewey],
        text_only=True,
    )

    with open("example_scene.csv", "w") as f:
        w = DataclassWriter(f, [example_scene], scene.Scene)
        w.write()

if __name__ == "__main__":
    main()