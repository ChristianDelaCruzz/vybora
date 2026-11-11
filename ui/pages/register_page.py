"""Premium split-screen Register Page."""
from PySide6.QtCore import Qt, Signal, QVariantAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QPixmap, QColor

from config.settings import (
    COLOR_BG, COLOR_SURFACE, COLOR_TEXT, COLOR_TEXT_DIM, 
    COLOR_PURPLE, COLOR_BLUE, COLOR_PINK, PROJECT_ROOT
)
from ui.components.icon_manager import get_icon
from ui.components.toast import Toast
from ui.components.animation_manager import fade_in
from ui.components.widgets import GradientButton
from database.user_repository import create_user, UserExistsError


class RegisterPage(QWidget):
    register_successful = Signal(str, str) 
    go_to_login = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ==========================================
        # LEFT SIDE
        # ==========================================
        left_frame = QFrame()
        left_frame.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 #100E1B, stop:1 {COLOR_PINK});"
        )
        left_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(60, 40, 60, 60)
        left_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(12)
        logo_icon = QLabel()
        pixmap = QPixmap(str(PROJECT_ROOT / "assets" / "icons" / "navigation" / "logo.svg"))
        logo_icon.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_icon.setStyleSheet("background: transparent; border: none;")
        
        logo_text = QLabel("VyBora")
        logo_text.setStyleSheet("color:white; font-size:28px; font-weight:900; letter-spacing:1px; background:transparent; border:none;")
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        left_layout.addLayout(logo_layout)

        left_layout.addStretch(1)
        
        features_layout = QVBoxLayout()
        features_layout.setSpacing(16)
        features_layout.setAlignment(Qt.AlignLeft)
        
        features_layout.addWidget(self._create_feature_card("navigation/gamepad-2", "Explore Games", "Discover your next adventure.", COLOR_PURPLE))
        features_layout.addWidget(self._create_feature_card("navigation/clapperboard", "Watch Movies", "Stream cinematic trailers.", COLOR_BLUE))
        features_layout.addWidget(self._create_feature_card("navigation/music-2", "Listen to Music", "Immerse in premium audio.", COLOR_PINK))

        left_layout.addLayout(features_layout)
        left_layout.addStretch(1)
        
        headline = QLabel("Join the VyBora Universe.")
        headline.setStyleSheet("color:white; font-size:36px; font-weight:700; background:transparent; border:none;")
        headline.setWordWrap(True)
        headline.setMaximumWidth(400)
        left_layout.addWidget(headline)

        subtext = QLabel("Create an account to explore games, videos, and music.")
        subtext.setStyleSheet("color:rgba(255, 255, 255, 180); font-size:16px; background:transparent; border:none; margin-top:10px;")
        subtext.setWordWrap(True)
        subtext.setMaximumWidth(400)
        left_layout.addWidget(subtext)

        layout.addWidget(left_frame, 1)

        # ==========================================
        # DIVIDER
        # ==========================================
        divider = QFrame()
        divider.setFixedWidth(2)
        divider.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            f"stop:0 transparent, stop:0.5 {COLOR_PINK}, stop:1 transparent);"
        )
        layout.addWidget(divider)

        # ==========================================
        # RIGHT SIDE
        # ==========================================
        right_frame = QWidget()
        right_frame.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(80, 60, 80, 60)
        right_layout.setAlignment(Qt.AlignCenter)

        form_container = QWidget()
        form_container.setMaximumWidth(400)
        form_container.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        welcome = QLabel("Create Account")
        welcome.setStyleSheet(f"color:{COLOR_TEXT}; font-size:32px; font-weight:800; background:transparent; border:none;")
        form_layout.addWidget(welcome)
        
        sub = QLabel("Start your premium entertainment journey.")
        sub.setStyleSheet(f"color:{COLOR_TEXT_DIM}; font-size:14px; background:transparent; border:none;")
        form_layout.addWidget(sub)
        form_layout.addSpacing(10)

        self.username_input = self._create_input("Username")
        form_layout.addWidget(self.username_input)

        self.email_input = self._create_input("Email Address")
        form_layout.addWidget(self.email_input)

        self.password_input = self._create_password_input("Password")
        form_layout.addWidget(self.password_input)

        self.confirm_input = self._create_password_input("Confirm Password")
        form_layout.addWidget(self.confirm_input)

        hint = QLabel("Password must be at least 8 characters.")
        hint.setStyleSheet(f"color:{COLOR_TEXT_DIM}; font-size:11px; background:transparent; border:none;")
        form_layout.addWidget(hint)

        form_layout.addSpacing(10)

        self.register_btn = GradientButton("Create Account", "navigation/user-plus")
        self.register_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.register_btn.clicked.connect(self._handle_register)
        form_layout.addWidget(self.register_btn)

        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignCenter)
        
        log_lbl = QLabel("Already have an account?")
        log_lbl.setStyleSheet(f"color:{COLOR_TEXT_DIM}; font-size:13px;")
        
        log_btn = QPushButton("Sign In")
        log_btn.setCursor(Qt.PointingHandCursor)
        log_btn.setStyleSheet(f"background:transparent; color:{COLOR_PURPLE}; border:none; font-weight:700; font-size:13px;")
        log_btn.clicked.connect(self.go_to_login.emit)
        
        login_layout.addWidget(log_lbl)
        login_layout.addWidget(log_btn)
        form_layout.addLayout(login_layout)

        right_layout.addWidget(form_container)
        layout.addWidget(right_frame, 1)

        fade_in(form_container, duration=600)

    def clear_fields(self) -> None:
        """Wipes the form if needed."""
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.textbox.clear()
        self.confirm_input.textbox.clear()

    def _handle_register(self) -> None:
        user = self.username_input.text().strip()
        email = self.email_input.text().strip()
        pwd = self.password_input.textbox.text()
        confirm = self.confirm_input.textbox.text()

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
            create_user(user, email, pwd, role="User")
            Toast(self.window(), "Account Created", "Welcome to VyBora!", "success").show_toast()
            self.register_successful.emit("User", user)
        except UserExistsError as e:
            Toast(self.window(), "Registration Failed", str(e), "error").show_toast()
        except Exception:
            Toast(self.window(), "Database Error", "Could not create account.", "error").show_toast()

    def _create_feature_card(self, icon_name: str, title: str, desc: str, glow_color: str) -> QFrame:
        card = QFrame()
        card.setFixedWidth(320)
        card.setCursor(Qt.PointingHandCursor)
        
        card.setStyleSheet(f"background-color: rgba(255, 255, 255, 5); border: 1px solid {glow_color}; border-radius: 12px;")
        
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(20)
        color = QColor(glow_color)
        color.setAlpha(100) 
        shadow.setColor(color)
        shadow.setOffset(0, 0)
        card.setGraphicsEffect(shadow)
        
        glow_anim = QVariantAnimation(card, startValue=20.0, endValue=35.0, duration=200)
        glow_anim.valueChanged.connect(lambda v: shadow.setBlurRadius(v))
        glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def enter_event(event):
            glow_anim.setDirection(QVariantAnimation.Direction.Forward)
            glow_anim.start()
            card.setStyleSheet(f"background-color: rgba(255, 255, 255, 10); border: 1px solid {glow_color}; border-radius: 12px;")
            super(QFrame, card).enterEvent(event)

        def leave_event(event):
            glow_anim.setDirection(QVariantAnimation.Direction.Backward)
            glow_anim.start()
            card.setStyleSheet(f"background-color: rgba(255, 255, 255, 5); border: 1px solid {glow_color}; border-radius: 12px;")
            super(QFrame, card).leaveEvent(event)
            
        card.enterEvent = enter_event
        card.leaveEvent = leave_event

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(16)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon(icon_name, glow_color, 24).pixmap(24, 24))
        icon_lbl.setStyleSheet("background: transparent; border: none;")
        card_layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: 700; background: transparent; border: none;")
        text_layout.addWidget(title_lbl)
        
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color: #A5A0B8; font-size: 12px; background: transparent; border: none;")
        text_layout.addWidget(desc_lbl)

        card_layout.addLayout(text_layout)
        return card

    def _create_input(self, placeholder: str) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(50)
        
        # STATIC QSS: Fixes cursor blinking
        inp.setStyleSheet(
            f"QLineEdit {{ background-color: {COLOR_SURFACE}; color: {COLOR_TEXT};"
            f"border: 1px solid rgba(255, 255, 255, 20); border-radius: 8px; padding: 0 16px; font-size: 14px;"
            f"selection-background-color: {COLOR_PURPLE}; selection-color: white; }}"
            f"QLineEdit:focus {{ border: 1px solid {COLOR_PURPLE}; background-color: rgba(27, 25, 41, 1); }}"
        )
        return inp

    def _create_password_input(self, placeholder: str) -> QWidget:
        container = QWidget()
        container.setFixedHeight(50)
        container.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(50)
        inp.setEchoMode(QLineEdit.Password)
        
        inp.setStyleSheet(
            f"QLineEdit {{ background-color: {COLOR_SURFACE}; color: {COLOR_TEXT};"
            f"border: 1px solid rgba(255, 255, 255, 20); border-radius: 8px; padding: 0 16px; padding-right: 45px; font-size: 14px;"
            f"selection-background-color: {COLOR_PURPLE}; selection-color: white; }}"
            f"QLineEdit:focus {{ border: 1px solid {COLOR_PURPLE}; background-color: rgba(27, 25, 41, 1); }}"
        )

        layout.addWidget(inp)

        btn = QPushButton(container)
        btn.setIcon(get_icon("system/eye", COLOR_TEXT_DIM, 20))
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("background: transparent; border: none;")
        
        btn.setParent(container)
        btn.move(340 - 40, 10)
        
        def toggle():
            if inp.echoMode() == QLineEdit.Password:
                inp.setEchoMode(QLineEdit.Normal)
                btn.setIcon(get_icon("system/eye-off", COLOR_TEXT_DIM, 20))
            else:
                inp.setEchoMode(QLineEdit.Password)
                btn.setIcon(get_icon("system/eye", COLOR_TEXT_DIM, 20))

        btn.clicked.connect(toggle)

        def resize_event(event):
            btn.move(container.width() - 40, 10)
        
        container.resizeEvent = resize_event
        container.textbox = inp
        
        return container