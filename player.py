from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gui import *

class Player(QObject):
    continue_game = pyqtSignal(bool)
    game_won = pyqtSignal()
    def __init__(self, name, color, color_name, parent=None):
        super().__init__(parent)

        self.name = name
        self.color = color
        self.color_name = color_name
        self.is_active = False
        self.bonus_moves = 0
        self.figures = []

    def hasWon(self):
        for fig in self.figures:
            if not isinstance(fig, EndField):
                return False
        return True

    def hasFigure(self, figure):
        if figure not in self.figures:
            return False
        return True

    def setFigures(self, figs):
        self.figures = [fig for fig in figs]

    def getFigures(self):
        return self.figures

    def getColor(self):
        return self.color, self.color_name

    def getName(self):
        return self.name

    def setDice(self, dice):
        self.dice = dice

    def setEnabled(self, enable):
        self.is_active = enable

    def move(self, figure):
        if not self.is_active:
            self.continue_game.emit(self.is_active)
            return

        if not self.hasFigure(figure):
            self.continue_game.emit(False)
            return

        newPosition = figure.getResultPosition()

        if not newPosition.isSpecial():
            allFigures = newPosition.getFigures()
            for fig in allFigures:
                if fig.getColor() != self.color:
                    fig.moveToHome()
                    self.bonus_moves += 1
                else:
                    newPosition = None
                    break

        if newPosition:
            if isinstance(newPosition, EndField):
                self.bonus_moves += 1
            figure.setPosition(newPosition)

        for fig in self.figures:
            fig.setEnabled(False)

        if self.hasWon():
            self.game_won.emit()
            return

        if self.dice == 6: self.bonus_moves += 1
        self.is_active = self.bonus_moves > 0
        if self.is_active: self.bonus_moves -= 1
        self.continue_game.emit(self.is_active)
        return
