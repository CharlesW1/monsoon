import requests


class DataDragon:
    def __init__(self):
        self.url = "https://ddragon.leagueoflegends.com"
        # Reuse TCP connections for multiple requests to the same host
        self.session = requests.Session()
        self.latest_version = self._fetch_latest_version()
        self.champions = self._fetch_champions()
        # O(1) lookup map for champion data by their numeric key
        self.champions_by_id = {int(v['key']): v for v in self.champions['data'].values()}
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
        """O(1) lookup of champion data by ID"""
        return self.champions_by_id.get(champion_id)

    def fetch_icon_by_champion_id(self, champion_id):
        """Fetch champion icon using O(1) lookup and cached icons"""
        champion = self.fetch_by_champion_id(champion_id)
        if champion is None:
            raise Exception("Invalid champion id")

        champion_name = champion['id']

        if champion_name not in self.champion_icons:
            req = self.session.get(f"{self.url}/cdn/{self.latest_version}/img/champion/{champion_name}.png")
            if req.status_code != 200:
                raise Exception("Failed to get champion icon from DataDragon")
            self.champion_icons[champion_name] = req.content

        return self.champion_icons[champion_name]
