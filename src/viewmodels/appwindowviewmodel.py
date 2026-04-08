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
        # Persistent executor for parallel champion data/icon fetching
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        # Start worker threads
        lockfile_watcher_worker = worker_service.get(Workers.LOCKFILE_WATCHER)
        lockfile_watcher_worker.start()
        lcu_event_processor_worker = worker_service.get(Workers.LCU_EVENT_PROCESSOR)
        lcu_event_processor_worker.com.data_signal.connect(self.on_data)
        lcu_event_processor_worker.start()

    def _fetch_balance_for_id(self, champ_id: int):
        """Helper to fetch balance and icon for a single champion ID"""
        champion = self.api_service.data_dragon.fetch_by_champion_id(champ_id)
        if champion is None:
            print(f"Warning: could not resolve champion for id {champ_id}")
            return None
        champ_name = champion.get("name")
        if not champ_name:
            print(f"Warning: champion data missing name for id {champ_id}")
            return None
        balance = self.api_service.lol_wiki.fetch_dynamic_balance_by_champion_name(champ_name)
        if balance is None:
            print(f"Warning: lol_wiki returned no balance for '{champ_name}'")
            return None
        balance.champion_icon = self.api_service.data_dragon.fetch_icon_by_champion_id(champ_id)
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

        # Parallelize fetching of all champion data and icons in a single batch.
        # Using a dictionary to map IDs back to results to maintain order and partition correctly.
        futures_map = {self._executor.submit(self._fetch_balance_for_id, cid): cid for cid in all_ids}

        # Wait for all tasks and store results
        results_by_id = {}
        for future in concurrent.futures.as_completed(futures_map):
            cid = futures_map[future]
            try:
                if (res := future.result()) is not None:
                    results_by_id[cid] = res
            except Exception as e:
                print(f"Error fetching data for champion {cid}: {e}")

        # Partition results back into team and available lists, maintaining original order
        team_balances = [results_by_id[cid] for cid in team_ids if cid in results_by_id]
        avail_balances = [results_by_id[cid] for cid in avail_ids if cid in results_by_id]

        if team_balances:
            self.team_champion_dynamic_balances = team_balances
        if avail_balances:
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
