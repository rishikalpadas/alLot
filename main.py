"""Main entry point for alLot application."""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def set_app_style(app):
    """Set application style and palette."""
    app.setStyle("Fusion")
    
    # Create custom palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(33, 150, 243))
    palette.setColor(QPalette.Highlight, QColor(33, 150, 243))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    
    app.setPalette(palette)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("alLot")
    app.setOrganizationName("alLot")
    
    # Set style
    set_app_style(app)
    
    # Show login window
    login_window = LoginWindow()
    
    def on_login_success(user):
        """Handle successful login."""
        main_window = MainWindow(user)
        main_window.show()
    
    login_window.login_successful.connect(on_login_success)
    login_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
