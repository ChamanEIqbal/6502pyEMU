import sys
import requests
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QTabWidget, QTextEdit
)


class DebuggerWindow(QWidget):
    api_url = "http://127.0.0.1:5000"
    memory_text = ""

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
        self.init_cpu_table()

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

    def fetch_cpu_state(self, opcode):
        payload = {"opcode": opcode}
        response = requests.post(f"{self.api_url}/execute", json=payload)
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
    def fetch_cpu_state_WE(self):
        response = requests.get(f"{self.api_url}/state")
        if response.status_code == 200:
            return response.json().get("cpu_state", {})
        else:
            print(f"Error: {response.json().get('error', 'Unknown error')}")
            return {}

    def init_cpu_table(self):
        cpu_state = self.fetch_cpu_state_WE()
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
    def update_cpu_table(self, cpu_state):
        """
        Update the CPU state table with the given CPU state data.
        :param cpu_state: A dictionary containing the CPU state attributes.
        """
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

    def step_next(self):
        """Execute the next instruction and update the debugger state."""
        try:
            # Fetch and execute the next instruction
            response = requests.post(f"{DebuggerWindow.api_url}/step_next")
            if response.status_code == 200:
                data = response.json()
                
                # Update CPU state
                cpu_state = data.get("cpu_state", {})
                
                self.update_cpu_table(cpu_state)
                
                # Update memory view
                memory_state = data.get("memory_state", [])
                memory_text = "\n".join(
                    f"Address: {item['address']}, Value: {item['value']}"
                    for item in memory_state
                )
                self.memory_view.setText(memory_text)

                # Log success message
                print(data.get("message", "Executed successfully."))
            else:
                error_message = response.json().get("error", "Unknown error")
                print(f"Error during execution: {error_message}")
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

