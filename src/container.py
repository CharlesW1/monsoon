from PySide6 import QtWidgets
from dependency_injector import containers, providers

from services import (
    ApplicationHostService,
    WorkerService,
    ApiService,
    SettingsContextService
)
from viewmodels import AboutWindowViewModel, SystemTrayViewModel, AppWindowViewModel
from views import AboutWindowView, SystemTray, AppWindowView


class Container(containers.DeclarativeContainer):
    """Represents a container used to configure services used with dependency
  injection.
  """

    # Services
    settings_context_service = providers.ThreadSafeSingleton(SettingsContextService)
    api_service = providers.ThreadSafeSingleton(ApiService)
    application_host_service = providers.ThreadSafeSingleton(ApplicationHostService)
    worker_service = providers.ThreadSafeSingleton(WorkerService)

    # Views and ViewModels
    application = providers.Singleton(QtWidgets.QApplication)
    system_tray = providers.Singleton(SystemTray)
    system_tray_viewmodel = providers.Singleton(SystemTrayViewModel)
    app_window_viewmodel = providers.Singleton(AppWindowViewModel)
    app_window_view = providers.Singleton(AppWindowView)
    about_window_viewmodel = providers.Singleton(AboutWindowViewModel)
    about_window_view = providers.Singleton(AboutWindowView)
