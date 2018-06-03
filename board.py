from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gui import Field, StartField, EndField, LastField, SafeField, SpecialField, HomeField
import resources

class Board(QWidget):
    def __init__(self):
        super().__init__()

        self.view = QGraphicsView()
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHint(QPainter.Antialiasing)

        self.rect = self.scene.addRect(QRectF(0, 0, 600, 600))
        self.rect.setPen(QPen(Qt.black, 2.0))

        self.end = self.scene.addRect(QRectF(240, 240, 120, 120))
        self.end.setPen(QPen(Qt.black, 2.0))
        self.fields = []
        self.starts = []

        index = 0

        for x in range(0, 240, 40):
            box = Field(x, 240, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            self.fields.append(box)

        for y in range(200, -1, -40):
            box = Field(240, y, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            self.fields.append(box)


        box = LastField(280, 0, 40, 40)
        box.setIndex(index)
        index += 1
        box.setColor(QColor(85, 107, 47))
        self.scene.addItem(box)
        self.fields.append(box)

        for y in range(0, 240, 40):
            box = Field(320, y, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            self.fields.append(box)

        for x in range(360, 600, 40):
            box = Field(x, 240, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            self.fields.append(box)

        box = LastField(560, 280, 40, 40)
        box.setIndex(index)
        index += 1
        box.setColor(QColor(218, 165, 32))
        self.scene.addItem(box)
        self.fields.append(box)

        for x in range(560, 359, -40):
            box = Field(x, 320, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            self.fields.append(box)

        for y in range(360, 600, 40):
            box = Field(320, y, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            self.fields.append(box)

        box = LastField(280, 560, 40, 40)
        box.setIndex(index)
        index += 1
        box.setColor(QColor(0, 191, 255))
        self.scene.addItem(box)
        self.fields.append(box)

        for y in range(560, 359, -40):
            box = Field(240, y, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            self.fields.append(box)

        for x in range(200, -1, -40):
            box = Field(x, 320, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            self.fields.append(box)

        box = LastField(0, 280, 40, 40)
        box.setIndex(index)
        index += 1
        box.setColor(QColor(205, 92, 92))
        self.scene.addItem(box)
        self.fields.append(box)

        for x in range(40, 240, 40):
            box = SafeField(x, 280, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            box.setColor(QColor(205, 92, 92))
            self.fields.append(box)

        for y in range(40, 240, 40):
            box = SafeField(280, y, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            box.setColor(QColor(85, 107, 47))
            self.fields.append(box)

        for x in range(520, 359, -40):
            box = SafeField(x, 280, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            box.setColor(QColor(218, 165, 32))
            self.fields.append(box)

        for y in range(520, 359, -40):
            box = SafeField(280, y, 40, 40)
            box.setIndex(index)
            index += 1
            self.scene.addItem(box)
            box.setColor(QColor(0, 191, 255))
            self.fields.append(box)

        self.diceBox = self.scene.addRect(270, 270, 60, 60)
        self.diceBox.setVisible(False)

        self.drawSpecial(1, 'red')
        self.drawSpecial(14, 'green')
        self.drawSpecial(27, 'yellow')
        self.drawSpecial(40, 'blue')

        self.drawSpecial(9)
        self.drawSpecial(22)
        self.drawSpecial(35)
        self.drawSpecial(48)

        self.home_fields = []
        redHome = HomeField(0, 0, 0, QColor(205, 92, 92), self.scene, self)
        self.addStartFields(redHome, 1)
        self.home_fields.append(redHome)

        greenHome = HomeField(360, 0, 90, QColor(85, 107, 47), self.scene, self)
        self.addStartFields(greenHome, 14)
        self.home_fields.append(greenHome)

        yellowHome = HomeField(360, 360, 180, QColor(218, 165, 32), self.scene, self)
        self.addStartFields(yellowHome, 27)
        self.home_fields.append(yellowHome)

        blueHome = HomeField(0, 360, 270, QColor(0, 191, 255), self.scene, self)
        self.addStartFields(blueHome, 40)
        self.home_fields.append(blueHome)

        self.end_fields = []
        endRed = EndField(240, 285, 30, 30)
        self.scene.addItem(endRed)
        self.end_fields.append(endRed)

        endGreen = EndField(285, 240, 30, 30)
        self.scene.addItem(endGreen)
        self.end_fields.append(endGreen)

        endYellow = EndField(330, 285, 30, 30)
        self.scene.addItem(endYellow)
        self.end_fields.append(endYellow)

        endBlue = EndField(285, 330, 30, 30)
        self.scene.addItem(endBlue)
        self.end_fields.append(endBlue)

        self.setupNextField()
        self.setupPreviousField()
        self.setupNextSafeZone()

        vLayout = QVBoxLayout()
        self.setLayout(vLayout)
        vLayout.addWidget(self.view)

    def setupNextField(self):
        ends = {56:0, 61:1, 66:2, 71:3}
        for id, box in enumerate(self.fields):
            if id not in ends.keys():
                next_id = 0 if id == 51 else id+1
                box.setNextField(self.fields[next_id])
            else:
                box.setNextField(self.end_fields[ends[id]])

    def setupPreviousField(self):
        for id, box in enumerate(self.fields):
            prev_id = 51 if id < 1 else id-1
            box.setPreviousField(self.fields[prev_id])

    def addStartFields(self, homeField, next_index):
        circles = homeField.getHomeField()
        starts = []
        for circle in circles:
            box = StartField(circle.boundingRect())
            box.setNextField(self.fields[next_index])
            starts.append(box)
            self.scene.addItem(box)
        self.starts.append(starts)

    def setupNextSafeZone(self):
        end_safe_pairs = [(51, 52), (12, 57), (25, 62), (38, 67)]
        for index, safe_index in end_safe_pairs:
            box = self.fields[index]
            box.setSafeField(self.fields[safe_index])

    def drawSpecial(self, index, color='black'):
        brect = self.fields[index].boundingRect()
        idx = self.fields[index].getIndex()
        self.fields[index] = None

        box = SpecialField(brect)
        box.setIndex(idx)
        pmap = QPixmap(":/images/star")
        if color != 'black':
            pmap = QPixmap(":/images/star-{}".format(color))
        pmap = pmap.scaled(QSize(30, 30), Qt.KeepAspectRatio)
        pmap_item = QGraphicsPixmapItem(pmap)
        pmap_item.setPos(brect.topLeft().x()+5.0, brect.topLeft().y()+5.0)
        self.scene.addItem(box)
        self.scene.addItem(pmap_item)
        self.fields[index] = box

    def getHome(self, index):
        if index < 4:
            return self.home_fields[index]
        return None

    def getStartField(self, index):
        if index < 4:
            return self.starts[index]
        return None

    def getDiceBox(self):
        return self.diceBox

    def getScene(self):
        return self.scene
