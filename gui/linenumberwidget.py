from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

class LineNumberWidget(QWidget):
    def __init__(self, text_edit):
        super().__init__(text_edit)
        self.text_edit = text_edit
        self.setFont(text_edit.font())  # Use the same font as QTextEdit
        self.setFixedWidth(50)  # Set fixed width for line number column
        self.setAutoFillBackground(True)
        
        # Connect the text edit to trigger update on text change
        self.text_edit.textChanged.connect(self.update_line_numbers)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.lightGray)  # Background color for line numbers
        doc = self.text_edit.document()
        block = doc.begin()
        line_number = 1

        while block.isValid():
            # Get the block's bounding rect (we already use the correct method)
            rect = self.text_edit.document().documentLayout().blockBoundingRect(block)
            
            # Get the content offset
            offset = self.text_edit.viewport().pos()  # This gives the scroll offset
            rect = rect.translated(offset)  # Apply the scroll offset

            if rect.top() > self.height():
                break
            
            # Use int() to cast the float to an int for the y-coordinate
            painter.setPen(Qt.black)
            painter.drawText(0, int(rect.top()) + 15, str(line_number))  # Ensure y-coordinate is an int
            
            block = block.next()
            line_number += 1

    def update_line_numbers(self):
        """Trigger a repaint only when the text changes"""
        self.update()  # Request an update to trigger the repaint only when text changes
