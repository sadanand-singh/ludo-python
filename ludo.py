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
from PyQt5.QtCore import QPointF, QTime, QCoreApplication, QEventLoop
from gui import NewGameDialog, Figure, DiceWidget
from player import Player
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

        self.dice = DiceWidget()
        dicePos = self.board.getDiceBox().boundingRect().topLeft()
        dicePos -= QPointF(10, 10)
        self.dice.setPos(dicePos)
        self.board.getScene().addItem(self.dice)

        self.dice.c.diceRolled.connect(self.updateStatusMessage)
        self.dice.c.diceRolled.connect(self.activatePlayerFigures)

        self.setWindowTitle('Ludo')
        self.show()

    def add_figures(self):
        self.figures = []
        self.players = [None]*4
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        for index in range(4):
            figures = []
            startFields = self.board.getStartField(index)

            for startField in startFields:
                figure = Figure(24.0)
                self.board.getScene().addItem(figure)
                figure.setPosition(startField)
                figure.setStartPosition(startField)
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
        self.dice.setPixmap(self.dice.images[0])
        self.dice.setEnabled(False)

        for index, player in enumerate(self.players):
            startFields = self.board.getStartField(index)
            figures = self.figures[index]
            self.dice.c.diceRolled.disconnect(player.setDice)
            for id, startField in enumerate(startFields):
                figure = figures[id]
                figure.c.clicked.disconnect(player.move)

        l = len(self.players)
        for _ in range(l):
            del self.players[0]

        for player in self.players:
            player = None

        self.players = [None]*4
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
        self.dice.setEnabled(True)
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']

        for index, (is_human, name) in enumerate(player_data):
            color_name = colors[index]
            color = self.colors[color_name]
            if not is_human: name = "Computer"

            player = Player(name, color, color_name, self) if is_human else Player(name, color, color_name, self)

            player.continue_game.connect(self.setCurrentPlayer)
            player.game_won.connect(self.finished)

            startFields = self.board.getStartField(index)
            figures = self.figures[index]
            player.setFigures(figures)
            self.dice.c.diceRolled.connect(player.setDice)
            for id, startField in enumerate(startFields):
                figure = figures[id]
                figure.c.clicked.connect(player.move)
            self.players[index] = player

        self.currPlayer = self.players[0]
        self.showTurn()
        self.currPlayer.setEnabled(True)
        self.dice.roll()

    def activatePlayerFigures(self, diceValue):
        figures = self.currPlayer.getFigures()
        is_any_enabled = False
        for figure in figures:
            enable = figure.enableIfPossible(diceValue)
            is_any_enabled = is_any_enabled or enable

        if not is_any_enabled:
            self.setCurrentPlayer(False)

    def setCurrentPlayer(self, isActive):
        if not isActive:
            self.currPlayer.setEnabled(False)
            try:
                indexPlayer = self.players.index(self.currPlayer)
            except ValueError:
                return
            indexPlayer = indexPlayer+1 if indexPlayer != 3 else 0
            self.currPlayer = self.players[indexPlayer]
            self.currPlayer.setEnabled(True)

        self.showTurn()
        self.dice.resetDice()
        self.delay(1)
        self.dice.roll()

    def delay(self, time_in_sec):
        dice_time = QTime.currentTime().addSecs(time_in_sec)
        while QTime.currentTime() < dice_time:
            QCoreApplication.processEvents(QEventLoop.AllEvents, 100)

    def showTurn(self):
        for idx in range(4):
            rectBox = self.board.getHome(idx)
            rectBox.getHiliteRect().setVisible(False)

        _, color_name = self.currPlayer.getColor()
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        index = colors.index(color_name)
        msg = "Current Player: {0} ({1})".format(self.currPlayer.getName(), color_name)
        self.statusBar().showMessage(msg)

        rectBox = self.board.getHome(index)
        rectBox.getHiliteRect().setVisible(True)

    def updateStatusMessage(self, diceValue):
        _, color_name = self.currPlayer.getColor()
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        index = colors.index(color_name)
        msg = "{0} ({1}) You Got {2}!".format(self.currPlayer.getName(), color_name, diceValue)
        self.statusLabel.setText(msg)

    def finished(self):
        _, color_name = self.currPlayer.getColor()
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        index = colors.index(color_name)
        msg = "Player: {0} ({1}) WON!!!".format(self.currPlayer.getName(), color_name)
        self.statusBar().showMessage(msg)
        self.statusLabel.setText("")

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