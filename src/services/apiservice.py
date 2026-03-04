from __future__ import annotations
import concurrent.futures

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from apis import DataDragon, LolWiki


class ApiService:
    def __init__(
            self
    ):
        # Parallelize initialization of separate network-bound APIs to speed up app startup.
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_dd = executor.submit(DataDragon)
            future_wiki = executor.submit(LolWiki)

            # Wait for both to complete
            self.data_dragon = future_dd.result()
            self.lol_wiki = future_wiki.result()
