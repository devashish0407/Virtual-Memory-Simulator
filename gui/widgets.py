from PyQt5.QtWidgets import QComboBox, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

def create_algorithm_dropdown(parent):
    combo = QComboBox(parent)
    combo.addItem("FIFO")
    combo.addItem("LRU")
    combo.addItem("Clock")
    combo.setStyleSheet("font-size: 16px; padding: 10px;")
    return combo

def create_start_button(parent, callback):
    print("Creating start button")
    button = QPushButton("Start Simulation", parent)
    button.setStyleSheet("""
        QPushButton {
            font-size: 18px;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    button.clicked.connect(callback)
    return button

def create_stats_display(parent):
    # Create QLabel widgets for displaying stats
    page_faults_label = QLabel("Page Faults: 0", parent)
    page_faults_label.setStyleSheet("font-size: 16px; color: #333333;")
    
    tlb_hits_label = QLabel("TLB Hits: 0", parent)
    tlb_hits_label.setStyleSheet("font-size: 16px; color: #333333;")
    
    tlb_hits_ratio_label = QLabel("TLB Hits Ratio: 0", parent)
    tlb_hits_ratio_label.setStyleSheet("font-size: 16px; color: #333333;")

    return page_faults_label, tlb_hits_label, tlb_hits_ratio_label
