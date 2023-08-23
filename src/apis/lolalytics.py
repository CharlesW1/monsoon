import requests

class LolAlytics:
    def __init__(self):
        self.url = "https://ax.lolalytics.com/tierlist/1/?lane=middle&patch=14&tier=emerald_plus&queue=450&region=all"
        self.__lolalytics_json = self._fetch_winrate_json()
        self.__winrates_by_key = self._process_winrate_data()

    def _fetch_winrate_json(self) -> dict:
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
        pass

    def _process_winrate_data(self) -> dict:
        """Process winrate json into dict of winrate models"""
        pass
    
    def fetch_winrate_by_champion_id(self, name) -> WinrateModel:
        """Finda a WinrateModel instance for a champion id"""
        pass

    