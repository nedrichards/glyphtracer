#!/usr/bin/python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from editor import Ui_MainWindow

def calculate_horizontal_cuts(image):
    (w, h) = (image.width(), image.height())
    sums = []
    for j in xrange(h):
        total = 0
        for i in xrange(w):
            total += image.pixelIndex(i, j)
        sums.append(total)
    return sums
    
def calculate_cutlines_locations(sums):
    element_strips = []
    cutoff = 0
    
    if sums[0] <= cutoff:
        background_strip = True
    else:
        background_strip = False
    strip_start = 0
    
    for i in xrange(len(sums)):
        if sums[i] <= cutoff:
            background = True
        else:
            background = False
        if background == background_strip:
            continue
        
        # We crossed a region.
        if background:
           strip_end = i-1;
           element_strips.append((strip_start, strip_end))
        strip_start = i
        background_strip = background
          
    if strip_start < len(sums) and not background_strip:
        strip_end = len(sums) - 1
        element_strips.append((strip_start, strip_end))
    return element_strips

def calculate_letter_boxes(image, xstrips):
    boxes = []
    (w, h) = (image.width(), image.height())
    rotate = QMatrix().rotate(90)
    for xs in xstrips:
        (y0, y1) = xs
        cur_image = image.copy(0, y0, w, y1-y0).transformed(rotate)
        ystrips = calculate_cutlines_locations(calculate_horizontal_cuts(cur_image))
        for ys in ystrips:
            (x0, x1) = ys
            box = LetterBox(QRect(x0, y0, x1-x0, y1-y0))
            boxes.append(box)
    return boxes


class LetterBox():
    def __init__(self, rectangle):
        self.r = rectangle
        self.taken = False

class Window(QWidget):
    def __init__(self, image_file, parent = None):
        QWidget.__init__(self, parent)
        self.resize(640, 480)
        self.image = QImage(image_file)
        strips = calculate_horizontal_cuts(self.image)
        hor_lines = calculate_cutlines_locations(strips)
        self.boxes = calculate_letter_boxes(self.image, hor_lines)

    def paintEvent(self, event):
        w = self.image.width()
        paint = QPainter()
        paint.begin(self)
        paint.drawImage(0, 0, self.image)
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        paint.setPen(pen)
        b = QBrush(QColor(0, 0, 0, 127))
        for box in self.boxes:
            paint.drawRect(box.r)
            if box.taken:
                paint.fillRect(box.r, b)
        #paint.setPen(pen)
        paint.end()

     
class StartDialog(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.resize(512, 200)
        
        self.grid = QGridLayout()
        self.name_edit = QLineEdit('Foobar')
        self.file_edit = QLineEdit()
        self.file_button = QPushButton('Browse')
        self.combo = QComboBox()
        self.combo.addItem('Regular')
        self.combo.addItem('Bold')
        self.combo.addItem('Italic')
        self.combo.addItem('BoldItalic')
        
        self.grid.setSpacing(10)
        self.grid.addWidget(QLabel('Font name'), 0, 0)
        self.grid.addWidget(self.name_edit, 0, 1, 1, 2)
        self.grid.addWidget(QLabel('Type'), 1, 0)
        self.grid.addWidget(self.combo, 1, 1, 1, 2)
        self.grid.addWidget(QLabel('Image file'), 2, 0)
        self.grid.addWidget(self.file_edit, 2, 1)
        self.grid.addWidget(self.file_button, 2, 2)
        
        hbox = QHBoxLayout()
        start_button = QPushButton('Start')
        hbox.addWidget(start_button)
        quit_button = QPushButton('Quit')
        hbox.addWidget(quit_button)
        w = QWidget()
        w.setLayout(hbox)
        self.grid.addWidget(w, 3, 0, 1, 3)
        
        self.setLayout(self.grid)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    #myapp = Window(sys.argv[1])
    myapp = StartDialog()
    myapp.show()
    sys.exit(app.exec_())
