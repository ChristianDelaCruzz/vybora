"""First-run secure Admin provisioning page."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
)
from config.settings import COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_PURPLE, COLOR_BLUE, COLOR_SURFACE
from database.user_repository import create_user
from ui.components.toast import Toast

class SetupAdminPage(QWidget):
    admin_created = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        container = QWidget()
        container.setFixedWidth(450)
        form = QVBoxLayout(container)
        form.setSpacing(16)

        title = QLabel("Secure Setup")
        title.setStyleSheet(f"color:{COLOR_TEXT}; font-size:32px; font-weight:800;")
        form.addWidget(title)

        sub = QLabel("Create the first Admin account for VyBora.\nThis can only be done once.")
        sub.setStyleSheet(f"color:{COLOR_TEXT_DIM}; font-size:14px;")
        form.addWidget(sub)
        form.addSpacing(20)

        self.username_in = self._create_input("Admin Username")
        form.addWidget(self.username_in)
        
        self.email_in = self._create_input("Admin Email")
        form.addWidget(self.email_in)
        
        self.password_in = self._create_input("Admin Password", True)
        form.addWidget(self.password_in)

        self.confirm_in = self._create_input("Confirm Password", True)
        form.addWidget(self.confirm_in)

        btn = QPushButton("Create Admin Account")
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLOR_PURPLE}, stop:1 {COLOR_BLUE});"
            f"color:white; border:none; border-radius:8px; font-weight:700; font-size:16px; }}"
        )
        btn.clicked.connect(self._handle_create)
        form.addWidget(btn)

        layout.addWidget(container)

    def _handle_create(self) -> None:
        user = self.username_in.text().strip()
        email = self.email_in.text().strip()
        pwd = self.password_in.text()
        confirm = self.confirm_in.text()

        if not user or not email or not pwd:
            Toast(self.window(), "Missing Info", "All fields are required.", "warning").show_toast()
            return
        if pwd != confirm:
            Toast(self.window(), "Mismatch", "Passwords do not match.", "error").show_toast()
            return
        if len(pwd) < 8:
            Toast(self.window(), "Weak Password", "Must be at least 8 characters.", "warning").show_toast()
            return

        try:
            # Force role = 'Admin'
            create_user(user, email, pwd, role="Admin")
            Toast(self.window(), "Admin Created", "You can now log in.", "success").show_toast()
            self.admin_created.emit()
        except Exception as e:
            Toast(self.window(), "Error", str(e), "error").show_toast()

    def _create_input(self, placeholder: str, is_pwd: bool = False) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(50)
        if is_pwd:
            inp.setEchoMode(QLineEdit.Password)
        inp.setStyleSheet(
            f"QLineEdit {{ background-color: {COLOR_SURFACE}; color: {COLOR_TEXT};"
            f"border: 1px solid rgba(255, 255, 255, 20); border-radius: 8px; padding: 0 16px; }}"
            f"QLineEdit:focus {{ border: 1px solid {COLOR_BLUE}; }}"
        )
        return inp