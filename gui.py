from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import resources
import random

class DiceButton(QPushButton):
    pressed = pyqtSignal(int)
    def __init__(self, dice, parent=None):
        super().__init__(str(dice), parent)
        self.dice = dice

    def mousePressEvent(self, mouse_event):
        self.pressed.emit(self.dice)
        QPushButton.mousePressEvent(self, mouse_event)

class DiceWidget(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = False
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
        self.dice = []
        self.graphics_rotation = QGraphicsRotation()
        self.graphics_rotation.setAxis(Qt.YAxis)
        self.graphics_rotation.setAngle(0)
        self.graphics_rotation.setOrigin(QVector3D(QPointF(35, 35)))
        self.setTransformations([self.graphics_rotation])

        self.animation = QPropertyAnimation(self.graphics_rotation, b"angle")
        self.animation.setDuration(500)
        self.animation.setStartValue(self.graphics_rotation.angle())
        self.animation.setEndValue(360)
        self.animation.finished.connect(self.throwDice)

    def mousePressEvent(self, mouse_event):
        if not self.enabled: return
        QGraphicsPixmapItem.mousePressEvent(self, mouse_event)

    def throwDice(self):
        self.dice.append(random.randint(1, 6))
        self.c.dice_updated.emit(self.dice)
        self.setPixmap(self.images[self.dice[-1]])
        if self.dice[-1] == 6:
            if len(self.dice) > 2 and all([d==6 for d in self.dice[-3:]]):
                self.dice = self.dice[:-3]
                self.c.three_sixes_message.emit()
            self.delay(1)
            self.roll()
        else:
            self.enabled = False
            self.c.dice_rolled.emit(self.dice)

    def resetDice(self):
        self.setPixmap(self.images[0])
        self.dice = []
        self.enabled = True

    def roll(self):
        if not self.enabled: return
        self.setPixmap(self.images[0])
        self.animation.start()

    def setEnabled(self, enabled):
        self.enabled = enabled

    def value(self):
        return self.dice

    def delay(self, time_in_sec=1.0):
        dice_time = QTime.currentTime().addSecs(time_in_sec)
        while QTime.currentTime() < dice_time:
            QCoreApplication.processEvents(QEventLoop.AllEvents, 100)

class Figure(QGraphicsEllipseItem):
    def __init__(self, diameter, parent=None):
        super().__init__(0.0, 0.0, diameter, diameter, parent)
        self.diameter = diameter
        self.enabled = False
        self.dice_value = 0
        self.hilight = None
        self.current_position = None
        self.start_position = None
        self.color = None
        self.result_position = None
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

    def getColor(self):
        return self.color

    def setColor(self, color):
        self.color = color
        self.setBrush(QBrush(self.color))

    def setPosition(self, position):
        self.unhilightField(self)
        if self.current_position: self.current_position.removeFigure(self)
        self.current_position = position
        self.current_position.addFigure(self)

    def setStartPosition(self, position):
        self.start_position = position

    def getPosition(self):
        return self.current_position

    def getResultPosition(self):
        return self.result_position

    def getDiameter(self):
        return self.diameter

    def setDiameter(self, diameter):
        self.diameter = diameter
        self.setRect(0, 0, diameter, diameter)

    def enableIfPossible(self, dice):
        enabled = False
        if isinstance(self.current_position, EndField):
            return enabled
        if isinstance(self.current_position, StartField):
            if dice == 6:
                self.setEnabled(True)
                self.dice_value = dice
                enabled = True
                self.result_position = self.current_position.next(self.color)
            return enabled

        self.result_position = self.findResultPosition(dice)
        if self.result_position:
            if self.result_position.isSpecial():
                self.setEnabled(True)
                self.dice_value = dice
                enabled = True
            else:
                figs = self.result_position.getFigures()
                if len(figs) > 0:
                    existing_color = figs[0].getColor()
                    if self.color != existing_color:
                        self.setEnabled(True)
                        self.dice_value = dice
                        enabled = True
                else:
                    self.setEnabled(True)
                    self.dice_value = dice
                    enabled = True
        return enabled

    def countValidFigures(self, dice):
        count = 0
        if isinstance(self.current_position, EndField):
            return count
        if isinstance(self.current_position, StartField):
            if dice == 6:
                count += 1
            return count

        result_position = self.findResultPosition(dice)
        if result_position:
            if result_position.isSpecial():
                count += 1
            else:
                figs = result_position.getFigures()
                if len(figs) > 0:
                    existing_color = figs[0].getColor()
                    if self.color != existing_color:
                        count += 1
                else:
                    print("reg field")
                    count += 1
        return count

    def findResultPosition(self, dice):
        result_position = None

        result_position_temp = self.current_position
        while dice > 0:
            dice -= 1
            if result_position_temp:
                result_position_temp = result_position_temp.next(self.color)
            else:
                break
        if dice == 0 and result_position_temp:
            return result_position_temp
        return result_position

    def getHilight(self):
        return self.hilight

    def moveToHome(self):
        self.setPosition(self.start_position)

class Communicate(QObject):
    enter = pyqtSignal(Figure)
    leave = pyqtSignal(Figure)
    clicked = pyqtSignal(Figure)
    moved = pyqtSignal(Figure)
    three_sixes_message = pyqtSignal()
    dice_rolled = pyqtSignal(list)
    dice_updated = pyqtSignal(list)

class Field(QGraphicsRectItem):
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.index = -1
        self.name = "Normal"
        self.setPen(QPen(Qt.black, 2.0))
        self.is_special = False
        self.next_field = None
        self.prev_field = None
        self.figures = []
        self.text = None

    def setNextField(self, field):
        self.next_field = field

    def setPreviousField(self, field):
        self.prev_field = field

    def next(self, color):
        return self.next_field

    def previous(self):
        return self.prev_field

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
            scene.removeItem(self.text)
            self.text = None

        for fig in self.figures:
            fig_count += 1
            scene.removeItem(fig)
            center = self.boundingRect().center()
            fig.setDiameter(24.0)
            fig_radius = 0.5 * fig.getDiameter()
            top_left = center - QPointF(fig_radius, fig_radius)
            fig.setPos(top_left)
            scene.addItem(fig)

        if fig_count > 1:
            self.text = QGraphicsTextItem()
            fig = self.figures[0]
            fig_radius = 0.5 * fig.getDiameter()
            center = self.boundingRect().center()
            top_left = center - QPointF(fig_radius*0.65, fig_radius*0.85)
            self.text.setPos(top_left)
            self.text.setFont(QFont("Times", 15, QFont.Bold))
            self.text.setPlainText(str(fig_count))
            scene.addItem(self.text)

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
        self.name = "Start"

class SpecialField(Field):
    def __init__(self, rect, parent=None):
        super().__init__(rect.x()+1.0, rect.y()+1.0, rect.width()-2.0, rect.height()-2.0, parent)
        self.name = "Start"
        self.color_counts = [0, 0, 0, 0]
        self.num_fig_colors = 0
        self.texts = [None, None, None, None]
        self.colors =[QColor(205, 92, 92), QColor(85, 107, 47), QColor(218, 165, 32), QColor(0, 191, 255)]
        self.is_special = True
        self.setBrush(QBrush(Qt.lightGray))
        self.shifts = [QPointF(-10.0, -10.0), QPointF(10.0, -10.0), QPointF(10.0, 10.0), QPointF(-10.0, 10.0)]

    def addFigure(self, fig):
        color = fig.getColor()
        index = self.colors.index(color)
        if self.color_counts[index] == 0: self.num_fig_colors += 1
        self.color_counts[index] += 1
        super().addFigure(fig)

    def removeFigure(self, fig):
        color = fig.getColor()
        index = self.colors.index(color)
        if self.color_counts[index] == 1: self.num_fig_colors -= 1
        self.color_counts[index] -= 1
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

        if self.num_fig_colors == 1:
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
            fig_radius = 0.5 * fig.getDiameter()
            top_left = center - QPointF(fig_radius, fig_radius)
            fig.setPos(top_left)
            scene.addItem(fig)

        for index in range(4):
            count = self.color_counts[index]
            if count > 1:
                text = QGraphicsTextItem()
                center = self.boundingRect().center()
                center = self.get_new_center(center, index)
                fig_radius = 0.5 * fig.getDiameter()
                top_left = center - QPointF(fig_radius*0.90, fig_radius*1.10)
                text.setPos(top_left)
                text.setFont(QFont("Times", 12, QFont.Bold))
                text.setPlainText(str(count))
                scene.addItem(text)
                self.texts[index] = text

    def get_new_center(self, center, index):
        return center+self.shifts[index]

class SafeField(Field):
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.color = QColor()
        self.name = "Safe"

    def setColor(self, color):
        self.color = color
        self.setBrush(QBrush(self.color))

class LastField(Field):
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.color = QColor()
        self.next_safe_field = None
        self.name = "Last"

    def setColor(self, color):
        self.color = color

    def getColor(self):
        return self.color

    def setSafeField(self, field):
        self.next_safe_field = field

    def next(self, color):
        if color == self.color: return self.next_safe_field
        return self.next_field

class EndField(Field):
    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.setVisible(False)
        self.is_special = True
        self.name = "End"

    def drawFigures(self):
        scene = self.scene()

        fig_count = 0
        if self.text:
            scene.removeItem(self.text)
            self.text = None

        for fig in self.figures:
            fig_count += 1
            scene.removeItem(fig)
            center = self.boundingRect().center()
            fig.setDiameter(18.0)
            fig_radius = 0.5 * fig.getDiameter()
            top_left = center - QPointF(fig_radius, fig_radius)
            fig.setPos(top_left)
            scene.addItem(fig)

        if fig_count > 1:
            self.text = QGraphicsTextItem()
            fig = self.figures[0]
            fig_radius = 0.5 * fig.getDiameter()
            center = self.boundingRect().center()
            top_left = center - QPointF(fig_radius*0.85, fig_radius)
            self.text.setPos(top_left)
            self.text.setFont(QFont("Times", 13, QFont.Bold))
            self.text.setPlainText(str(fig_count))
            scene.addItem(self.text)

class HomeField(QObject):
    def __init__(self, x, y, rotation, color, scene, parent=None):
        super().__init__(parent)
        self.name = "Home"
        self.startX = x
        self.startY = y
        self.color = color
        self.circles = []

        self.rect = scene.addRect(QRectF(self.startX, self.startY, 240, 240))
        self.rect.setPen(QPen(Qt.black, 2.0))
        self.rect.setBrush(QBrush(self.color))

        self.hilighted_rect = scene.addRect(QRectF(self.startX+10, self.startY+10, 220, 220))
        self.hilighted_rect.setPen(QPen(Qt.white, 4.0))
        self.hilighted_rect.setVisible(False)

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

    def getHilightedRect(self):
        return self.hilighted_rect


class OnDemandSpacer(QWidget):
    def __init__(self):
        super().__init__()

        horizontal_layout = QHBoxLayout()
        self.spacer = QSpacerItem(150, 12, QSizePolicy.Fixed, QSizePolicy.Fixed)

        horizontal_layout.addSpacerItem(self.spacer)
        self.setLayout(horizontal_layout)

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
        self.computer_option = QRadioButton("Computer")
        self.human_option = QRadioButton("Human")
        self.player_name = QLineEdit()
        self.spacer = OnDemandSpacer()
        self.h_layout = QHBoxLayout()

        self.computer_option.setChecked(True)
        self.human_option.setChecked(False)

        self.player_name.setPlaceholderText("Enter player name...")
        self.player_name.setClearButtonEnabled(True)
        self.player_name.setVisible(False)
        self.player_name.setFixedWidth(180)

        self.spacer.setVisible(True)
        self.spacer.setFixedWidth(180)

        self.h_layout.addWidget(self.icon)
        self.h_layout.addWidget(self.computer_option)
        self.h_layout.addWidget(self.human_option)
        self.h_layout.addWidget(self.player_name)
        self.h_layout.addWidget(self.spacer)

        self.human_option.toggled.connect(self.player_name.setVisible)
        self.human_option.toggled.connect(self.spacer.setHidden)

        self.setLayout(self.h_layout)

    def getPlayerName(self):
        return self.player_name

    def getComputerOption(self):
        return self.computer_option

    def getHumanOption(self):
        return self.human_option


class NewGameDialog(QDialog):
    trigger = pyqtSignal(list)
    def __init__(self, title):
        super().__init__()

        self.ok_button = QPushButton("Start Demo")
        self.ok_button.setEnabled(True)
        self.ok_button.setDefault(True)
        self.cancel_button = QPushButton("Cancel")
        self.spacer = OnDemandSpacer()
        self.h_layout_button = QHBoxLayout()
        self.buttons = QWidget()

        self.player_list = []
        self.player_list.append(PlayerOption(QColor(205, 92, 92)))
        self.player_list.append(PlayerOption(QColor(85, 107, 47)))
        self.player_list.append(PlayerOption(QColor(218, 165, 32)))
        self.player_list.append(PlayerOption(QColor(0, 191, 255)))

        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.buttons)
        self.v_layout.setSizeConstraint(QLayout.SetFixedSize)
        for player in self.player_list:
            self.v_layout.addWidget(player)

        self.h_layout_button.addWidget(self.spacer)
        self.h_layout_button.addWidget(self.ok_button)
        self.h_layout_button.addWidget(self.cancel_button)
        self.buttons.setLayout(self.h_layout_button)

        self.setWindowTitle(title)
        self.setLayout(self.v_layout)
        self.setModal(True)

        self.cancel_button.clicked.connect(self.close)
        self.ok_button.clicked.connect(self.savePlayerData)

        for player in self.player_list:
            field = player.getPlayerName()
            field.textChanged.connect(self.enableOKButton)
            computer_option = player.getComputerOption()
            computer_option.toggled.connect(self.enableOKButton)

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
        if valid_names != len(player_names): ok = False

        button_title = "Start Demo"
        if any_human: button_title = "Start Game"
        self.ok_button.setText(button_title)
        self.ok_button.setEnabled(ok)

    def savePlayerData(self):
        player_data = []
        for player in self.player_list:
            is_human = player.getHumanOption().isChecked()
            name = player.getPlayerName().text() if is_human else ""
            player_data.append((is_human, name))
        self.accept()
        self.trigger.emit(player_data)
