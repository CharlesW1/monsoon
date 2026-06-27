from enum import Enum


class Monsoon:
    TITLE = "Monsoon"
    VERSION = "2.2.12"
    # Thread pool worker count for parallel processing
    EXECUTOR_WORKERS = 10
    AUTHOR = "ChOwOs#Snerp"
    LEGAL = "Monsoon isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone " \
            "officially involved in producing or managing Riot Games properties. Riot Games, and all associated " \
            "properties are trademarks or registered trademarks of Riot Games, Inc. "
    WIDTH = 1280
    HEIGHT = 720


class Workers(Enum):
    LOCKFILE_WATCHER = 0
    LCU_EVENT_PROCESSOR = 1


class SettingsSchema:
    DEFAULT = ("", "")
