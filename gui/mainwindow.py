import os
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontDatabase, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QHBoxLayout, QWidget, QMenuBar, QAction, QFileDialog, QStatusBar, QLabel, QShortcut, QMessageBox

from syntaxhighlighter import SyntaxHighlighter
from widgets import Widgets
from linenumberwidget import LineNumberWidget
from debugger import DebuggerWindow
class MainWindow(QMainWindow):
    def __init__(self, api_url):
        super().__init__()

        print("Initializing MainWindow")

        self.setWindowTitle("6502 Emulator v0.0.2")
        self.setGeometry(100, 100, 800, 600)

        # Mode flag: 'edit' or 'debug'
        self.mode = 'edit'

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

        # Add shortcuts
        self.add_shortcuts()

        # Debugger-related attributes
        self.debugger_active = False
        self.current_line = 0
        self.instructions = []
        self.labels = {}


    def read_labels(self):
            self.labels.clear()  # Clear the labels dictionary before populating it
            text = self.textEdit.toPlainText()  # Get the text from the textEdit
            lines = text.splitlines()  # Split the text into lines

            for i, line in enumerate(lines):
                line = line.strip()
                if line.endswith(":"):  # Check if the line is a label
                    label = line[:-1]  # Remove the trailing colon
                    self.labels[label] = i  # Store the line number (0-based index)
            
            print(f"Labels updated: {self.labels}")

    def setup_menu(self):
        """Set up the menu bar with File actions (New, Open, Save)."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        debugger_menu = menu_bar.addMenu("Debugger")

        # Debugger action
        toggle_debug_mode_action = QAction("Toggle Debug Mode", self)
        toggle_debug_mode_action.triggered.connect(self.toggle_debug_mode)
        toggle_debug_mode_action.setShortcut("Ctrl+D")
        debugger_menu.addAction(toggle_debug_mode_action)

        step_action = QAction("STEP", self)
        step_action.triggered.connect(self.step_instruction)
        debugger_menu.addAction(step_action)

        # Create the File menu
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def add_shortcuts(self):
        """Add keyboard shortcuts for actions."""
        self.split_lines_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.split_lines_shortcut.activated.connect(self.split_text_lines)

        self.assemble_ready_shortcut = QShortcut(QKeySequence("CTRL+Shift+P"), self)
        self.assemble_ready_shortcut.activated.connect(self.assemble_ready)

        self.step_next_shortcut = QShortcut(Qt.Key_F8, self)
        self.step_next_shortcut.activated.connect(self.step_instruction)

    def toggle_debug_mode(self):
        """Toggle between edit mode and debug mode."""
        self.mode = 'debug' if self.mode == 'edit' else 'edit'
        self.debugger_active = self.mode == 'debug'
        
        if self.debugger_active:
            self.debugger_window = DebuggerWindow(self.api_url)
            self.debugger_window.init_cpu_table()
            self.debugger_window.update_memory_table()
            self.debugger_window.show()

            print("Debugger Mode Activated")
            self.initialize_debugger()
        else:
            print("Edit Mode Activated")
            self.textEdit.setReadOnly(False)

    def initialize_debugger(self):
        """Prepare the debugger state."""

        self.textEdit.setReadOnly(True)
        self.instructions = self.textEdit.toPlainText().splitlines()
        self.current_line = 0
        self.highlight_line(self.current_line)

    def highlight_line(self, line_number):
        """Highlight a specific line in the text editor."""
        cursor = self.textEdit.textCursor()
        cursor.movePosition(cursor.Start)
        for _ in range(line_number):
            cursor.movePosition(cursor.Down)
        cursor.select(cursor.LineUnderCursor)
        self.textEdit.setTextCursor(cursor)

    def step_instruction(self):
        """Execute the current line and move to the next line."""
        if not self.debugger_active:
            QMessageBox.warning(self, "Debugger Not Active", "Please enable Debug Mode first.")
            return

        if self.current_line >= len(self.instructions):
            QMessageBox.information(self, "End of Program", "No more instructions to execute.")
            return

        instruction = self.instructions[self.current_line].strip()
        if instruction.endswith(":"):  # If it's a label, skip it
            print(f"Label encountered: {instruction}")
            self.current_line += 1
            self.highlight_line(self.current_line)
            return

        # Check if it's a JMP or JSR instruction
        parts = instruction.split()
        opcode = parts[0]
        if opcode in ('JMP', 'JSR') and len(parts) > 1:
            label = parts[1]
            if label in self.labels:
                self.current_line = self.labels[label]  # Jump to the label line
                print(f"Jumping to label: {label} at line {self.current_line}")
                self.highlight_line(self.current_line)
                return
            else:
                QMessageBox.warning(self, "Invalid Label", f"Label '{label}' not found.")
        else:
            print(f"Executing instruction: {instruction}")
            self.execute_opcode()  # Mock execution function

        self.current_line += 1
        self.highlight_line(self.current_line)

    def execute_opcode(self):
        """Mock execution of an opcode."""
        
        self.debugger_window.step_next()


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
        Widgets.split_lines(text)
    
    def assemble_ready(self): 
        self.read_labels()
        text = self.textEdit.toPlainText()
        if(Widgets.assemble(text)):
            QMessageBox.information(self, "Success", "Successfully Assembled!")
        else:
            QMessageBox.information(self, "Failure", "Failure, Cannot Assemble.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    API_URL = "http://127.0.0.1:5000"
    window = MainWindow(API_URL)
    window.show()
    sys.exit(app.exec_())