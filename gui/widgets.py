# gui/widgets.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt

class VirtualMemoryWidgets(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Window Title
        self.setWindowTitle("Virtual Memory Simulator")
        
        self.setStyleSheet(
         
        """
        QLineEdit, QComboBox {
            border: 2px solid #ccc;
            border-radius: 10px;
            padding: 6px;
            font-size: 14px;
            background-color: #f9f9f9;
        }
        
        QPushButton {
            border-radius: 12px;
            padding: 8px 16px;
            font-size: 15px;
            font-weight: bold;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 black, stop:1 white);
            color: white;
        }

        QPushButton#SimulateBtn {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980B9, stop:1 #6DD5FA);
            color: white;
        }

        QPushButton#ResetBtn {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f12711, stop:1 #f5af19);
            color: white;
        }

        QPushButton:hover {
            opacity: 0.8;
        }
    """)
        
        # Title Heading
        self.title_label = QLabel("<h1>Virtual Memory Simulator</h1>")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Input fields for Local Address, Page Size, and Frame Size
        self.local_address_label = QLabel("Enter Local Address:")
        self.local_address_input = QLineEdit()
        self.local_address_input.setPlaceholderText("Enter address in decimal format")

        self.page_size_label = QLabel("Enter Page Size:")
        self.page_size_input = QLineEdit()
        self.page_size_input.setPlaceholderText("Enter page size in bytes")

        self.frame_size_label = QLabel("Enter Frame Size:")
        self.frame_size_input = QLineEdit()
        self.frame_size_input.setPlaceholderText("Enter frame size in bytes")

        # Algorithm Selection
        self.algorithm_label = QLabel("Select Page Replacement Algorithm:")
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["FIFO", "LRU"])

        # Simulate and Reset Buttons
        self.simulate_button = QPushButton("Simulate")
        self.simulate_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;")
        self.simulate_button.setStyleSheet("QPushButton:hover { background-color: #45a049; }")
        self.simulate_button.clicked.connect(self.simulate_access)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet("background-color: #f44336; color: white; font-size: 16px; padding: 10px;")
        self.reset_button.setStyleSheet("QPushButton:hover { background-color: #e53935; }")
        self.reset_button.clicked.connect(self.reset_inputs)

        # TLB and Page Table
        self.tlb_table = QTableWidget(5, 2)
        self.page_table = QTableWidget(5, 2)

        # Set up tables with headers
        self.setup_table(self.page_table, ["Page #", "Frame #"])
        self.setup_table(self.tlb_table, ["TLB Entry", "Frame #"])

        # Hit/Miss/Failure Stats
        self.stats_label = QLabel("<h3>TLB Hits: 0  |  TLB Misses: 0  |  Page Faults: 0</h3>")
        self.stats_label.setAlignment(Qt.AlignCenter)

        # Layout Setup
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.local_address_label)
        self.layout.addWidget(self.local_address_input)
        self.layout.addWidget(self.page_size_label)
        self.layout.addWidget(self.page_size_input)
        self.layout.addWidget(self.frame_size_label)
        self.layout.addWidget(self.frame_size_input)
        self.layout.addWidget(self.algorithm_label)
        self.layout.addWidget(self.algorithm_combo)
        self.layout.addWidget(self.simulate_button)
        self.layout.addWidget(self.reset_button)
        self.layout.addWidget(self.stats_label)
        self.layout.addWidget(self.page_table)
        self.layout.addWidget(self.tlb_table)

        self.setLayout(self.layout)

    def setup_table(self, table, headers):
        """Setup table with headers and set all cells as empty initially."""
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.setItem(row, col, QTableWidgetItem(""))

    def reset_inputs(self):
        """Reset all inputs and stats"""
        self.local_address_input.clear()
        self.page_size_input.clear()
        self.frame_size_input.clear()
        self.algorithm_combo.setCurrentIndex(0)
        self.stats_label.setText("<h3>TLB Hits: 0  |  TLB Misses: 0  |  Page Faults: 0</h3>")
        self.reset_table(self.tlb_table)
        self.reset_table(self.page_table)

    def reset_table(self, table):
        """Reset table content"""
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.setItem(row, col, QTableWidgetItem(""))

    def simulate_access(self):
        """Handle simulation of page access."""
        local_address = self.local_address_input.text()
        page_size = self.page_size_input.text()
        frame_size = self.frame_size_input.text()
        algorithm = self.algorithm_combo.currentText()

        # Validate input
        if not local_address.isdigit() or not page_size.isdigit() or not frame_size.isdigit():
            return  # Validate inputs (all must be integers)

        local_address = int(local_address)
        page_size = int(page_size)
        frame_size = int(frame_size)

        # Perform simulation based on algorithm
        if algorithm == "FIFO":
            self.simulate_fifo(local_address, page_size, frame_size)
        elif algorithm == "LRU":
            self.simulate_lru(local_address, page_size, frame_size)

    def simulate_fifo(self, local_address, page_size, frame_size):
        """Simulate FIFO algorithm."""
        print(f"Simulating FIFO with Local Address: {local_address}, Page Size: {page_size}, Frame Size: {frame_size}")
        # Logic for FIFO
        self.update_tlb_table("FIFO")

    def simulate_lru(self, local_address, page_size, frame_size):
        """Simulate LRU algorithm."""
        print(f"Simulating LRU with Local Address: {local_address}, Page Size: {page_size}, Frame Size: {frame_size}")
        # Logic for LRU
        self.update_tlb_table("LRU")

    def update_tlb_table(self, algorithm):
        """Update the TLB table (for demonstration purposes)."""
        for row in range(self.tlb_table.rowCount()):
            self.tlb_table.setItem(row, 0, QTableWidgetItem(f"Entry {row} - {algorithm}"))
            self.tlb_table.setItem(row, 1, QTableWidgetItem(f"Frame {row}"))

        # Update the stats label (simulated example)
        self.stats_label.setText("<h3>TLB Hits: 3  |  TLB Misses: 2  |  Page Faults: 1</h3>")

