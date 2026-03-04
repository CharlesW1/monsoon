import requests
import json
import re
import concurrent.futures
import logging
from bs4 import BeautifulSoup


class LoLalytics:
    def __init__(self):
        self.url = "https://lolalytics.com/lol/tierlist/aram/?patch=14"
        self.champ_url = "https://lolalytics.com/lol/{}/aram/build/?patch=14"
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

    # ...existing code... (retry helper intentionally removed to keep network calls simple)

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

        print(response.status_code)

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

            # grab the {champ : ?? id } dictionary
            for i, x in enumerate(data['objs']):
                if isinstance(x, dict) and i > 265:
                    numChamps = len(list(x.keys()))
                    champs = list(x.keys())
                    break
            
            # find index of average wr info (marks begining of champ specific info)
            for i, x in enumerate(data['objs'][1000:]):
                if isinstance(x, float) and x == avgWR:
                    avgWRIndex = i + 1000
                    break
            
            # organize champ data by champ (some info is randomly missing for each champ)
            champsData = [[]]
            i = avgWRIndex+2
            while len(champsData) < numChamps + 1:
                champsData[-1].append(data['objs'][i])
                if isinstance(data['objs'][i], dict):
                    champsData.append([])
                i+=1

            return champs, champsData
        except:
            raise Exception("Failed to grab JSON from LoLalytics")

    def _fetch_winrate_for_champ(self, champ) -> float:
        """Visit champion page directly and grab winrate info"""
        print(f"Fetching winrate for missing champion {champ} from LoLalytics")
        response = self.session.get(self.champ_url.format(champ))

        print(response.status_code)

        if response.status_code != 200:
            raise Exception("LoLalytics did not respond 200")

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            # Find the specific <p> tag with the given class
            p_tag = soup.find('p', class_='lolx-links px-2 text-justify text-[14px] leading-normal text-white sm:px-0')

            # Use regex to find the float before the % symbol
            match = re.search(r'(\d+\.?\d*)%', p_tag.get_text())
            if match:
                return float(match.group(1))
            
            return -1
        except:
            raise Exception("Failed to find win rate for {}".format(champ))

        


    def _process_winrate_data(self) -> dict:
        """Process winrate json into dict of cid -> rank, winrate pair"""
        champs = self.__champs
        champsData = self.__champsData
        winrates = {}
        wrById = {}
        for champ, data in zip(champs, champsData):
            '''data list is how lolalytics represents the winrate data.
            It is obfuscated, but is a list of attributes in this order (all values not always present):
                [rank, winrate, wr delta, pick rate, games, some id dict]
            # one reason is that they don't show the same wr twice so one champion will be missing
            '''

            if len(data) < 1:
                continue
            # first slot is wr as decimal
            if isinstance(data[0], (int, float)) and 38 < data[0] and data[0] < 67:
                winrates[champ] = data[0]
                wrById[data[-1]['wr']] = (data[0], champ)
                continue

            if len(data) < 2:
                continue

            # second slot is wr as decimal
            if isinstance(data[1], (int, float)) and 38 < data[1] and data[1] < 67:
                winrates[champ] = data[1]
                wrById[data[-1]['wr']] = (data[1], champ)
                continue

            # wr happens to be int first slot (check next slot is delta/pr)
            if (isinstance(data[0], int) and 38 < data[0] and data[0] < 67 and
                isinstance(data[1], float) and data[1] < 10):
                winrates[champ] = data[0]
                wrById[data[-1]['wr']] = (data[0], champ)
                continue

        # fill in guessed wr
        missingInfo = set()
        for champ, data in zip(champs, champsData):
            if champ in winrates:
                continue
            if data[-1]['wr'] in wrById:
                winrates[champ] = wrById[data[-1]['wr']][0]
                continue
            missingInfo.add(champ)

        # remaining champs seem to have integer wr that is just missing
        # fetch directly from their champ page in parallel
        if missingInfo:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Map champion names to future objects
                future_to_champ = {executor.submit(self._fetch_winrate_for_champ, champ): champ for champ in missingInfo}
                for future in concurrent.futures.as_completed(future_to_champ):
                    champ = future_to_champ[future]
                    try:
                        winrates[champ] = future.result()
                    except Exception as exc:
                        logging.error(f'{champ} generated an exception: {exc}')
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

if __name__ == "__main__":
    api = LoLalytics()