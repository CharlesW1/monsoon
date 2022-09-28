from PySide6 import QtWidgets, QtCore
from constant import Monsoon
from controller import EventDataController, LeagueClientController

class MainView(QtWidgets.QMainWindow):
  def __init__(self, event_data_controller: EventDataController):
    super().__init__()

    # Set instance variables
    self.client_controller = LeagueClientController()
    self.event_data_controller = event_data_controller
    (self.hbox, self.hbox_layout) = self.__create_hbox()
    (self.left_vbox, self.left_vbox_layout) = self.__create_vbox()
    (self.left_sub_hbox, self.left_sub_hbox_layout) = self.__create_hbox()
    (self.middle_vbox, self.middle_vbox_layout) = self.__create_vbox()
    (self.right_vbox, self.right_vbox_layout) = self.__create_vbox()
    (self.team_damages_vbox, self.team_damages_vbox_layout) = self.__create_vbox()
    (self.team_others_vbox, self.team_others_vbox_layout) = self.__create_vbox()
    (self.bench_info_hbox, self.bench_info_hbox_layout) = self.__create_hbox()
    self.team_damages_rows = [QtWidgets.QLabel("") for i in range(5)]
    self.team_others_rows = [QtWidgets.QLabel("") for i in range(5)]
    self.bench_info_columns = [QtWidgets.QLabel("") for i in range(10)]

    # Set horizontal box columns
    self.hbox_layout.addWidget(self.left_vbox, 35)
    self.hbox_layout.addWidget(self.middle_vbox, 58)
    self.hbox_layout.addWidget(self.right_vbox, 35)

    # Set left box rows
    self.left_vbox_layout.addWidget(QtWidgets.QLabel(""), 2)
    self.left_vbox_layout.addWidget(self.left_sub_hbox, 8)
    self.left_vbox_layout.addWidget(QtWidgets.QLabel(""), 3)

    # Set left sub horizontal box columns
    self.left_sub_hbox_layout.addWidget(QtWidgets.QLabel(""), 1)
    self.left_sub_hbox_layout.addWidget(self.team_damages_vbox, 1)
    self.left_sub_hbox_layout.addWidget(self.team_others_vbox, 1)

    # Set middle box rows
    self.middle_vbox_layout.addWidget(self.bench_info_hbox, 1)
    self.middle_vbox_layout.addWidget(QtWidgets.QLabel(""), 13)

    # Set team damages rows
    for row in self.team_damages_rows:
      self.team_damages_vbox_layout.addWidget(row)
    
    # Set team others rows
    for row in self.team_others_rows:
      self.team_others_vbox_layout.addWidget(row)

    # Set bench info columns
    self.bench_info_hbox_layout.setContentsMargins(0, 0, 0, 0)
    for column in self.bench_info_columns:
      self.bench_info_hbox_layout.addWidget(column)

    # Set window properties
    self.resize(Monsoon.WIDTH.value, Monsoon.HEIGHT.value)
    self.setWindowTitle(Monsoon.TITLE.value)
    self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
    self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    self.setCentralWidget(self.hbox)

  def __create_hbox(self):
    hbox = QtWidgets.QGroupBox()
    hbox_layout = QtWidgets.QHBoxLayout()
    hbox.setLayout(hbox_layout)

    return (hbox, hbox_layout)
  
  def __create_vbox(self):
    vbox = QtWidgets.QGroupBox()
    vbox_layout = QtWidgets.QVBoxLayout()
    vbox.setLayout(vbox_layout)

    return (vbox, vbox_layout)
    
  @QtCore.Slot()
  def refresh(self):
    if (self.client_controller.is_active()):
      (left, top, right, bottom) = self.client_controller.find()

      # Calculate window dimensions
      height = bottom - top
      width = right - left

      # Have our event data controller process any events in queue
      self.event_data_controller.process()
      (is_active, team_balances, team_other_balances, bench_balances) = self.event_data_controller.get_state()
      if is_active:
        # Process team balances
        for i, balance in enumerate(team_balances):
          self.team_damages_rows[i].setText(balance)
          if len(balance) > 0:
            self.team_others_rows[i].setText("ℹ️")
            self.team_others_rows[i].setToolTip(team_other_balances[i])
          else:
            self.team_others_rows[i].setText("")
            self.team_others_rows[i].setToolTip("")
          

        # Process bench balances
        for i, balance in enumerate(bench_balances):
          if len(balance) > 0:
            self.bench_info_columns[i].setText("ℹ️")
            self.bench_info_columns[i].setToolTip(balance)
          else:
            self.bench_info_columns[i].setText("")
            self.bench_info_columns[i].setToolTip("")
        self.show()
      else:
        self.hide()

      # Adjust view based on League client (lock onto it)
      self.setGeometry(left, top, width, height)
    pass

