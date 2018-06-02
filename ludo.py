#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
Ludo in PyQt5

This program creates a game of Ludo with option to play against
other human or computer players. Different kinds of strategies
can be chosen for the computer players.

Author: Sadanand Singh
Website: sadanand-singh.github.io
Last edited: August 2017
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from gui import NewGameDialog, Figure
from board import Board
import resources

class Ludo(QMainWindow):

    def __init__(self):
        super().__init__()

        icon = QIcon(":/images/game")
        self.setWindowIcon(icon)

        self.colors = {}
        self.colors['RED'] = QColor(205, 92, 92)
        self.colors['GREEN'] = QColor(85, 107, 47)
        self.colors['YELLOW'] = QColor(218, 165, 32)
        self.colors['BLUE'] = QColor(0, 191, 255)

        self.board = Board()
        self.setCentralWidget(self.board)
        self.setFixedSize(635, 720)

        menu = self.menuBar().addMenu("&Game")
        toolbar = self.addToolBar("Game")
        toolbar.setMovable(False)
        icon = QIcon(":/images/icon")
        self.new_game_action = QAction(icon, "&New Game", self)
        self.new_game_action.setShortcuts(QKeySequence.New)
        self.new_game_action.setStatusTip("Start a New Game")
        self.new_game_action.triggered.connect(self.start_game)

        icon = QIcon(":/images/reset")
        self.reset_action = QAction(icon, "&Reset Game", self)
        self.reset_action.setShortcuts(QKeySequence.SelectEndOfDocument)
        self.reset_action.setStatusTip("Reset Game")
        self.reset_action.setEnabled(False)
        self.reset_action.triggered.connect(self.reset)

        menu.addAction(self.new_game_action)
        toolbar.addAction(self.new_game_action)
        menu.addAction(self.reset_action)
        toolbar.addAction(self.reset_action)

        menu.addSeparator()
        exit_icon = QIcon(":/images/exit")
        exit_action = QAction(exit_icon, "&Exit", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcuts(QKeySequence.Quit)
        exit_action.setStatusTip("Exit the Application")
        menu.addAction(exit_action)

        menu.addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        how_to_play = help_menu.addAction("&How To Play", self.how_to_play)
        how_to_play.setStatusTip("Show How to Play Ludo")

        about_action = help_menu.addAction("&About Ludo App", self.about)
        about_action.setStatusTip("Show Details About Ludo")

        about_qt_action = help_menu.addAction("About &Qt", QApplication.aboutQt)
        about_qt_action.setStatusTip("Show Qt library's About Menu")

        self.statusLabel = QLabel("Ready")
        self.statusBar().addPermanentWidget(self.statusLabel)

        self.add_figures()

        self.setWindowTitle('Ludo')
        self.show()

    def add_figures(self):
        self.figures = []
        self.players = [None, None, None, None]
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        for index in range(4):
            figures = []
            startFields = self.board.getStartField(index)

            for startField in startFields:
                figure = Figure(24.0)
                self.board.getScene().addItem(figure)
                figure.setPosition(startField)
                figure.setColor(self.colors[colors[index]])
                figures.append(figure)

            self.figures.append(figures)


    def start_game(self):
        dialog = NewGameDialog("Choose Players...")
        dialog.trigger.connect(self.start)
        dialog.exec()
        del dialog

    def reset(self):
        self.new_game_action.setEnabled(True)
        self.statusLabel.setText("Ready")
        self.reset_action.setEnabled(False)

        for index in range(4):
            startFields = self.board.getStartField(index)
            figures = self.figures[index]
            for id, startField in enumerate(startFields):
                figure = figures[id]
                figure.setPosition(startField)

    def start(self, player_data):
        self.reset_action.setEnabled(True)
        self.new_game_action.setEnabled(False)
        self.statusLabel.setText("Game Started...")
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']

        for index, (is_human, name) in enumerate(player_data):
            color = self.colors[colors[index]]
            if not is_human: name = "Computer"
            print(name)


    def how_to_play(self):
        QMessageBox.about(self, "How to Play LUDO",
                 "<b>How to Play Ludo</b> <br>"
                 "There are 4 colored players, "
                 "each having 4 pieces. <br> Red player starts first.<br>"
                 "You need to get a SIX to come out of HOME area.<br>"
                 "If another colored player falls on your place.<br>"
                 "You end up being dead and go back to HOME.<br>"
                 "First player to bring all pieces to central <br>"
                 "box WINS the game.")

    def about(self):
        QMessageBox.about(self, "About Ludo",
                "<b>Ludo</b> is a board game. <br>"
                "&copy; by Sadanand Singh 2018-19")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Ludo()
    sys.exit(app.exec_())