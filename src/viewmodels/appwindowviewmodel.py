from __future__ import annotations

import concurrent.futures
from typing import TYPE_CHECKING

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
        # Persistent ThreadPoolExecutor for parallel champion data and icon fetching.
        # This avoid the overhead of thread creation/destruction on every session update.
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

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
        # Start worker threads
        lockfile_watcher_worker = worker_service.get(Workers.LOCKFILE_WATCHER)
        lockfile_watcher_worker.start()
        lcu_event_processor_worker = worker_service.get(Workers.LCU_EVENT_PROCESSOR)
        lcu_event_processor_worker.com.data_signal.connect(self.on_data)
        lcu_event_processor_worker.start()

    def _process_champion_balance(self, champion_id: int, source: str) -> DynamicBalanceModel | None:
        """Fetch champion data, balance and icon for a single champion ID.
        This is separated to allow parallel processing.
        """
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
        # This call is network-bound if the icon is not already cached
        balance.champion_icon = self.api_service.data_dragon.fetch_icon_by_champion_id(champion_id)
        return balance

    @QtCore.Slot(ChampionSelectSessionModel)
    def on_data(self, data: ChampionSelectSessionModel):
        if data is None:
            print("Warning: received None data in on_data")
            return

        team_ids = data.team_champion_ids or []
        avail_ids = data.available_champion_ids or []
        all_ids = team_ids + avail_ids

        if not all_ids:
            return

        # Parallelize champion data and icon fetching to improve UI responsiveness,
        # especially when multiple new icons need to be fetched over the network.
        # We use a persistent executor to minimize overhead during frequent LCU updates.

        # Submit all tasks and wait for results while preserving order.
        # This blocks the LCU worker thread but not the main UI thread.
        futures = [
            self._executor.submit(
                self._process_champion_balance,
                champion_id,
                "team" if i < len(team_ids) else "available"
            )
            for i, champion_id in enumerate(all_ids)
        ]
        results = [f.result() for f in futures]

        team_champion_dynamic_balances = [b for b in results[:len(team_ids)] if b]
        available_champion_dynamic_balances = [b for b in results[len(team_ids):] if b]

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
