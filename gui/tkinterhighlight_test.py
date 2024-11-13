import sys
import os
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit

# Set the platform to 'xcb' (X11) to avoid the Wayland plugin error
os.environ['QT_QPA_PLATFORM'] = 'xcb'

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlightingRules = []

        # Custom 6502 instructions
        instructions = ['LDA', 'LDX', 'LDY', 'STA', 'STX', 'STY', 'ADC', 'SBC', 'CMP', 'CPX', 'CPY']
        custom_keywords = r'(' + r'|'.join([r'\b' + inst + r'\b' for inst in instructions]) + r')'

        # Regular expressions for 6502 addresses and special characters
        address_pattern = r'\$[0-9A-Fa-f]{4}'  # 6502 address in hex format (e.g., $2000)
        special_characters = r'[#$]'  # Match $ or # (common in 6502)

        # Define highlighting rules
        self.addHighlightingRule(custom_keywords, Qt.red)  # 6502 instructions (Red)
        self.addHighlightingRule(address_pattern, Qt.blue)  # 6502 addresses (Blue)
        
        # Define orange color using QColor (RGB for orange)
        orange_color = QColor(255, 165, 0)
        self.addHighlightingRule(special_characters, orange_color)  # Special chars (Orange)

    def addHighlightingRule(self, pattern, color):
        """Helper function to add highlighting rule."""
        format = QTextCharFormat()
        format.setForeground(color)
        rule = (QRegExp(pattern), format)
        self.highlightingRules.append(rule)

    def highlightBlock(self, text):
        """Override the base method to apply syntax highlighting."""
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("6502 Syntax Highlighter")
        self.setGeometry(100, 100, 800, 600)

        # Create a QTextEdit widget
        self.textEdit = QTextEdit(self)
        self.setCentralWidget(self.textEdit)

        # Create a SyntaxHighlighter instance for the QTextEdit
        highlighter = SyntaxHighlighter(self.textEdit.document())

        # Example text (including 6502 code)
        example_text = """LDA $2000
ADC $3000
STA $4000
LDX $5000
# Comment line
"""
        self.textEdit.setPlainText(example_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
