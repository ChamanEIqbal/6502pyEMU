import os
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontDatabase, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QHBoxLayout, QWidget, QMenuBar, QAction, QFileDialog, QStatusBar, QLabel, QShortcut

from syntaxhighlighter import SyntaxHighlighter
from linenumberwidget import LineNumberWidget
from debugger import DebuggerWindow
from linesplitter import LineSplitter

os.environ["QT_QPA_PLATFORM"] = "xcb"

class MainWindow(QMainWindow):
    def __init__(self, api_url):
        super().__init__()

        print("Initializing MainWindow")

        self.setWindowTitle("6502 Emulator v0.0.2")
        self.setGeometry(100, 100, 800, 600)

        # Font setup
        font_path = os.path.join(os.getcwd(), 'fonts', 'iosevka-regular.ttf')
        print(f"Font path: {font_path}")

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to find font! at path: {font_path}")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"Loaded font: {font_family}")

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

        # Initialize current_file as None (for untitled files)
        self.current_file = None
        print(f"current_file initialized to: {self.current_file}")

        # Flag to control if update is needed
        self.is_text_changed = False

        # Set up status bar
        self.statusBar = self.statusBar()
        self.file_name_label = QLabel("Untitled*")  # Initial label for untitled
        self.file_name_label.setStyleSheet("QLabel {background-color: #333333; color:white;}")
        self.statusBar.addWidget(self.file_name_label)

        # Set up menu actions
        self.api_url = api_url  # Store the API URL for the debugger
        self.setup_menu()

        # Add shortcut for line splitting (Ctrl + P)
        self.split_lines_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.split_lines_shortcut.activated.connect(self.split_text_lines)

    def setup_menu(self):
        """Set up the menu bar with File actions (New, Open, Save)."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        debugger_menu = menu_bar.addMenu("Debugger")

        # Debugger action
        open_debugger_action = QAction("Open Debugger", self)
        open_debugger_action.triggered.connect(self.open_debugger)
        debugger_menu.addAction(open_debugger_action)

        # Create the File menu
        # Create the New action
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")  # Set shortcut for New file (Ctrl+N)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        # Create the Open action
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")  # Set shortcut for Open file (Ctrl+O)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Create the Save action
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")  # Set shortcut for Save file (Ctrl+S)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # Optionally, add an exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def new_file(self):
        """Clear the current text and reset the file state for a new file."""
        if self.is_text_changed and self.current_file is None:
            response = QFileDialog.question(self, "Unsaved Changes", 
                                            "You have unsaved changes. Do you want to save them?",
                                            QFileDialog.Yes | QFileDialog.No | QFileDialog.Cancel)
            if response == QFileDialog.Yes:
                self.save_file()
            elif response == QFileDialog.Cancel:
                return

        self.textEdit.clear()
        self.current_file = None
        self.is_text_changed = False
        self.update_file_name_label()

    def open_file(self):
        """Open a file using QFileDialog."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "ASM Files (*.asm);;Text Files (*.txt);;All Files (*)")
        if file_name:
            with open(file_name, "r") as file:
                file_content = file.read()
                self.textEdit.setPlainText(file_content)
            self.current_file = file_name
            self.is_text_changed = False
            self.update_file_name_label()

    def save_file(self):
        """Save the current content of the QTextEdit to a file."""
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.textEdit.toPlainText())
            self.is_text_changed = False
            self.update_file_name_label()
        else:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "ASM Files (*.asm);;Text Files (*.txt);;All Files (*)")
            if file_name:
                with open(file_name, "w") as file:
                    file.write(self.textEdit.toPlainText())
                self.current_file = file_name
                self.is_text_changed = False
                self.update_file_name_label()

    def update_file_name_label(self):
        """Update the status bar label to show the current file name or 'Untitled'."""
        if self.current_file:
            file_name = os.path.basename(self.current_file)
            self.file_name_label.setText(file_name)
        else:
            self.file_name_label.setText("Untitled" + ("*" if self.is_text_changed else ""))

    def open_debugger(self):
        self.debugger_window = DebuggerWindow(self.api_url)
        self.debugger_window.update_cpu_table()
        self.debugger_window.update_memory_view()
        self.debugger_window.show()

    def on_text_changed(self):
        self.is_text_changed = True
        self.update_timer.start()
        self.update_file_name_label()

    def on_update_timeout(self):
        if self.is_text_changed:
            self.highlighter.rehighlight()
            self.line_number_widget.update()
            self.is_text_changed = False
        self.update_timer.stop()

    def split_text_lines(self):
        """Splits the text in the QTextEdit and prints it to the console."""
        text = self.textEdit.toPlainText()
        LineSplitter.split_lines(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    API_URL = "http://127.0.0.1:5000"
    window = MainWindow(API_URL)
    window.show()
    sys.exit(app.exec_())