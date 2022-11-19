"""Module providing API access to winrate data"""
import requests
from bs4 import BeautifulSoup
from model import WinRateModel


class LeagueOfGraphs:
    """Class for interacting with win rate data"""

    def __init__(self) -> None:
        self.url = "https://leagueofgraphs.com"
        self.__cache = self._fetch_aram_winrate()
        self.__winrate_by_key = self._process_cache()

    def _fetch_aram_winrate(self):
        """Fetch and parse ARAM win rate data from League of Graphs website

        Raises:
            Exception: Failed to get a valid request
            Exception: Failed to find any changes from table

        Returns:
            ResultSet[tag]: Set of 'tr' tags that are parsed from HTML table.
        """
        req = requests.get(
            f"{self.url}/champions/builds/aram",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=60,
        )

        if req.status_code != 200:
            raise Exception("Failed to get ARAM win rate from League of Graphs")

        soup = BeautifulSoup(req.text, "html.parser")
        rows = soup.select("table.with_sortable_column tr")

        if len(rows) == 0:
            raise Exception("Failed to parse table from Lol Fandom; No rows found")

        return rows

    def _process_cache(self):
        """Process cache into a dictionary of balance changes using name as key."""
        wr = {}
        for tr in self.__cache[1:]:
            # there are some add and extra header rows
            if not (not tr.get("class") and len(tr.contents) == 15):
                continue
            champion_name = tr.contents[3].text.strip()
            wr[champion_name] = WinRateModel(
                champion_name=tr.contents[3].text.strip(),
                win_rate=round(
                    float(tr.select("progressbar")[1].get("data-value").strip()) * 100,
                    2,
                ),
            )
        return wr

    def fetch_winrate_by_champion_name(self, name) -> WinRateModel:
        """Finds a WinRateModel instance for a champion name. May return None in some edge case.

        Args:
            name (str): Champion name to find with.

        Returns:
            WinRateModel: Represents the win rate for a champion in ARAM over the past two days
        """
        return self.__winrate_by_key.get(name)
