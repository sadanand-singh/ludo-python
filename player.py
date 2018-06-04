from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gui import *

class Player(QObject):
    update_dice_widget = pyqtSignal(list)
    enable_player_figures = pyqtSignal(list)
    continue_game = pyqtSignal(bool)
    roll_dice = pyqtSignal()
    game_won = pyqtSignal()
    three_sixes_message = pyqtSignal()
    def __init__(self, name, color, color_name, parent=None):
        super().__init__(parent)

        self.name = name
        self.color = color
        self.color_name = color_name
        self.is_active = False
        self.current_dice = -1
        self.figures = []
        self.dice = []

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

    def setCurrentDice(self, data):
        dice, _ = data
        if not self.is_active: return
        if dice not in self.dice:
            raise ValueError("Error! current dice value is not list!")
        self.current_dice = dice

    def setDice(self, dice):
        if not self.is_active: return

        self.dice.append(dice)
        if dice == 6:
            if len(self.dice) > 2 and all([x == 6 for x  in self.dice[-3:]]):
                self.dice = self.dice[:-3]
                self.three_sixes_message.emit()
            self.update_dice_widget.emit(self.dice)
            self.roll_dice.emit()
            return
        self.enable_player_figures.emit([dice, None])

    def setEnabled(self, enable):
        self.is_active = enable

    def move(self, figure):
        if not self.is_active:
            self.continue_game.emit(self.is_active)
            return

        if not self.hasFigure(figure):
            self.continue_game.emit(False)
            return

        new_position = figure.getResultPosition()

        if not new_position: return

        if not new_position.isSpecial():
            allFigures = new_position.getFigures()
            for fig in allFigures:
                if fig.getColor() != self.color:
                    fig.moveToHome()
                    self.roll_dice.emit()
                else:
                    new_position = None
                    break

        self.dice.remove(self.current_dice)
        self.update_dice_widget.emit(self.dice)
        if isinstance(new_position, EndField):
            self.roll_dice.emit()
        figure.setPosition(new_position)

        for fig in self.figures:
            fig.setEnabled(False)

        if self.hasWon():
            self.game_won.emit()
            return

        self.is_active = len(self.dice) > 0
        self.continue_game.emit(self.is_active)
        return
