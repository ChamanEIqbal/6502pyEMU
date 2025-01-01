import sys
import requests
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QTabWidget
)


class DebuggerWindow(QWidget):
    api_url = "http://127.0.0.1:5000"

    def __init__(self, api_url):
        super().__init__()
        self.api_url = api_url
        self.setWindowTitle("Debugger")
        self.setGeometry(100, 100, 500, 600)  # Adjusted width for table view

        # Tab widget
        self.tabs = QTabWidget(self)

        # CPU state tab
        self.cpu_tab = QWidget()
        self.cpu_table = QTableWidget(self.cpu_tab)
        self.cpu_table.setRowCount(7)  # Number of CPU attributes
        self.cpu_table.setColumnCount(2)  # Attribute name and value
        self.cpu_table.setHorizontalHeaderLabels(["Attribute", "Value"])
        self.init_cpu_table()

        cpu_layout = QVBoxLayout()
        cpu_layout.addWidget(self.cpu_table)
        self.cpu_tab.setLayout(cpu_layout)

        # Memory view tab
        self.memory_tab = QWidget()
        self.memory_table = QTableWidget(self.memory_tab)
        self.memory_table.setColumnCount(2)  # Address and Value columns
        self.memory_table.setHorizontalHeaderLabels(["Address", "Value"])
        self.init_memory_table()

        memory_layout = QVBoxLayout()
        memory_layout.addWidget(self.memory_table)
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
            return response.json().get("cpu_state", {})
        else:
            print(f"Error: {response.json().get('error', 'Unknown error')}")
            return {}

    def fetch_memory_dump(self):
        response = requests.get(f"{self.api_url}/memory")
        if response.status_code == 200:
            return response.json().get("memory", {})
        else:
            return {}

    def init_cpu_table(self):
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

    def init_memory_table(self):
        memory_dump = self.fetch_memory_dump()
        self.memory_table.setRowCount(len(memory_dump))
        for row, (addr, value) in enumerate(memory_dump.items()):
            self.memory_table.setItem(row, 0, QTableWidgetItem(addr))
            self.memory_table.setItem(row, 1, QTableWidgetItem(value))

    def update_memory_table(self):
        memory_dump = self.fetch_memory_dump()
        self.memory_table.setRowCount(len(memory_dump))  # Adjust row count
        for row, (addr, value) in enumerate(memory_dump.items()):
            self.memory_table.setItem(row, 0, QTableWidgetItem(addr))
            self.memory_table.setItem(row, 1, QTableWidgetItem(value))

    def step_next(self):
        """Execute the next instruction and update the debugger state."""
        try:
            response = requests.post(f"{self.api_url}/step_next")
            if response.status_code == 200:
                data = response.json()

                # Update CPU state
                cpu_state = data.get("cpu_state", {})
                self.update_cpu_table(cpu_state)

                # Update memory view
                self.update_memory_table()

                print(data.get("message", "Executed successfully."))
            else:
                error_message = response.json().get("error", "Unknown error")
                print(f"Error during execution: {error_message}")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

    def update_cpu_table(self, cpu_state):
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
