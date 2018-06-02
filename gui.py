from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import resources

class Field(QObject, QGraphicsRectItem):
    def __init__(self, x, y, w, h, parent):
        QGraphicsRectItem.__init__(self, x, y, w, h, parent)
        index = 0
        self.setPen(QPen(Qt.black, 2.0))
        self.is_special = False
        self.nextField = None
        self.prevField = None
        self.figures = []
        self.text = None

    def setNextField(self, field):
        self.nextField = field

    def setPreviousField(self, field):
        self.prevField = field

    def next(self, color):
        return self.nextField

    def previous(self):
        return self.prevField

    def getFigures(self):
        return self.figures

    def addFigure(self, figure):
        self.figures.append(figure)
        self.drawFigures()

    def removeFigure(self, figure):
        temp = [x for x in self.figures if x != figure]
        self.figures = temp
        self.drawFigures()

    def setColor(self, color):
        pass

    def setSafeField(self, field):
        pass

    def drawFigures(self):
        scene = self.scene()
        fig_count = 0

        if self.text:
            scene.removeItem(text)
            self.text = None

        for fig in self.figures:
            fig_count += 1
            scene.removeItem(fig)
            center = self.boundingRect().center()
            fig.setDiameter(24.0)
            figureRadius = 0.5 * fig.getDiameter()
            topLeft = center - QPointF(figureRadius, figureRadius)
            fig.setPos(topLeft)
            scene.addItem(fig)

        if fig_count > 1:
            self.text = QGraphicsTextItem()
            fig = figures.at(0)
            figureRadius = 0.5 * fig.getDiameter()
            center = self.boundingRect().center()
            topLeft = center - QPointF(figureRadius, figureRadius)
            topLeft += QPointF(5, 0)
            text.setPos(topLeft)
            text.setFont(QFont("Times", 10, QFont.Bold))
            text.setPlainText(str(figureCount))
            scene.addItem(text)

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def isSpecial(self):
        return self.is_special

class StartField(Field):
    def __init__(self, rect, parent):
        super().__init__(rect.x()+1.0, rect.y()+1.0, rect.width()-2.0, rect.height()-2.0, parent)
        self.setVisible(False)

class SpecialField(Field):
    def __init__(self, rect, parent):
        super().__init__(rect.x()+1.0, rect.y()+1.0, rect.width()-2.0, rect.height()-2.0, parent)
        self.colorCounts = [0, 0, 0, 0]
        self.figureColors = 0
        self.texts = [None, None, None, None]
        self.colors =[QColor(205, 92, 92), QColor(85, 107, 47), QColor(218, 165, 32), QColor(0, 191, 255)]
        self.is_special = True
        self.setBrush(QBrush(Qt.lightGray))
        self.shifts = [QPointF(-10.0, -10.0), QPointF(10.0, -10.0), QPointF(10.0, 10.0), QPointF(-10.0, 10.0)]

    def addFigure(self, fig):
        color = fig.getColor()
        index = self.colors.index(color)
        if self.colorCounts[index] == 0: self.figureColors += 1
        self.colorCounts[index] += 1
        super().addFigure(fig)

    def removeFigure(self, fig):
        color = fig.getColor()
        index = self.colors.index(color)
        if self.colorCounts[index] == 1: self.figureColors -= 1
        self.colorCounts[index] -= 1
        super().removeFigure(fig)

    def drawFigures(self):
        scene = self.scene()
        if self.text:
            scene.removeItem(self.text)
            self.text = None

        for text in self.texts:
            if text:
                scene.removeItem(text)
                text = None

        if self.figureColors == 1:
            color = self.figures[0].getColor()
            index = self.colors.index(color)
            self.text = self.texts[index]
            super().drawFigures()
            return

        for fig in self.figures:
            color = fig.getColor()
            index = self.colors.index(color)
            center = self.boundingRect().center()
            center = self.get_new_center(center, index)
            fig.setDiameter(16.0)
            figureRadius = 0.5 * fig.getDiameter()
            topLeft = center - QPointF(figureRadius, figureRadius)
            fig.setPos(topLeft)
            scene.addItem(fig)

        for index in range(4):
            count = self.colorCounts[index]
            if count > 1:
                text = QGraphicsTextItem()
                center = self.boundingRect().center()
                center = self.get_new_center(center, index)
                topLeft = center - QPointF(8.0, 8.0)
                topLeft += QPointF(2, -2)
                text.setPos(topLeft)
                text.setFont(QFont("Times", 10, QFont.Bold))
                text.setPlainText(str(figureCount))
                scene.addItem(text)
                self.texts[index] = text

    def get_new_center(self, center, index):
        return center+self.shifts[index]

class SafeField(Field):
    def __init__(self, x, y, w, h, parent):
        super().__init__(x, y, w, h, parent)
        self.color = QColor()

    def setColor(self, color):
        self.color = color
        self.setBrush(QBrush(self.color))

class LastField(Field):
    def __init__(self, x, y, w, h, parent):
        super().__init__(x, y, w, h, parent)
        self.color = QColor()
        self.nextSafe = None

    def setColor(self, color):
        self.color = color

    def getColor(self):
        return self.color

    def setSafeField(self, field):
        self.nextSafe = field

    def next(self, color):
        if color == self.color: return self.nextSafe
        return self.nextField

class EndField(Field):
    def __init__(self, x, y, w, h, parent):
        super().__init__(x, y, w, h, parent)
        self.setVisible(False)
        self.is_special = True

    def drawFigures(self):
        scene = self.scene()

        if self.text:
            scene.removeItem(text)
            self.text = None
            fig_count = 0

        for fig in self.figures:
            fig_count += 1
            scene.removeItem(fig)
            center = self.boundingRect().center()
            fig.setDiameter(18.0)
            figureRadius = 0.5 * fig.getDiameter()
            topLeft = center - QPointF(figureRadius, figureRadius)
            fig.setPos(topLeft)
            scene.addItem(fig)
        if fig_count > 1:
            self.text = QGraphicsTextItem()
            fig = figures.at(0)
            figureRadius = 0.5 * fig.getDiameter()
            center = self.boundingRect().center()
            topLeft = center - QPointF(figureRadius, figureRadius)
            topLeft += QPointF(2, -2)
            self.text.setPos(topLeft)
            self.text.setFont(QFont("Times", 10, QFont.Bold))
            self.text.setPlainText(str(figureCount))
            scene.addItem(text)

class HomeField(QObject):
    def __init__(self, x, y, r, c, scene, parent):
        super().__init__(parent)





















class OnDemandSpacer(QWidget):
    def __init__(self):
        super().__init__()

        hLayout = QHBoxLayout()
        self.spacer = QSpacerItem(150, 12, QSizePolicy.Fixed, QSizePolicy.Fixed)

        hLayout.addSpacerItem(self.spacer)
        self.setLayout(hLayout)

class PlayerIcon(QWidget):
    def __init__(self, color):
        super().__init__()

        self.color = color
        self.setFixedSize(20, 20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black , 0.5))
        painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))

class PlayerOption(QWidget):
    def __init__(self, color):
        super().__init__()

        self.icon = PlayerIcon(color)
        self.computerOption = QRadioButton("Computer")
        self.humanOption = QRadioButton("Human")
        self.playerName = QLineEdit()
        self.spacer = OnDemandSpacer()
        self.hLayout = QHBoxLayout()

        self.computerOption.setChecked(True)
        self.humanOption.setChecked(False)

        self.playerName.setPlaceholderText("Enter player name...")
        self.playerName.setClearButtonEnabled(True)
        self.playerName.setVisible(False)
        self.playerName.setFixedWidth(180)

        self.spacer.setVisible(True)
        self.spacer.setFixedWidth(180)

        self.hLayout.addWidget(self.icon)
        self.hLayout.addWidget(self.computerOption)
        self.hLayout.addWidget(self.humanOption)
        self.hLayout.addWidget(self.playerName)
        self.hLayout.addWidget(self.spacer)

        self.humanOption.toggled.connect(self.playerName.setVisible)
        self.humanOption.toggled.connect(self.spacer.setHidden)

        self.setLayout(self.hLayout)

    def getPlayerName(self):
        return self.playerName

    def getComputerOption(self):
        return self.computerOption

    def getHumanOption(self):
        return self.humanOption


class NewGameDialog(QDialog):
    trigger = pyqtSignal(list)
    def __init__(self, title):
        super().__init__()

        self.okButton = QPushButton("Start Demo")
        self.okButton.setEnabled(True)
        self.okButton.setDefault(True)
        self.cancelButton = QPushButton("Cancel")
        self.spacer = OnDemandSpacer()
        self.hLayoutButton = QHBoxLayout()
        self.buttons = QWidget()

        self.player_list = []
        self.player_list.append(PlayerOption(QColor(205, 92, 92)))
        self.player_list.append(PlayerOption(QColor(85, 107, 47)))
        self.player_list.append(PlayerOption(QColor(218, 165, 32)))
        self.player_list.append(PlayerOption(QColor(0, 191, 255)))

        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.buttons)
        self.vLayout.setSizeConstraint(QLayout.SetFixedSize)
        for player in self.player_list:
            self.vLayout.addWidget(player)

        self.hLayoutButton.addWidget(self.spacer)
        self.hLayoutButton.addWidget(self.okButton)
        self.hLayoutButton.addWidget(self.cancelButton)
        self.buttons.setLayout(self.hLayoutButton)

        self.setWindowTitle(title)
        self.setLayout(self.vLayout)
        self.setModal(True)

        self.cancelButton.clicked.connect(self.close)
        self.okButton.clicked.connect(self.savePlayerData)

        for player in self.player_list:
            field = player.getPlayerName()
            field.textChanged.connect(self.enableOKButton)
            computerOption = player.getComputerOption()
            computerOption.toggled.connect(self.enableOKButton)

    def enableOKButton(self):
        player_names = []
        valid_names = 0
        ok = True
        any_human = False

        for player in self.player_list:
            is_human = player.getHumanOption().isChecked()
            name = player.getPlayerName().text()
            player_ok = name and is_human

            if player_ok:
                valid_names += 1
                player_names.append(name.lower())

            player_ok = player_ok or not is_human
            ok = ok and player_ok
            any_human = any_human or is_human

        player_names = set(player_names)
        if valid_names != len(player_names):
            ok = False

        buttonTitle = "Start Demo"
        if any_human: buttonTitle = "Start Game"
        self.okButton.setText(buttonTitle)
        self.okButton.setEnabled(ok)

    def savePlayerData(self):
        player_data = []
        for player in self.player_list:
            is_human = player.getHumanOption().isChecked()
            name = ""
            if is_human: name = player.getPlayerName().text()
            player_data.append((is_human, name))

        self.accept()
        self.trigger.emit(player_data)
