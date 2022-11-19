"""Module providing the data class for win rate data"""
from dataclasses import dataclass


@dataclass
class WinRateModel:
    """Data class for caching ARAM win rate of a champion from League of Graphs"""

    champion_name: str
    win_rate: float

    def format(self):
        """Displays champion name followed by win rate"""
        return f"{self.champion_name} {self.win_rate}"

    def format_minimal(self):
        "Displays only win rate"
        return f"{self.win_rate}"
