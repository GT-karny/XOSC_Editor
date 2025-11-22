"""エントリポイント"""

import sys
from PySide6.QtWidgets import QApplication
from osc_editor.ui.main_window import MainWindow


def main():
    """アプリケーションのエントリポイント"""
    app = QApplication(sys.argv)
    app.setApplicationName("XOSC Editor")
    app.setOrganizationName("XOSC Editor")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


