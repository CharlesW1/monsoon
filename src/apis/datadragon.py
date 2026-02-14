import requests


class DataDragon:
    def __init__(self):
        self.url = "https://ddragon.leagueoflegends.com"
        self.session = requests.Session()  # Use session for connection pooling
        self.latest_version = self._fetch_latest_version()
        self.champions = self._fetch_champions()
        # Pre-calculate mapping for O(1) lookups by numeric ID
        self.champions_by_id = {int(v['key']): v for v in self.champions['data'].values()}
        self.champion_icons = dict()

    def _fetch_latest_version(self):
        # Optimization: use connection pooling for network calls
        req = self.session.get(f"{self.url}/api/versions.json")

        if req.status_code != 200:
            raise Exception("Failed to get latest version from DataDragon")

        if len(req.json()) == 0:
            raise Exception("Received empty versions list from DataDragon")

        return req.json()[0]

    def _fetch_champions(self):
        # Optimization: use connection pooling for network calls
        req = self.session.get(f"{self.url}/cdn/{self.latest_version}/data/en_US/champion.json")

        if req.status_code != 200:
            raise Exception("Failed to get champions from DataDragon")

        return req.json()

    def fetch_by_champion_id(self, champion_id):
        # Optimization: O(1) lookup instead of O(N) linear search
        return self.champions_by_id.get(champion_id)

    def fetch_icon_by_champion_id(self, champion_id):
        # Optimization: O(1) lookup to find champion name for icon
        champion_data = self.champions_by_id.get(champion_id)
        if champion_data is None:
            raise Exception("Invalid champion id")

        champion_name = champion_data['id']

        if not champion_name in self.champion_icons:
            # Optimization: use connection pooling for network calls
            req = self.session.get(f"{self.url}/cdn/{self.latest_version}/img/champion/{champion_name}.png", stream=True)
            if req.status_code != 200:
                raise Exception("Failed to get champion icon from DataDragon")
            self.champion_icons[champion_name] = req.content

        return self.champion_icons[champion_name]
