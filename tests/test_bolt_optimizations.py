from src.apis import DataDragon, LolWiki

class TestApisBolt:
    def test_lolwiki_id_lookup(self):
        api = LolWiki()
        # Sona's ID is 37
        balance = api.fetch_dynamic_balance_by_champion_id(37)
        assert balance is not None
        assert balance.champion_name == 'Sona'

    def test_datadragon_icon_cache_by_id(self):
        api = DataDragon()
        # Fetch icon for Sona (37)
        icon_data = api.fetch_icon_by_champion_id(37)
        assert icon_data is not None
        # Verify it is in cache with ID as key
        assert 37 in api.champion_icons
        assert api.champion_icons[37] == icon_data
