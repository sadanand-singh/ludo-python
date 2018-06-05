from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gui import *

class Player(QObject):
    continue_game = pyqtSignal(list)
    draw_dice = pyqtSignal(list)
    game_won = pyqtSignal()
    def __init__(self, name, color, color_name, parent=None):
        super().__init__(parent)

        self.name = name
        self.color = color
        self.color_name = color_name
        self.is_active = False
        self.bonus_moves = 0
        self.dice = []
        self.figures = []

    def hasWon(self):
        for fig in self.figures:
            if not isinstance(fig.getPosition(), EndField):
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
        if self.is_active:
            self.dice += dice
            self.draw_dice.emit(self.dice)

    def removeDice(self, dice):
        if self.is_active and dice in self.dice:
            self.dice.remove(dice)
            self.draw_dice.emit(self.dice)

    def setEnabled(self, enable):
        self.is_active = enable

    def move(self, figure):
        if not self.is_active:
            self.removeDice(figure.dice_value)
            self.continue_game.emit([self.is_active, 0])
            return

        if not self.hasFigure(figure):
            self.removeDice(figure.dice_value)
            self.continue_game.emit([False, 0])
            return

        newPosition = figure.getResultPosition()
        if not newPosition: return

        if not newPosition.isSpecial():
            allFigures = newPosition.getFigures()
            for fig in allFigures:
                if fig.getColor() != self.color:
                    fig.moveToHome()
                    self.bonus_moves += 1
                else:
                    newPosition = None
                    break

        if isinstance(newPosition, EndField):
            self.bonus_moves += 1
        figure.setPosition(newPosition)

        self.removeDice(figure.dice_value)

        for fig in self.figures:
            fig.setEnabled(False)

        if self.hasWon():
            self.game_won.emit()
            return

        self.is_active = len(self.dice) > 0
        if self.bonus_moves > 0: self.bonus_moves -= 1

        self.continue_game.emit([self.is_active, self.bonus_moves])
        return
