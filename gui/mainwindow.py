import os
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QHBoxLayout, QWidget

from syntaxhighlighter import SyntaxHighlighter
from linenumberwidget import LineNumberWidget

os.environ["QT_QPA_PLATFORM"] = "xcb"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("6502 Syntax Highlighter")
        self.setGeometry(100, 100, 800, 600)

        # Font setup
        font_path = os.path.join(os.getcwd(), 'gui', 'fonts', 'iosevka-regular.ttf')
        print(f"Font path: {font_path}")

        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id == -1:
            print(f"failed to find font! at path: {font_path}")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"loaded font: {font_family}")

        font = QFont(font_family)
        font.setPointSize(16)

        # Create a QWidget for the central layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create the QTextEdit widget
        self.textEdit = QTextEdit(self)
        self.textEdit.setFont(font)

        # Create the line number widget
        self.line_number_widget = LineNumberWidget(self.textEdit)

        # Connect the textChanged signal AFTER the textEdit is initialized
        self.textEdit.textChanged.connect(self.on_text_changed)

        # Create a SyntaxHighlighter instance for the QTextEdit
        self.highlighter = SyntaxHighlighter(self.textEdit)

        # Create the update timer BEFORE connecting it
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(100)  # 100 ms interval
        self.update_timer.timeout.connect(self.on_update_timeout)

        # Set up the layout
        layout = QHBoxLayout(central_widget)
        layout.addWidget(self.line_number_widget)
        layout.addWidget(self.textEdit)

        # Set some example text
        example_text = """LDA $2000
ADC $3000
STA $4000
LDX $5000
; Comment line
"""
        self.textEdit.setPlainText(example_text)

        # Flag to control if update is needed
        self.is_text_changed = False

    def on_text_changed(self):
        """Handle text changes and trigger highlighting and line number updates."""
        self.is_text_changed = True
        self.update_timer.start()  # Start the timer to handle updates

    def on_update_timeout(self):
        """Called when the timer times out, used to handle line number and rehighlighting updates."""
        if self.is_text_changed:
            self.highlighter.rehighlight()  # Rehighlight the text
            self.line_number_widget.update()  # Update the line numbers
            self.is_text_changed = False
        self.update_timer.stop()  # Stop the timer to avoid repeated calls

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
