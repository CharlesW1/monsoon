from __future__ import annotations

import concurrent.futures
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services import WorkerService, ApiService

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
        # Persistent executor for parallel champion processing
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        # Start worker threads
        lockfile_watcher_worker = worker_service.get(Workers.LOCKFILE_WATCHER)
        lockfile_watcher_worker.start()
        lcu_event_processor_worker = worker_service.get(Workers.LCU_EVENT_PROCESSOR)
        lcu_event_processor_worker.com.data_signal.connect(self.on_data)
        lcu_event_processor_worker.start()

    def __del__(self):
        # Ensure the executor is shut down when the viewmodel is destroyed
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)

    def _fetch_champion_balance(self, champion_id: int, source: str):
        """Helper to fetch champion data, balance, and icon for a single champion ID"""
        champion = self.api_service.data_dragon.fetch_by_champion_id(champion_id)
        if champion is None:
            print(f"Warning: could not resolve champion for id {champion_id} ({source})")
            return None
        champ_name = champion.get("name")
        if not champ_name:
            print(f"Warning: champion data missing name for id {champion_id} ({source})")
            return None
        balance = self.api_service.lol_wiki.fetch_dynamic_balance_by_champion_name(champ_name)
        if balance is None:
            print(f"Warning: lol_wiki returned no balance for '{champ_name}' ({source})")
            return None
        balance.champion_icon = self.api_service.data_dragon.fetch_icon_by_champion_id(champion_id)
        return balance

    @QtCore.Slot(ChampionSelectSessionModel)
    def on_data(self, data: ChampionSelectSessionModel):
        if data is None:
            print("Warning: received None data in on_data")
            return

        team_ids = data.team_champion_ids or []
        avail_ids = data.available_champion_ids or []

        # Use separate lists of futures to ensure results are correctly categorized
        # even if some fetches fail (return None).
        team_futures = [self._executor.submit(self._fetch_champion_balance, id, "team") for id in team_ids]
        avail_futures = [self._executor.submit(self._fetch_champion_balance, id, "available") for id in avail_ids]

        # Collect and filter results for each group independently
        team_champion_dynamic_balances = [res for f in team_futures if (res := f.result()) is not None]
        available_champion_dynamic_balances = [res for f in avail_futures if (res := f.result()) is not None]

        if team_champion_dynamic_balances:
            self.team_champion_dynamic_balances = team_champion_dynamic_balances
        if available_champion_dynamic_balances:
            self.available_champion_dynamic_balances = available_champion_dynamic_balances

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
