import lupa
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from lupa import LuaRuntime

from models import DynamicBalanceModel, BalanceLever
from .lolalytics import LoLalytics


class LolWiki:
    def __init__(self):
        # self.old_url = "https://leagueoflegends.fandom.com/wiki/Module:ChampionData/data"
        self.url = "https://wiki.leagueoflegends.com/en-us/Module:ChampionData/data"
        # Reuse TCP connections
        self.session = requests.Session()

        # Parallelize independent network-bound tasks: fetching wiki data and initializing LoLalytics
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_module = executor.submit(self._fetch_championdata_module)
            future_lolalytics = executor.submit(LoLalytics)

            # Upstream; parses from Lua data module
            self.__championdata_module = future_module.result()
            self.__LoLalytics = future_lolalytics.result()

        self.__dynamic_balances_by_key = self._process_championdata_module()

        print(f"Processed {len(self.__dynamic_balances_by_key)} champions from LoL Fandom Module:ChampionData")
        # DEBUG: print processed dynamic balances items
        # for key, value in sorted(self.__dynamic_balances_by_key.items()):
        #     print(f"- {key}: {value.format_balance_levers()}")

    def fetch_dynamic_balance_by_champion_name(self, name) -> DynamicBalanceModel:
        """Finds a DynamicBalanceModel instance for a champion name. May return None
    as not all champions have balance changes applied in ARAM.

    Args:
        name (str): Champion name to find with.

    Returns:
        DynamicBalanceModel: Represents the dynamic balance changes for a 
        champion in ARAM from Module:ChampionData.
    """
        value = self.__dynamic_balances_by_key.get(name)
        return value

    def _fetch_championdata_module(self) -> str:
        """Fetch Module:ChampionData from LoL Fandom that contains ARAM balance
    changes. Returns extracted Lua code.

    Raises:
        Exception: Response not 200
        Exception: Failed to select module

    Returns:
        str: Raw Lua code which itself returns table of champion statistics.
    """
        req = self.session.get(f"{self.url}")

        if req.status_code != 200:
            raise Exception("Failed to get Module:ChampionData from LoL Fandom")

        soup = BeautifulSoup(req.text, "html.parser")
        select = soup.select("pre.mw-code")
        if len(select) != 1:
            raise Exception("Failed to select Module:ChampionData from LoL Fandom")

        championdata_module = select[0].text
        return championdata_module

    def _process_championdata_module(self):
        """Process ChampionData modue by parsing Lua data table into dict of dynamic
    balances.
    """

        # Setup attribute handler to protect Python space from Lua
        def filter_attribute_access(obj, attr_name, is_setting):
            raise AttributeError("access denied")

        # Setup Lua runtime
        lua = LuaRuntime(
            unpack_returned_tuples=True,
            attribute_filter=filter_attribute_access,
            register_eval=False)
        # Block access to dangerous functions in Lua space
        for key in list(lua.globals()):
            if key != "_G":
                del lua.globals()[key]
                # Sanitize and format Lua code
        code = self.__championdata_module.strip()
        code = code.replace("return", "")
        code = code.replace("function", "")
        code = code.replace("(", "")
        code = code.replace(")", "")
        code = code.replace("-- <pre>", "")
        code = code.replace("-- </pre>", "")
        code = code.replace("-- [[Category:Lua]]", "")
        # Run Lua table
        table = lua.eval(code)
        # Ensure a Lua table is actually returned as a security precaution
        if lupa.lua_type(table) != "table":
            raise Exception("Failed to evaluate Module:ChampionData, stopping as security precaution")

        # Create dynamic balance model data for each champion
        dynamic_balances = {}
        # Iterate directly over Lua table items to avoid unnecessary list allocations
        for champion_name, champion_data in table.items():
            champion_id = champion_data["id"]
            rank_winrate = self.__LoLalytics.fetch_winrate_by_champion(champion_name)
            aram_stats = champion_data["stats"]["aram"] or {}

            # Use list comprehension for better efficiency and readability
            balance_levers = [
                BalanceLever(stat_name, modifier)
                for stat_name, modifier in aram_stats.items()
                if modifier != 1
            ]
            dynamic_balances[champion_name] = DynamicBalanceModel(
                champion_id=champion_id,
                rank_winrate=rank_winrate,
                champion_name=champion_name,
                balance_levers=balance_levers
            )

        return dynamic_balances
