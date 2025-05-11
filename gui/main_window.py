from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QTextEdit, QLabel, QHBoxLayout, QGroupBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from backend.fifo import FIFOReplacement
from backend.lru import LRUReplacement
from backend.clock import ClockReplacement
from backend.page_table import PageTable
from backend.frame_table import FrameTable
from backend.tlb import TLB
from gui.widgets import create_algorithm_dropdown, create_start_button, create_stats_display
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Virtual Memory Simulator")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QIcon('icons/simulator_icon.png'))  # Optional: Add an icon
        self.setStyleSheet("background-color: #f5f5f5;")  # Light background color

        self.page_table = PageTable(8)
        self.frame_table = FrameTable(4)
        self.tlb = TLB(4)

        self.initUI()

    def initUI(self):
        # Layout setup
        layout = QVBoxLayout()

        # Title Label
        title_label = QLabel("Virtual Memory Simulator", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E3A87;")
        layout.addWidget(title_label)

        # Frame Size Input
        self.frame_size_label = QLabel("Enter Frame Size: ", self)
        self.frame_size_input = QLineEdit(self)
        self.frame_size_input.setPlaceholderText("Enter frame size ")
        layout.addWidget(self.frame_size_label)
        layout.addWidget(self.frame_size_input)

        # Page Size Input
        self.page_size_label = QLabel("Enter Page Size: ", self)
        self.page_size_input = QLineEdit(self)
        self.page_size_input.setPlaceholderText("Enter page size ")
        layout.addWidget(self.page_size_label)
        layout.addWidget(self.page_size_input)

        # Logical Addresses Input
        self.logical_address_label = QLabel("Enter Logical Addresses (comma-separated): ", self)
        self.logical_address_input = QLineEdit(self)
        self.logical_address_input.setPlaceholderText()
        layout.addWidget(self.logical_address_label)
        layout.addWidget(self.logical_address_input)

        # Algorithm Selection Section
        algo_group = QGroupBox("Choose Replacement Algorithm", self)
        algo_layout = QHBoxLayout()

        self.alg_combo = create_algorithm_dropdown(self)
        algo_layout.addWidget(self.alg_combo)

        algo_group.setLayout(algo_layout)
        layout.addWidget(algo_group)

        # Start Button Section
        self.start_btn = create_start_button(self, self.start_simulation)
        layout.addWidget(self.start_btn)

        #Reset Button Section
        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.setStyleSheet("background-color: #ff4d4d; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.reset_btn.clicked.connect(self.reset_simulation)
        layout.addWidget(self.reset_btn)

        # Output Display (Step-by-step)
        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("font-size: 14px; background-color: #ffffff; border-radius: 5px; padding: 10px;")
        layout.addWidget(self.output_text)

        # Stats Display
        stats_group = QGroupBox("Simulation Statistics", self)
        stats_layout = QVBoxLayout()

        self.page_faults_label, self.tlb_hits_label, self.tlb_hits_ratio_label = create_stats_display(self)
        stats_layout.addWidget(self.page_faults_label)
        stats_layout.addWidget(self.tlb_hits_label)
        stats_layout.addWidget(self.tlb_hits_ratio_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Central widget setup
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_simulation(self):
        try:
            # Clear previous output and stats
            self.output_text.clear()

            # Get selected algorithm
            selected_algo = self.alg_combo.currentText()

            # Set replacement algorithm
            if selected_algo == "FIFO":
                replacement_algo = FIFOReplacement(4)
            elif selected_algo == "LRU":
                replacement_algo = LRUReplacement(4)
            elif selected_algo == "Clock":
                replacement_algo = ClockReplacement(4)

            # Simulation settings
            logical_addresses = [0, 1, 2, 3, 0, 4, 1, 5, 2, 6, 3, 7]

            tlb_hits = 0
            page_faults = 0

            # Start simulation step-by-step
            for logical_address in logical_addresses:
                self.output_text.append(f"\nTranslating logical address: {logical_address}")

                # Check TLB
                frame_number = self.tlb.lookup(logical_address)
                if frame_number is not None:
                    self.output_text.append(f"TLB Hit! Page {logical_address} → Frame {frame_number}")
                    tlb_hits += 1
                else:
                    self.output_text.append("TLB Miss.")
                    frame_number = self.page_table.get_frame(logical_address)

                    if frame_number is None:
                        self.output_text.append("Page Fault!")
                        page_faults += 1
                        # Perform eviction
                        frame_number = replacement_algo.evict(self.frame_table, self.page_table)
                        self.page_table.set_entry(logical_address, frame_number)
                        self.frame_table.add_page(logical_address, frame_number)
                        replacement_algo.insert(logical_address if not isinstance(replacement_algo, ClockReplacement) else frame_number)
                    else:
                        self.output_text.append(f"Page found in page table → Frame {frame_number}")

                    self.tlb.add_entry(logical_address, frame_number)
                    self.output_text.append(f"Updated TLB: {list(self.tlb.entries.items())}")

                self.output_text.append(f"Frame Table: {self.frame_table.frames}")

            # Update stats
            self.page_faults_label.setText(f"Page Faults: {page_faults}")
            self.tlb_hits_label.setText(f"TLB Hits: {tlb_hits}")
            if tlb_hits > 0:
                tlb_hits_ratio = tlb_hits / len(logical_addresses)
            else:
                tlb_hits_ratio = 0
            self.tlb_hits_ratio_label.setText(f"TLB Hits Ratio: {tlb_hits_ratio:.2f}")
            self.output_text.append("\n--- Simulation Complete ---")

        except Exception as e:
            self.output_text.append(f"Error: {str(e)}")
            print(f"Error: {str(e)}")
    def reset_simulation(self):
        # Reset all input fields
        self.frame_size_input.clear()
        self.page_size_input.clear()
        self.logical_address_input.clear()

        # Reset output text
        self.output_text.clear()

        # Reset stats labels
        self.page_faults_label.setText("Page Faults: 0")
        self.tlb_hits_label.setText("TLB Hits: 0")
        self.tlb_hits_ratio_label.setText("TLB Hits Ratio: 0.00")