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
        self.toolbar = self.addToolBar("Game")
        self.toolbar.setMovable(False)
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
        self.toolbar.addAction(self.new_game_action)
        menu.addAction(self.reset_action)
        self.toolbar.addAction(self.reset_action)

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

        self.status_label = QLabel("Ready")
        self.statusBar().addPermanentWidget(self.status_label)
        self.right_spacer = None
        self.dice_widgets = []

        self.add_figures()

        self.dice = DiceWidget()
        dice_pos = self.board.getDiceBox().boundingRect().topLeft()
        dice_pos -= QPointF(10, 10)
        self.dice.setPos(dice_pos)
        self.board.getScene().addItem(self.dice)

        self.dice.c.dice_rolled.connect(self.updateStatusMessage)

        self.setWindowTitle('Ludo')
        self.show()

    def add_figures(self):
        self.figures = []
        self.players = [None]*4
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        for index in range(4):
            figures = []
            start_fields = self.board.getStartField(index)

            for start_field in start_fields:
                figure = Figure(24.0)
                self.board.getScene().addItem(figure)
                figure.setPosition(start_field)
                figure.setStartPosition(start_field)
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
        self.status_label.setText("Ready")
        self.reset_action.setEnabled(False)
        self.dice.setPixmap(self.dice.images[0])
        self.dice.setEnabled(False)

        for index, player in enumerate(self.players):
            player.continue_game.disconnect(self.setCurrentPlayer)
            player.game_won.disconnect(self.finished)
            player.roll_dice.disconnect(self.roll_dice)
            player.enable_player_figures.disconnect(self.activatePlayerFigures)
            player.three_sixes_message.disconnect(self.threeSixesMessage)
            player.update_dice_widget.disconnect(self.drawDiceWidget)

            rect_box = self.board.getHome(index)
            rect_box.getHilightedRect().setVisible(False)
            start_fields = self.board.getStartField(index)
            figures = self.figures[index]
            self.dice.c.dice_rolled.disconnect(player.setDice)
            for id, start_field in enumerate(start_fields):
                figure = figures[id]
                figure.c.clicked.disconnect(player.move)

        l = len(self.players)
        for _ in range(l):
            del self.players[0]

        for player in self.players:
            player = None

        self.players = [None]*4
        for index in range(4):
            start_fields = self.board.getStartField(index)
            figures = self.figures[index]
            for id, start_field in enumerate(start_fields):
                figure = figures[id]
                figure.setPosition(start_field)

    def start(self, player_data):
        self.reset_action.setEnabled(True)
        self.new_game_action.setEnabled(False)
        self.status_label.setText("Game Started...")
        self.dice.setEnabled(True)
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']

        for index, (is_human, name) in enumerate(player_data):
            color_name = colors[index]
            color = self.colors[color_name]
            if not is_human: name = "Computer_" + str(index)

            player = Player(name, color, color_name, self) if is_human else Player(name, color, color_name, self)
            player.continue_game.connect(self.setCurrentPlayer)
            player.game_won.connect(self.finished)
            player.roll_dice.connect(self.roll_dice)
            player.enable_player_figures.connect(self.activatePlayerFigures)
            player.three_sixes_message.connect(self.threeSixesMessage)
            player.update_dice_widget.connect(self.drawDiceWidget)

            start_fields = self.board.getStartField(index)
            figures = self.figures[index]
            player.setFigures(figures)
            self.dice.c.dice_rolled.connect(player.setDice)
            for id, start_field in enumerate(start_fields):
                figure = figures[id]
                figure.c.clicked.connect(player.move)
            self.players[index] = player

        self.current_player = self.players[0]
        self.showTurn()
        self.current_player.setEnabled(True)
        self.dice.roll()

    def drawDiceWidget(self, dice_list):
        self.removeCurrentDiceWidget()
        color = self.current_player.getColor()
        self.right_spacer = QWidget()
        self.right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(self.right_spacer)
        for dice in dice_list:
            widget = QPushButton(str(dice))
            pal = widget.palette()
            pal.setColor(QPalette.Button, color)
            widget.setAutoFillBackground(true)
            widget.setPalette(pal)
            widget.update()
            self.toolbar.addWidget(widget)
            for player in self.players:
                widget.clicked.connect(player.setCurrentDice)
            widget.clicked.connect(self.activatePlayerFigures)
            widget.clicked.connect(self.uncheckOtherDiceWidgets)
            self.dice_widgets.append(widget)

    def removeCurrentDiceWidget(self):
        del self.right_spacer
        self.right_spacer = None
        for widget in self.dice_widgets:
            for player in self.players:
                widget.clicked.disconnect(player.setCurrentDice)
            widget.clicked.disconnect(self.activatePlayerFigures)
            widget.clicked.disconnect(self.uncheckOtherDiceWidgets)

        l = len(self.dice_widgets)
        for _ in range(l):
            del self.dice_widgets[0]

        for widget in self.dice_widgets:
            widget = None
        self.dice_widgets = []

    def uncheckOtherDiceWidgets(self, data):
        diceValue, widget = data
        other_widgets = [w for w in self.dice_widgets if w != widget]
        for widget in other_widgets:
            widget.uncheck()

    def activatePlayerFigures(self, data):
        diceValue, _ = data
        print(diceValue)
        figures = self.current_player.getFigures()
        is_any_enabled = False
        for figure in figures:
            enable = figure.enableIfPossible(diceValue)
            is_any_enabled = is_any_enabled or enable

        if not is_any_enabled:
            self.setCurrentPlayer(False)

    def setCurrentPlayer(self, is_active):
        if not is_active:
            self.current_player.setEnabled(False)
            try:
                player_id = self.players.index(self.current_player)
            except ValueError:
                return
            player_id = player_id+1 if player_id != 3 else 0
            self.current_player = self.players[player_id]
            self.current_player.setEnabled(True)
            self.roll_dice()
            print(self.current_player.getName())
        else:
            self.showTurn()
        return

    def roll_dice(self):
        print("throwing dice for player {}".format(self.current_player.getName()))
        self.showTurn()
        self.dice.resetDice()
        self.delay(1.0)
        self.dice.roll()

    def delay(self, time_in_sec=1.0):
        dice_time = QTime.currentTime().addSecs(time_in_sec)
        while QTime.currentTime() < dice_time:
            QCoreApplication.processEvents(QEventLoop.AllEvents, 100)

    def showTurn(self):
        for idx in range(4):
            rect_box = self.board.getHome(idx)
            rect_box.getHilightedRect().setVisible(False)

        _, color_name = self.current_player.getColor()
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        index = colors.index(color_name)
        msg = "Current Player: {0} ({1})".format(self.current_player.getName(), color_name)
        self.statusBar().showMessage(msg)

        rect_box = self.board.getHome(index)
        rect_box.getHilightedRect().setVisible(True)

    def updateStatusMessage(self, diceValue):
        _, color_name = self.current_player.getColor()
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        index = colors.index(color_name)
        msg = "{0} ({1}) You Got {2}!".format(self.current_player.getName(), color_name, diceValue)
        self.status_label.setText(msg)

    def threeSixesMessage(self):
        _, color_name = self.current_player.getColor()
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        index = colors.index(color_name)
        msg = "{0} ({1}) You Got 3 consecutive 6s! Sorry, you need to roll the dice agian."
        msg = msg.format(self.current_player.getName(), color_name)
        self.statusBar().setText(msg)
        self.status_label.setText("")

    def finished(self):
        _, color_name = self.current_player.getColor()
        colors = ['RED', 'GREEN', 'YELLOW', 'BLUE']
        index = colors.index(color_name)
        msg = "Player: {0} ({1}) WON!!!".format(self.current_player.getName(), color_name)
        self.statusBar().showMessage(msg)
        self.status_label.setText("")

    def how_to_play(self):
        QMessageBox.about(self, "How to Play LUDO",
                 """<b>How to Play Ludo</b><br>
                 There are 4 colored players, each having 4 pieces.
                 Red player starts first.
                 You need to get a SIX (6) to come out of HOME.<br><br>
                 <b>YOUR GOAL: </b>Each player's goal is to put all 4 pieces to central end-zone!
                 Each player needs to go around the board to reach the final end-zone.
                 Board has 3 kinds of positions: <b>normal, special and safe/end.</b><br><br>
                 In the <b>Normal</b> position, If another colored player falls
                 on your place. You end up being dead and go back to HOME.
                 You can not place more than one of your pieces in one position.
                 In the <b>Special</b> position, denoted by 'STAR'
                 symbols, everyone is safe. You start from the special
                 position nearest to you denoted by the corresponding
                 colored star. Any player can put as many pieces as they
                 wish. Finally, in <b>safe/end</b> positions, colored
                 acordingly, no other colored piece/player can land.<br><br>
                 The first player to bring all 4 pieces to the end-zone WINS!
                 """)

    def about(self):
        QMessageBox.about(self, "About Ludo",
                "<b>Ludo</b> is a board game. <br>"
                "&copy; by Sadanand Singh 2018-19")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Ludo()
    sys.exit(app.exec_())