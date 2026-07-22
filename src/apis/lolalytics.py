import requests
import json
import re
from bs4 import BeautifulSoup

# Index in data['objs'] after which champion-keyed dicts start appearing.
CHAMPION_DICT_SCAN_START = 265
# Index in data['objs'] after which per-champion winrate data begins.
WINRATE_SCAN_START = 1000


class LoLalytics:
    def __init__(self):
        self.url = "https://lolalytics.com/lol/tierlist/aram/?patch=14"
        # Reuse TCP connections
        self.session = requests.Session()
        self.__champs, self.__champsData = self._fetch_winrate_json()
        # Initial raw data processing
        self.__winrates_by_champ = self._process_winrate_data()
        # O(1) pre-formatted lookup map for all champion name variants
        self.__lookup_map = self._build_lookup_map()

        print(f"Processed winrates for {len(self.__winrates_by_champ)} champions from LoLalytics")
        # DEBUG: print processed winrates
        # for key, value in sorted(self.__winrates_by_champ.items()):
        #     print(f"- {key}: {value}")

    def _fetch_winrate_json(self) -> tuple[list, list]:
        """Fetch the json from lolalytics.com that contains ARAM win rates for each
        champion over that past 14 days from the emerald+ elo. 
        
        Notes: 
            I am not sure how elo is determined by the website, but the data tier
                by tier does seem to correlate with player skill. 
            14 days is used to ensure there is a stable number of games for accurate info

        Raises:
            Exception: Response not 200
            Exception: Failed to convert to dict
        
        Returns:
            dict: dict representation of the json returned
        """
        # fetch page containing tierlist data
        response = self.session.get(self.url)

        if response.status_code != 200:
            raise Exception("LoLalytics did not respond 200")

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            div = soup.find('div', class_='ml-auto text-right')
            script_tag = soup.find('script', {'type': 'qwik/json'})

            if not div or not script_tag:
                raise Exception
            
            # process div for avgWR (needed to parse the script json object dynamically)
            text = div.get_text(strip=True)
            match = re.search(r'(\d+\.\d+)', text)
            if match:
                avgWR = float(match.group(1))

            # process script_tag for the scripted json object
            json_text = script_tag.string.strip()  
            data = json.loads(json_text)
            self.__objs = data['objs']

            # grab the {champ : ?? id } dictionary
            for i, x in enumerate(self.__objs):
                if isinstance(x, dict) and i > CHAMPION_DICT_SCAN_START:
                    numChamps = len(list(x.keys()))
                    champs = list(x.keys())
                    break

            # find index of average wr info (marks begining of champ specific info)
            for i, x in enumerate(self.__objs[WINRATE_SCAN_START:]):
                # Data may be returned as int or float; ensure robust comparison
                if isinstance(x, (int, float)) and x == avgWR:
                    avgWRIndex = i + WINRATE_SCAN_START
                    break
            
            # organize champ data by champ (some info is randomly missing for each champ)
            champsData = [[]]
            i = avgWRIndex+2
            while len(champsData) < numChamps + 1:
                champsData[-1].append(self.__objs[i])
                if isinstance(self.__objs[i], dict):
                    champsData.append([])
                i+=1

            return champs, champsData
        except Exception as e:
            raise Exception("Failed to grab JSON from LoLalytics") from e

    def _process_winrate_data(self) -> dict:
        """Process winrate json into dict of champion -> rank, winrate pair using O(1) direct Qwik JSON lookup.

        The obfuscated winrate is mapped directly in the Qwik JSON `objs` list, and each champion's metadata
        contains a base-36 index reference 'wr' pointing to its exact winrate value. This eliminates both the
        heuristic guess-and-fallback logic and any parallel fallback network requests.
        """
        champs = self.__champs
        champsData = self.__champsData
        winrates = {}

        for champ, data in zip(champs, champsData):
            if not data:
                continue
            meta = data[-1]
            if isinstance(meta, dict) and 'wr' in meta:
                # Convert the base-36 reference index to an integer to perform O(1) lookup in objs
                try:
                    wr_idx = int(meta['wr'], 36)
                    winrates[champ] = self.__objs[wr_idx]
                except (ValueError, TypeError, IndexError):
                    winrates[champ] = -1
            else:
                winrates[champ] = -1

        wrSorted = sorted([(-wr, champ) for champ, wr in winrates.items()])

        for rank, x in enumerate(wrSorted, 1):
            winrates[x[1]] = (rank, winrates[x[1]])
        return winrates

    @staticmethod
    def _format_rank_winrate(rank, winrate) -> str:
        return "Rank: {}\nWinrate: {}".format(rank, winrate)

    def _normalize_name(self, name: str) -> str:
        """Standardize champion name for consistent lookups"""
        return name.strip().lower().replace(" ", "").replace("\'", "").replace(".", "")

    def _build_lookup_map(self) -> dict:
        """Pre-format and index winrate data by both original and normalized names"""
        lookup = {}
        for name, data in self.__winrates_by_champ.items():
            formatted = self._format_rank_winrate(*data)
            # Store by original name
            lookup[name] = formatted
            # Store by normalized name for faster fallback lookups
            normalized = self._normalize_name(name)
            if normalized not in lookup:
                lookup[normalized] = formatted
        return lookup

    def fetch_winrate_by_champion(self, champ) -> str:
        """Return formated rank, winrate data for a champion using O(1) lookup map"""
        # 1. Direct O(1) lookup (exact or previously normalized name)
        if champ in self.__lookup_map:
            return self.__lookup_map[champ]

        # 2. Try lookup with current name normalized
        normalized = self._normalize_name(champ)
        if normalized in self.__lookup_map:
            return self.__lookup_map[normalized]

        # 3. Final fallback: first part of name (e.g. "Renata Glasc" -> "renata")
        first_part = champ.split()[0].strip().lower()
        if first_part in self.__lookup_map:
            return self.__lookup_map[first_part]

        print(f"Warning: could not find winrate for champion '{champ}'")
        return ""