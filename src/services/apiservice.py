from __future__ import annotations

from typing import TYPE_CHECKING
import concurrent.futures

if TYPE_CHECKING:
    pass

from apis import DataDragon, LolWiki


class ApiService:
    def __init__(
            self
    ):
        # Parallelize initialization of core services to reduce startup time
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_dd = executor.submit(DataDragon)
            future_lw = executor.submit(LolWiki)
            self.data_dragon = future_dd.result()
            self.lol_wiki = future_lw.result()
