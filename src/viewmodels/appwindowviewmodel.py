from __future__ import annotations

import concurrent.futures
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.services import WorkerService, ApiService
    from models import DynamicBalanceModel

from constants import Monsoon, Workers
from models import ChampionSelectSessionModel
from utils import EventHandler, ResourceHelper

from PySide6 import QtCore, QtGui
from dependency_injector.wiring import Provide, inject


class AppWindowViewModel(object):
    @inject
    def __init__(
            self,
            worker_service: WorkerService = Provide["worker_service"],
            api_service: ApiService = Provide["api_service"]
    ):
        self.object_name = "appView"
        self.window_title = Monsoon.TITLE
        self.height = Monsoon.HEIGHT
        self.width = Monsoon.WIDTH
        self.wordmark_pixmap = QtGui.QPixmap()
        self.wordmark_pixmap.loadFromData(ResourceHelper.get_resource_bytes("resources/images/wordmark.png"))

        self._available_champion_dynamic_balances = []
        self._team_champion_dynamic_balances = []
        self._is_enabled = False

        self.property_changed = EventHandler()

        self.api_service = api_service
        # Persistent thread pool for data processing to avoid instantiation overhead in high-frequency events.
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        # Start worker threads
        lockfile_watcher_worker = worker_service.get(Workers.LOCKFILE_WATCHER)
        lockfile_watcher_worker.start()
        lcu_event_processor_worker = worker_service.get(Workers.LCU_EVENT_PROCESSOR)
        lcu_event_processor_worker.com.data_signal.connect(self.on_data)
        lcu_event_processor_worker.start()

    def _process_champion_id(self, champion_id: int) -> Optional[DynamicBalanceModel]:
        """Fetch champion name, balance changes, and icon for a single ID."""
        champion = self.api_service.data_dragon.fetch_by_champion_id(champion_id)
        if not champion:
            print(f"Warning: could not resolve champion for id {champion_id}")
            return None

        name = champion.get("name")
        if not name:
            return None

        balance = self.api_service.lol_wiki.fetch_dynamic_balance_by_champion_name(name)
        if not balance:
            print(f"Warning: lol_wiki returned no balance for '{name}'")
            return None

        # Fetch icon (uses O(1) cache if already retrieved)
        balance.champion_icon = self.api_service.data_dragon.fetch_icon_by_champion_id(champion_id)
        return balance

    @QtCore.Slot(ChampionSelectSessionModel)
    def on_data(self, data: ChampionSelectSessionModel):
        if data is None:
            print("Warning: received None data in on_data")
            return

        # Parallelize champion data processing to reduce LCU event handling latency.
        # This is especially impactful when icons for new champions need to be fetched over the network.
        # Note: While we process in parallel, we block here for all results to ensure the UI updates
        # atomically with consistent state from the LCU event.
        team_ids = data.team_champion_ids or []
        avail_ids = data.available_champion_ids or []

        # Map both sets of IDs to their processing futures
        team_futures = [self._executor.submit(self._process_champion_id, cid) for cid in team_ids]
        avail_futures = [self._executor.submit(self._process_champion_id, cid) for cid in avail_ids]

        # Use result retrieval that avoids multiple calls and lock acquisitions per future
        team_balances = []
        for f in concurrent.futures.as_completed(team_futures):
            res = f.result()
            if res:
                team_balances.append(res)

        avail_balances = []
        for f in concurrent.futures.as_completed(avail_futures):
            res = f.result()
            if res:
                avail_balances.append(res)

        if team_balances:
            # Sort balances to maintain stable UI order if required (as_completed is non-deterministic)
            # This ensures that as IDs arrive, their position in the UI is stable across updates.
            team_balances.sort(key=lambda b: team_ids.index(b.champion_id) if b.champion_id in team_ids else 0)
            self.team_champion_dynamic_balances = team_balances

        if avail_balances:
            avail_balances.sort(key=lambda b: avail_ids.index(b.champion_id) if b.champion_id in avail_ids else 0)
            self.available_champion_dynamic_balances = avail_balances

    @property
    def available_champion_dynamic_balances(self):
        return self._available_champion_dynamic_balances

    @available_champion_dynamic_balances.setter
    def available_champion_dynamic_balances(self, value):
        self._available_champion_dynamic_balances = value
        self.property_changed.invoke(self, None)

    @property
    def team_champion_dynamic_balances(self):
        return self._team_champion_dynamic_balances

    @team_champion_dynamic_balances.setter
    def team_champion_dynamic_balances(self, value):
        self._team_champion_dynamic_balances = value
        self.property_changed.invoke(self, None)

    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        self._is_enabled = value
        self.property_changed.invoke(self, None)
