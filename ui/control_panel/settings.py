"""Settings panel."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QMessageBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt
from services.auth_service import AuthService


class SettingsPanel(QWidget):
    """Panel for application settings."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Password change group
        password_group = QGroupBox("Change Password")
        password_layout = QFormLayout()
        
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Current Password:", self.current_password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        password_layout.addRow("New Password:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Confirm Password:", self.confirm_password)
        
        button_layout = QHBoxLayout()
        change_btn = QPushButton("Change Password")
        change_btn.clicked.connect(self.change_password)
        button_layout.addWidget(change_btn)
        button_layout.addStretch()
        
        password_layout.addRow("", button_layout)
        password_group.setLayout(password_layout)
        
        layout.addWidget(password_group)
        layout.addStretch()
    
    def change_password(self):
        """Change admin password."""
        current = self.current_password.text()
        new = self.new_password.text()
        confirm = self.confirm_password.text()
        
        if not current or not new or not confirm:
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return
        
        if new != confirm:
            QMessageBox.warning(self, "Validation Error", "New passwords do not match.")
            return
        
        if len(new) < 4:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 4 characters.")
            return
        
        success, message = AuthService.change_password("admin", current, new)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.current_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
        else:
            QMessageBox.critical(self, "Error", message)
