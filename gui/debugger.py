import sys
import requests
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QTabWidget, QTextEdit
)


class DebuggerWindow(QWidget):
    def __init__(self, api_url):
        super().__init__()
        self.api_url = api_url
        self.setWindowTitle("Debugger")
        self.setGeometry(100, 100, 250, 600)

        # Tab widget
        self.tabs = QTabWidget(self)

        # CPU state tab
        self.cpu_tab = QWidget()
        self.cpu_table = QTableWidget(self.cpu_tab)
        self.cpu_table.setRowCount(7)  # Number of CPU attributes
        self.cpu_table.setColumnCount(2)  # Attribute name and value
        self.cpu_table.setHorizontalHeaderLabels(["Attribute", "Value"])
        self.update_cpu_table()

        cpu_layout = QVBoxLayout()
        cpu_layout.addWidget(self.cpu_table)
        self.cpu_tab.setLayout(cpu_layout)

        # Memory view tab
        self.memory_tab = QWidget()
        self.memory_view = QTextEdit(self.memory_tab)
        self.memory_view.setReadOnly(True)
        self.update_memory_view()

        memory_layout = QVBoxLayout()
        memory_layout.addWidget(self.memory_view)
        self.memory_tab.setLayout(memory_layout)

        # Add tabs to the tab widget
        self.tabs.addTab(self.cpu_tab, "CPU State")
        self.tabs.addTab(self.memory_tab, "Memory View")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def fetch_cpu_state(self):
        response = requests.get(f"{self.api_url}/state")
        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def fetch_memory_dump(self):
        response = requests.get(f"{self.api_url}/memory")
        if response.status_code == 200:
            return response.json().get("memory", {})
        else:
            return {}

    def update_cpu_table(self):
        cpu_state = self.fetch_cpu_state()
        attributes = [
            ("PC", hex(cpu_state.get("PC", 0))),
            ("SP", hex(cpu_state.get("SP", 0))),
            ("A", hex(cpu_state.get("A", 0))),
            ("X", hex(cpu_state.get("X", 0))),
            ("Y", hex(cpu_state.get("Y", 0))),
            ("PS", bin(cpu_state.get("PS", 0))),
            ("Cycles", cpu_state.get("cycles", 0)),
        ]

        for i, (name, value) in enumerate(attributes):
            self.cpu_table.setItem(i, 0, QTableWidgetItem(name))
            self.cpu_table.setItem(i, 1, QTableWidgetItem(str(value)))

    def update_memory_view(self):
        memory_dump = self.fetch_memory_dump()
        memory_text = "\n".join(f"{addr}: {value}" for addr, value in memory_dump.items())
        self.memory_view.setText(memory_text)
