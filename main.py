"""VyBora entry point."""
import os
# CRITICAL: --disable-software-rasterizer prevents the WebEngine crash on machines without GLES3
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"

import sys
import logging
import traceback

from PySide6.QtWidgets import QApplication

from config.settings import has_tmdb_token
from database.initialization import initialize_database

# Only import MainWindow ONCE, at the top
from ui.windows.main_window import MainWindow

# Setup logging to catch background errors
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def _excepthook(exc_type, exc_value, exc_tb):
    """Global exception handler — prints the full traceback so nothing silently dies."""
    print("\n========== UNHANDLED EXCEPTION ==========")
    traceback.print_exception(exc_type, exc_value, exc_tb)
    print("=========================================\n")


# Install the global hook BEFORE creating QApplication
sys.excepthook = _excepthook


def main() -> int:
    # 1. Initialize Database
    try:
        initialize_database()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        traceback.print_exc()
        return 1

    # 2. Check API Token
    if not has_tmdb_token():
        print("WARNING: TMDB_READ_TOKEN is missing. API calls will fail.")

    # 3. Start Application
    app = QApplication(sys.argv)
    app.setApplicationName("VyBora")

    try:
        win = MainWindow()
        win.show()
    except Exception:
        traceback.print_exc()
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())