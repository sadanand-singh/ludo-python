from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import resources
import random

class DiceWidget(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = False
        random.seed(1234)
        self.c = Communicate()
        self.images = []
        self.images.append(QPixmap(":/images/dice"))
        self.images.append(QPixmap(":/images/dice1"))
        self.images.append(QPixmap(":/images/dice2"))
        self.images.append(QPixmap(":/images/dice3"))
        self.images.append(QPixmap(":/images/dice4"))
        self.images.append(QPixmap(":/images/dice5"))
        self.images.append(QPixmap(":/images/dice6"))
        self.setPixmap(self.images[0])
        self.dice = 0
        self.graphicsRotation = QGraphicsRotation()
        self.graphicsRotation.setAxis(Qt.YAxis)
        self.graphicsRotation.setAngle(0)
        self.graphicsRotation.setOrigin(QVector3D(QPointF(35, 35)))
        self.setTransformations([self.graphicsRotation])

        self.animation = QPropertyAnimation(self.graphicsRotation, b"angle")
        self.animation.setDuration(500)
        self.animation.setStartValue(self.graphicsRotation.angle())
        self.animation.setEndValue(360)
        self.animation.finished.connect(self.throwDice)

    def mousePressEvent(self, mouse_event):
        if not self.enabled: return
        QGraphicsPixmapItem.mousePressEvent(mouse_event)

    def throwDice(self):
        self.dice = random.randint(1, 6)
        self.setPixmap(self.images[self.dice])
        self.enabled = False
        self.c.diceRolled.emit(self.dice)

    def resetDice(self):
        self.setPixmap(self.images[0])
        self.enabled = True

    def roll(self):
        if not self.enabled: return
        self.setPixmap(self.images[0])
        self.animation.start()

    def setEnabled(self, enabled):
        self.enabled = enabled

    def value(self):
        return self.dice

class Figure(QGraphicsEllipseItem):
    def __init__(self, diameter, parent=None):
        super().__init__(0.0, 0.0, diameter, diameter, parent)
        self.diameter = diameter
        self.enabled = False
        self.hilight = None
        self.currPos = None
        self.color = None
        self.player = None
        self.setAcceptHoverEvents(True)
        self.setPen(QPen(Qt.black, 2.0))
        self.c = Communicate()
        self.c.enter.connect(self.hilightField)
        self.c.leave.connect(self.unhilightField)

    def hoverEnterEvent(self, event):
        if not self.enabled: return
        self.c.enter.emit(self)

    def hoverLeaveEvent(self, event):
        if not self.enabled: return
        self.c.leave.emit(self)

    def mousePressEvent(self, mouse_event):
        if not self.enabled: return
        self.c.clicked.emit(self)

    def hilightField(self, fig):
        pos = fig.getResultPosition()
        if pos is not None:
            scene = pos.scene()
            fig.hilight = scene.addRect(pos.boundingRect())
            color = fig.getColor()
            fig.hilight.setPen(QPen(color, 4.0))

    def unhilightField(self, fig):
        if fig.hilight is not None:
            pos = fig.getResultPosition()
            scene = pos.scene()
            scene.removeItem(fig.hilight)
            fig.hilight = None

    def setEnabled(self, enabled):
        self.enabled = enabled

    def isEnabled(self):
        return self.enabled

    def setPlayer(self, player):
        self.player = player
        self.color = player.getColor()
        self.setBrush(QBrush(self.color))

    def getColor(self):
        return self.color

    def setColor(self, color):
        self.color = color
        self.setBrush(QBrush(self.color))

    def setPosition(self, pos):
        self.unhilightField(self)
        if self.currPos: self.currPos.removeFigure(self)
        self.currPos = pos
        self.currPos.addFigure(self)

    def getPlayer(self):
        return self.player

    def getPosition(self):
        return self.currPos

    def getResultPosition(self):
        return self.resultPos

    def getDiameter(self):
        return self.diameter

    def setDiameter(self, diameter):
        self.diameter = diameter
        self.setRect(0, 0, diameter, diameter)

    def enableIfPossible(self, dice):
        enabled = False
        if isinstance(currPos, EndField):
            return enabled
        if isinstance(currPos, StartField):
            if dice == 6:
                self.setEnabled(True)
                enabled = True
                resultPos = currPos.next(self.color)
            return enabled

        resultPos = self.findResultPosition(dice)
        if resultPos:
            if not resultPos.isSpecial():
                figs = resultPos.getFigures()
                if len(figs) != 0:
                    existingColor = figs[0].getColor()
                    if self.color != existingColor:
                        self.setEnabled(True)
                        enabled = True
                else:
                    self.setEnabled(True)
                    enabled = True
            else:
                self.setEnabled(True)
                enabled = True
        return enabled

    def findResultPosition(self, dice):
        resultPos = None

        resultPosTemp = self.currPos
        while dice > 0:
            dice -= 1
            if resultPosTemp:
                resultPosTemp = resultPosTemp.next(color)
            else:
                break

        if dice == -1 and resultPosTemp:
            resultPos = resultPosTemp

        return resultPos

    def getHilight(self):
        return self.hilight

    def moveToHome(self):
        startField = self.player.getStartField()
        index = self.player.getFigures().index(self)
        start = startField[index]
        self.setPosition(start)

class Communicate(QObject):
    enter = pyqtSignal(Figure)
    leave = pyqtSignal(Figure)
    clicked = pyqtSignal(Figure)
    moved = pyqtSignal(Figure)
    diceRolled = pyqtSignal(int)

class Field(QGraphicsRectItem, QObject):
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
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
    def __init__(self, rect, parent=None):
        super().__init__(rect.x()+1.0, rect.y()+1.0, rect.width()-2.0, rect.height()-2.0, parent)
        self.setVisible(False)

class SpecialField(Field):
    def __init__(self, rect, parent=None):
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
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.color = QColor()

    def setColor(self, color):
        self.color = color
        self.setBrush(QBrush(self.color))

class LastField(Field):
    def __init__(self, x, y, w, h, parent=None):
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
    def __init__(self, x, y, w, h, parent=None):
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
    def __init__(self, x, y, rotation, color, scene, parent):
        super().__init__(parent)
        self.startX = x
        self.startY = y
        self.color = color
        self.circles = []

        self.rect = scene.addRect(QRectF(self.startX, self.startY, 240, 240))
        self.rect.setPen(QPen(Qt.black, 2.0))
        self.rect.setBrush(QBrush(self.color))

        self.hiliteRect = scene.addRect(QRectF(self.startX+10, self.startY+10, 220, 220))
        self.hiliteRect.setPen(QPen(Qt.white, 4.0))
        self.hiliteRect.setVisible(False)

        c1 = scene.addEllipse(self.startX+40, self.startY+40, 60, 60)
        c1.setPen(QPen(Qt.black, 2.0))
        c1.setBrush(QBrush(Qt.white))
        self.circles.append(c1)

        c2 = scene.addEllipse(self.startX+140, self.startY+40, 60, 60)
        c2.setPen(QPen(Qt.black, 2.0))
        c2.setBrush(QBrush(Qt.white))
        self.circles.append(c2)

        c3 = scene.addEllipse(self.startX+40, self.startY+140, 60, 60)
        c3.setPen(QPen(Qt.black, 2.0))
        c3.setBrush(QBrush(Qt.white))
        self.circles.append(c3)

        c4 = scene.addEllipse(self.startX+140, self.startY+140, 60, 60)
        c4.setPen(QPen(Qt.black, 2.0))
        c4.setBrush(QBrush(Qt.white))
        self.circles.append(c4)


        T = QPolygonF()
        T.append(QPointF(240, 240))
        T.append(QPointF(240, 360))
        T.append(QPointF(300, 300))
        T.append(QPointF(240, 240))
        self.triangle = scene.addPolygon(T)
        self.triangle.setPen(QPen(Qt.black, 2.0))
        self.triangle.setBrush(QBrush(color))
        self.triangle.setTransformOriginPoint(QPointF(300, 300))
        self.triangle.setRotation(rotation)

    def getHomeField(self):
        return self.circles

    def getEndZone(self):
        return self.triangle

    def getHiliteRect(self):
        return self.hiliteRect


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
