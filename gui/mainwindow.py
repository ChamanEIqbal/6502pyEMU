import os
import sys
from PyQt5.QtCore import Qt, QTimer, QFile
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QHBoxLayout, QWidget, QMenuBar, QAction, QFileDialog, QStatusBar, QLabel

from syntaxhighlighter import SyntaxHighlighter
from linenumberwidget import LineNumberWidget
from debugger import DebuggerWindow

os.environ["QT_QPA_PLATFORM"] = "xcb"

class MainWindow(QMainWindow):
    def __init__(self, api_url):
        super().__init__()

        print("Initializing MainWindow")

        self.setWindowTitle("6502 Syntax Highlighter")
        self.setGeometry(100, 100, 800, 600)

        # Font setup
        font_path = os.path.join(os.getcwd(), 'fonts', 'iosevka-regular.ttf')
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
        # Check if the current file is unsaved
        if self.is_text_changed and self.current_file is None:
            response = QFileDialog.question(self, "Unsaved Changes", 
                                            "You have unsaved changes. Do you want to save them?",
                                            QFileDialog.Yes | QFileDialog.No | QFileDialog.Cancel)
            if response == QFileDialog.Yes:
                self.save_file()  # Save before creating new file
            elif response == QFileDialog.Cancel:
                return  # Don't create a new file if the user cancels

        # Clear the text editor and reset the file state
        self.textEdit.clear()
        self.current_file = None  # No file saved yet
        self.is_text_changed = False
        self.update_file_name_label()  # Update the label to show "Untitled*"

    def open_file(self):
        """Open a file using QFileDialog."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "ASM Files (*.asm);;Text Files (*.txt);;All Files (*)")

        if file_name:
            with open(file_name, "r") as file:
                file_content = file.read()
                self.textEdit.setPlainText(file_content)
            self.current_file = file_name  # Store the current file name
            self.is_text_changed = False  # Reset unsaved change flag
            self.update_file_name_label()  # Update the label with the file name

    def save_file(self):
        """Save the current content of the QTextEdit to a file."""
        if self.current_file:
            # If there's already a file, save to it
            with open(self.current_file, "w") as file:
                file.write(self.textEdit.toPlainText())
            self.is_text_changed = False  # Reset the unsaved change flag
            self.update_file_name_label()  # Update the label to reflect saved file name
        else:
            # If no file is currently saved, use QFileDialog to select where to save
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "ASM Files (*.asm);;Text Files (*.txt);;All Files (*)")
            if file_name:
                with open(file_name, "w") as file:
                    file.write(self.textEdit.toPlainText())
                self.current_file = file_name  # Store the saved file name
                self.is_text_changed = False  # Reset the unsaved change flag
                self.update_file_name_label()  # Update the label with the file name

    def update_file_name_label(self):
        """Update the status bar label to show the current file name or 'Untitled'."""
        if hasattr(self, 'current_file'):
            if self.current_file:
                file_name = os.path.basename(self.current_file)
                self.file_name_label.setText(file_name)
            else:
                self.file_name_label.setText("Untitled" + ("*" if self.is_text_changed else ""))
        else:
            print("current_file not initialized yet.")

    def open_debugger(self):
        self.debugger_window = DebuggerWindow(self.api_url)  # Pass API URL to the debugger
        self.debugger_window.update_cpu_table()  # Update CPU table with current state
        self.debugger_window.update_memory_view()  # Update memory view with current state
        self.debugger_window.show()

    def on_text_changed(self):
        """Handle text changes and trigger highlighting and line number updates."""
        self.is_text_changed = True
        self.update_timer.start()  # Start the timer to handle updates
        self.update_file_name_label()  # Update the file name label with the "*" for unsaved changes

    def on_update_timeout(self):
        """Called when the timer times out, used to handle line number and rehighlighting updates."""
        if self.is_text_changed:
            self.highlighter.rehighlight()  # Rehighlight the text
            self.line_number_widget.update()  # Update the line numbers
            self.is_text_changed = False
        self.update_timer.stop()  # Stop the timer to avoid repeated calls

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Base URL of the Flask API
    API_URL = "http://127.0.0.1:5000"
    
    window = MainWindow(API_URL)
    window.show()
    
    sys.exit(app.exec_())