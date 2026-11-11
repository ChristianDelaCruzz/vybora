"""Profile Page - Complete with Stats and Activity, fully themed."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QFrame, QHBoxLayout,
    QPushButton, QScrollArea, QGridLayout, QDialog, QFormLayout
)

from ui.app_state import theme_state
from ui.components.widgets import GradientButton
from ui.components.toast import Toast
from ui.components.icon_manager import get_icon
from database import user_repository


# ==========================================================
# EDIT PROFILE DIALOG
# ==========================================================
class EditProfileDialog(QDialog):
    def __init__(self, parent, username: str, email: str):
        super().__init__(parent)
        self.setWindowTitle("Edit Profile")
        self.setFixedSize(400, 260)
        
        # FIX: Apply the theme background to the QDialog itself
        self.setStyleSheet(f"QDialog {{ background-color: {theme_state.bg()}; }}")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        title = QLabel("Edit Profile Info")
        title.setStyleSheet(f"color: {theme_state.text()}; font-size: 18px; font-weight: 800; background: transparent;")
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.name_input = QLineEdit(username)
        self.email_input = QLineEdit(email)
        
        inp_style = f"""
            QLineEdit {{
                background-color: {theme_state.surface()};
                color: {theme_state.text()};
                border: 1px solid {theme_state.border()};
                border-radius: 8px;
                padding: 8px 12px;
            }}
            QLineEdit:focus {{ border: 1px solid {theme_state.accent_hex}; }}
        """
        self.name_input.setStyleSheet(inp_style)
        self.email_input.setStyleSheet(inp_style)
        
        name_lbl = QLabel("Username")
        name_lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-weight: 600; background: transparent;")
        email_lbl = QLabel("Email")
        email_lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-weight: 600; background: transparent;")
        
        form.addRow(name_lbl, self.name_input)
        form.addRow(email_lbl, self.email_input)
        
        layout.addLayout(form)
        layout.addStretch(1)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setStyleSheet(f"background-color: {theme_state.surface()}; color: {theme_state.text()}; border: 1px solid {theme_state.border()}; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedSize(140, 36)
        save_btn.setStyleSheet(f"background-color: {theme_state.accent_hex}; color: white; font-weight: 700; border-radius: 8px;")
        save_btn.clicked.connect(self.accept)
        
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)


# ==========================================================
# STAT CARD
# ==========================================================
class _StatCard(QFrame):
    def __init__(self, icon_name: str, value: str, label: str, color: str):
        super().__init__()
        self.setObjectName("StatCard")
        self._icon_name = icon_name
        self._color = color
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(16)

        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(self.icon_lbl)

        text_lay = QVBoxLayout()
        text_lay.setSpacing(2)
        
        self.val_lbl = QLabel(value)
        self.label_lbl = QLabel(label)
        
        text_lay.addWidget(self.val_lbl)
        text_lay.addWidget(self.label_lbl)
        lay.addLayout(text_lay)
        lay.addStretch(1)

        self.refresh_theme()

    def refresh_theme(self):
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: {theme_state.surface()};
                border-radius: 12px;
                border: 1px solid {theme_state.border()};
            }}
        """)
        
        self.val_lbl.setStyleSheet(f"color: {theme_state.text()}; font-size: 22px; font-weight: 800; background: transparent; border: none;")
        self.label_lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        self.icon_lbl.setPixmap(get_icon(self._icon_name, self._color, 28).pixmap(28, 28))
        
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


# ==========================================================
# PROFILE PAGE
# ==========================================================
class ProfilePage(QWidget):
    username_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self._current_username = ""
        self._current_user_id = 1
        self._stat_cards: list[_StatCard] = []
        self._section_labels: list[QLabel] = []
        self._panels: list[QFrame] = []
        self._row_labels: list[QLabel] = []
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        self.header_lbl = QLabel("My Profile")
        root.addWidget(self.header_lbl)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        self.scroll.viewport().setStyleSheet("background: transparent;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(24)

        # 1. PROFILE HEADER
        self.header_panel = QFrame()
        self.header_panel.setObjectName("PanelCard")
        h_lay = QHBoxLayout(self.header_panel)
        h_lay.setContentsMargins(30, 30, 30, 30)
        h_lay.setSpacing(24)
        self._panels.append(self.header_panel)

        self.avatar = QLabel()
        self.avatar.setFixedSize(80, 80)
        self.avatar.setAlignment(Qt.AlignCenter)
        h_lay.addWidget(self.avatar)

        info_lay = QVBoxLayout()
        info_lay.setSpacing(4)
        
        self.name_lbl = QLabel("Loading...")
        self.role_lbl = QLabel("")
        self.email_lbl = QLabel("")

        info_lay.addWidget(self.name_lbl)
        info_lay.addWidget(self.role_lbl)
        info_lay.addWidget(self.email_lbl)
        h_lay.addLayout(info_lay, 1)

        self.edit_btn = GradientButton("Edit Profile", "navigation/user-round")
        self.edit_btn.setFixedWidth(140)
        self.edit_btn.clicked.connect(self._open_edit_dialog) 
        h_lay.addWidget(self.edit_btn, alignment=Qt.AlignTop)
        lay.addWidget(self.header_panel)

        # 2. STATISTICS
        lay.addWidget(self._section_title("ENTERTAINMENT STATISTICS"))
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(16)
        lay.addLayout(self.stats_grid)

        # 3. RECENT ACTIVITY
        lay.addWidget(self._section_title("RECENT ACTIVITY"))
        self.activity_panel = QFrame()
        self.activity_panel.setObjectName("PanelCard")
        self._panels.append(self.activity_panel)
        self.a_lay = QVBoxLayout(self.activity_panel)
        self.a_lay.setContentsMargins(20, 20, 20, 20)
        self.a_lay.setSpacing(12)
        lay.addWidget(self.activity_panel)

        # 4. SECURITY
        lay.addWidget(self._section_title("SECURITY & PASSWORD"))
        self.pw_panel = QFrame()
        self.pw_panel.setObjectName("PanelCard")
        self._panels.append(self.pw_panel)
        pw_lay = QVBoxLayout(self.pw_panel)
        pw_lay.setContentsMargins(30, 30, 30, 30)
        pw_lay.setSpacing(16)

        pw_grid = QGridLayout()
        pw_grid.setSpacing(16)
        pw_grid.setColumnStretch(0, 0)
        pw_grid.setColumnStretch(1, 1)

        self.current_pw = self._create_pw_input("Current Password")
        self.new_pw = self._create_pw_input("New Password")
        self.confirm_pw = self._create_pw_input("Confirm New Password")
        
        self.cpw_lbl = QLabel("Current Password")
        self.npw_lbl = QLabel("New Password")
        self.conf_lbl = QLabel("Confirm Password")
        self._row_labels.extend([self.cpw_lbl, self.npw_lbl, self.conf_lbl])
        
        pw_grid.addWidget(self.cpw_lbl, 0, 0)
        pw_grid.addWidget(self.current_pw, 0, 1)
        pw_grid.addWidget(self.npw_lbl, 1, 0)
        pw_grid.addWidget(self.new_pw, 1, 1)
        pw_grid.addWidget(self.conf_lbl, 2, 0)
        pw_grid.addWidget(self.confirm_pw, 2, 1)
        
        pw_lay.addLayout(pw_grid)
        
        pw_btn_row = QHBoxLayout()
        pw_btn_row.addStretch(1)
        self.pw_btn = GradientButton("Update Password", "system/lock")
        self.pw_btn.setFixedWidth(180)
        self.pw_btn.clicked.connect(self._change_password)
        pw_btn_row.addWidget(self.pw_btn)
        pw_lay.addLayout(pw_btn_row)

        lay.addWidget(self.pw_panel)
        lay.addStretch(1)

        self.scroll.setWidget(content)
        root.addWidget(self.scroll)
        
        self.refresh_theme()

    def refresh_theme(self) -> None:
        self.header_lbl.setStyleSheet(f"color: {theme_state.text()}; font-size: 24px; font-weight: 700; background: transparent; border: none;")
        self.setStyleSheet("QWidget { background-color: transparent; }")

        for lbl in self._section_labels:
            lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 12px; font-weight: 900; letter-spacing: 1px; background: transparent; border: none; margin-top: 10px;")
            
        for panel in self._panels:
            panel.setStyleSheet(f"""
                QFrame#PanelCard {{
                    background-color: {theme_state.surface()};
                    border-radius: 12px;
                    border: 1px solid {theme_state.border()};
                }}
            """)

        self.name_lbl.setStyleSheet(f"color: {theme_state.text()}; font-size: 24px; font-weight: 800; background: transparent; border: none;")
        self.role_lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
        self.email_lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 13px; background: transparent; border: none;")
        self.avatar.setStyleSheet(f"background-color: {theme_state.accent_hex}; border-radius: 40px; color: white; font-size: 32px; font-weight: 800;")

        for lbl in self._row_labels:
            lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-weight: 600; background: transparent; border: none;")

        for card in self._stat_cards:
            card.refresh_theme()

        input_style = (
            f"QLineEdit {{ background-color: {theme_state.bg()}; color: {theme_state.text()};"
            f" border-radius: 8px; padding: 0 12px; padding-right: 40px; border: 1px solid {theme_state.border()};"
            f" selection-background-color: {theme_state.accent_hex}; selection-color: white; }}"
            f"QLineEdit:focus {{ border: 1px solid {theme_state.accent_hex}; }}"
        )
        for container in (self.current_pw, self.new_pw, self.confirm_pw):
            container.textbox.setStyleSheet(input_style)
            container.eye_btn.setIcon(get_icon("system/eye", theme_state.text_dim(), 18))

        self._load_activity()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 12px; font-weight: 900; letter-spacing: 1px; background: transparent; border: none; margin-top: 10px;")
        self._section_labels.append(lbl)
        return lbl

    def _create_pw_input(self, placeholder: str) -> QWidget:
        container = QWidget()
        container.setFixedHeight(40)
        container.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setEchoMode(QLineEdit.Password)
        inp.setFixedHeight(40)
        layout.addWidget(inp)

        btn = QPushButton(container)
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("background: transparent; border: none;")
        btn.setParent(container)
        
        def toggle():
            if inp.echoMode() == QLineEdit.Password:
                inp.setEchoMode(QLineEdit.Normal)
                btn.setIcon(get_icon("system/eye-off", theme_state.text_dim(), 18))
            else:
                inp.setEchoMode(QLineEdit.Password)
                btn.setIcon(get_icon("system/eye", theme_state.text_dim(), 18))

        btn.clicked.connect(toggle)

        def resize_event(event):
            btn.move(container.width() - 35, 5)
        
        container.resizeEvent = resize_event
        container.textbox = inp
        container.eye_btn = btn
        
        return container

    def load_user_data(self, username: str):
        self._current_username = username
        data = user_repository.get_user_profile(username)
        
        if data:
            self._current_user_id = data.get("user_id", 1)
            self.name_lbl.setText(data.get("username", username))
            self.role_lbl.setText(data.get("role", "User"))
            self.email_lbl.setText(data.get("email", ""))
            
            initials = "".join([part[0].upper() for part in username.split()[:2]])
            self.avatar.setText(initials)
            
            self._load_stats()
            self._load_activity()
        else:
            self.name_lbl.setText(username)
            self.role_lbl.setText("User")
            self.email_lbl.setText(f"{username.lower()}@vybora.com")
            self.avatar.setText(username[0].upper())

    def _open_edit_dialog(self):
        dialog = EditProfileDialog(self, self._current_username, self.email_lbl.text())
        
        if dialog.exec():
            new_name = dialog.name_input.text().strip()
            new_email = dialog.email_input.text().strip()
            
            if not new_name or not new_email:
                Toast(self.window(), "Error", "Fields cannot be empty.", "error").show_toast()
                return
                
            success = user_repository.update_user_profile(self._current_user_id, new_name, new_email)
            
            if success:
                Toast(self.window(), "Profile Updated", "Your information has been saved.", "success").show_toast()
                self.load_user_data(new_name)
                self.username_changed.emit(new_name)
            else:
                Toast(self.window(), "Error", "Could not update profile. Username or email may be taken.", "error").show_toast()

    def _load_stats(self):
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._stat_cards.clear()

        stats = user_repository.get_user_stats(self._current_user_id)
        
        cards = [
            _StatCard("navigation/clapperboard", str(stats.get("movies", 0)), "Movies Watched", theme_state.accent_hex),
            _StatCard("navigation/film",          str(stats.get("tv", 0)),     "TV Episodes",   "#3985FF"),
            _StatCard("navigation/gamepad-2",     str(stats.get("games", 0)),  "Games Played",  "#D946EF"),
            _StatCard("navigation/music-2",       str(stats.get("music", 0)),  "Tracks Played", "#34D399"),
        ]
        
        self._stat_cards.extend(cards)
        for i, card in enumerate(cards):
            self.stats_grid.addWidget(card, i // 2, i % 2)

    def _load_activity(self):
        while self.a_lay.count():
            item = self.a_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        activity = user_repository.get_recent_activity(self._current_user_id)
        
        if not activity:
            lbl = QLabel("No recent activity.")
            lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 13px; background: transparent;")
            self.a_lay.addWidget(lbl)
            return

        for item in activity:
            row = QHBoxLayout()
            icon = get_icon("navigation/clapperboard", theme_state.text_dim(), 18)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(icon.pixmap(18, 18))
            icon_lbl.setStyleSheet("background: transparent; border: none;")
            
            title = QLabel(item.get("title", "Unknown"))
            title.setStyleSheet(f"color: {theme_state.text()}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
            
            time_lbl = QLabel(item.get("watched_at", "")[:10])
            time_lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 12px; background: transparent; border: none;")
            
            row.addWidget(icon_lbl)
            row.addWidget(title)
            row.addStretch(1)
            row.addWidget(time_lbl)
            self.a_lay.addLayout(row)

    def _change_password(self):
        current = self.current_pw.textbox.text()
        new = self.new_pw.textbox.text()
        confirm = self.confirm_pw.textbox.text()
        
        if not current or not new or not confirm:
            Toast(self.window(), "Missing Info", "Please fill in all password fields.", "warning").show_toast()
            return

        if new != confirm:
            Toast(self.window(), "Mismatch", "New passwords do not match.", "error").show_toast()
            return
            
        if len(new) < 8:
            Toast(self.window(), "Weak Password", "New password must be at least 8 characters.", "warning").show_toast()
            return

        success = user_repository.change_user_password(self._current_username, current, new)
        
        if success:
            Toast(self.window(), "Password Updated", "Your password has been changed.", "success").show_toast()
            self.current_pw.textbox.clear()
            self.new_pw.textbox.clear()
            self.confirm_pw.textbox.clear()
        else:
            Toast(self.window(), "Error", "Incorrect current password.", "error").show_toast()