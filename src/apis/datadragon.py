import requests


class DataDragon:
    def __init__(self):
        self.url = "https://ddragon.leagueoflegends.com"
        # API client classes must use requests.Session() to enable TCP connection pooling
        self.session = requests.Session()
        self.latest_version = self._fetch_latest_version()
        self.champions = self._fetch_champions()
        # O(1) lookup mapping for champion data by their numeric key
        self.champions_by_id = {int(v["key"]): v for v in self.champions["data"].values()}
        self.champion_icons = dict()

    def _fetch_latest_version(self):
        req = self.session.get(f"{self.url}/api/versions.json")

        if req.status_code != 200:
            raise Exception("Failed to get latest version from DataDragon")

        if len(req.json()) == 0:
            raise Exception("Received empty versions list from DataDragon")

        return req.json()[0]

    def _fetch_champions(self):
        req = self.session.get(f"{self.url}/cdn/{self.latest_version}/data/en_US/champion.json")

        if req.status_code != 200:
            raise Exception("Failed to get champions from DataDragon")

        return req.json()

    def fetch_by_champion_id(self, champion_id):
        # Optimized to O(1) using pre-calculated mapping
        return self.champions_by_id.get(champion_id)

    def fetch_icon_by_champion_id(self, champion_id):
        # Optimized to O(1) using pre-calculated mapping
        champion_data = self.champions_by_id.get(champion_id)
        if champion_data is None:
            raise Exception("Invalid champion id")

        champion_name = champion_data["id"]

        if not champion_name in self.champion_icons:
            req = self.session.get(f"{self.url}/cdn/{self.latest_version}/img/champion/{champion_name}.png", stream=True)
            if req.status_code != 200:
                raise Exception("Failed to get champion icon from DataDragon")
            self.champion_icons[champion_name] = req.content

        return self.champion_icons[champion_name]
