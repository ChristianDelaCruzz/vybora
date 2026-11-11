"""Settings Page - Uses Central Settings Manager with full light/dark theming."""
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QCheckBox, QComboBox, 
    QScrollArea, QPushButton, QApplication
)

from ui.app_state import theme_state
from ui.components.toast import Toast
from ui.components.icon_manager import get_icon
from database import user_repository
from modules.settings.settings_manager import settings_manager


class SettingsPage(QWidget):
    account_deleted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self._user_id = None
        
        # Track widgets for theme refresh
        self._section_labels: list[QLabel] = []
        self._row_titles: list[QLabel] = []
        self._row_descs: list[QLabel] = []
        self._panels: list[QFrame] = []
        self._combos: list[QComboBox] = []
        self._toggles: list[QCheckBox] = []
        self._danger_buttons: list[QPushButton] = []
        
        settings_manager.appearance_changed.connect(self._sync_ui)
        settings_manager.playback_changed.connect(self._sync_ui)
        settings_manager.notifications_changed.connect(self._sync_ui)
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        self.header_lbl = QLabel("Settings")
        self.header_lbl.setStyleSheet("font-size: 24px; font-weight: 700; background: transparent; border: none;")
        root.addWidget(self.header_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        scroll.viewport().setStyleSheet("background: transparent;")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(24)

        # APPEARANCE
        lay.addWidget(self._section_title("APPEARANCE"))
        app_panel = self._panel()
        a_lay = QVBoxLayout()
        a_lay.setSpacing(20)

        self.theme_combo = self._combo(["Dark Mode", "Light Mode", "System Default"])
        self.theme_combo.currentTextChanged.connect(lambda v: settings_manager.update_setting("theme", v))
        a_lay.addLayout(self._row("Theme", "Choose how VyBora looks.", self.theme_combo))

        self.accent_combo = self._combo(["Purple", "Electric Blue", "Pink"])
        self.accent_combo.currentTextChanged.connect(lambda v: settings_manager.update_setting("accent_color", v))
        a_lay.addLayout(self._row("Accent Color", "Choose the primary highlight color.", self.accent_combo))

        self.font_combo = self._combo(["Small", "Medium", "Large"])
        self.font_combo.currentTextChanged.connect(lambda v: settings_manager.update_setting("font_size", v))
        a_lay.addLayout(self._row("Font Size", "Adjust text size across the app.", self.font_combo))

        self.anim_toggle = self._toggle(True)
        self.anim_toggle.stateChanged.connect(lambda s: settings_manager.update_setting("animations", 1 if s == Qt.Checked else 0))
        a_lay.addLayout(self._row("UI Animations", "Enable smooth page transitions and hover effects.", self.anim_toggle))

        self.sidebar_combo = self._combo(["Expanded", "Collapsed", "Automatic"])
        self.sidebar_combo.currentTextChanged.connect(lambda v: settings_manager.update_setting("sidebar", v))
        a_lay.addLayout(self._row("Sidebar Appearance", "Keep the sidebar expanded, collapsed, or automatic.", self.sidebar_combo))
        
        app_panel.layout().addLayout(a_lay)
        lay.addWidget(app_panel)

        # PLAYBACK
        lay.addWidget(self._section_title("PLAYBACK"))
        pb_panel = self._panel()
        p_lay = QVBoxLayout()
        p_lay.setSpacing(20)

        self.autoplay_ep = self._toggle(True)
        self.autoplay_ep.stateChanged.connect(lambda s: settings_manager.update_setting("autoplay_episode", 1 if s == Qt.Checked else 0))
        p_lay.addLayout(self._row("Autoplay Next Episode", "Automatically start the next TV episode.", self.autoplay_ep))

        self.quality_combo = self._combo(["Auto", "1080p", "720p", "480p"])
        self.quality_combo.currentTextChanged.connect(lambda v: settings_manager.update_setting("video_quality", v))
        p_lay.addLayout(self._row("Default Video Quality", "Stream in this resolution when available.", self.quality_combo))

        self.remember_toggle = self._toggle(True)
        self.remember_toggle.stateChanged.connect(lambda s: settings_manager.update_setting("remember_position", 1 if s == Qt.Checked else 0))
        p_lay.addLayout(self._row("Remember Playback Position", "Resume from where you left off.", self.remember_toggle))

        self.subs_combo = self._combo(["English", "Spanish", "French", "Off"])
        self.subs_combo.currentTextChanged.connect(lambda v: settings_manager.update_setting("subtitles", v))
        p_lay.addLayout(self._row("Default Subtitle Language", "Select your preferred subtitle language.", self.subs_combo))

        self.autoplay_track = self._toggle(True)
        self.autoplay_track.stateChanged.connect(lambda s: settings_manager.update_setting("autoplay_track", 1 if s == Qt.Checked else 0))
        p_lay.addLayout(self._row("Autoplay Next Track", "Continue playing the next song in the queue.", self.autoplay_track))

        self.shuffle_toggle = self._toggle(False)
        self.shuffle_toggle.stateChanged.connect(lambda s: settings_manager.update_setting("shuffle", 1 if s == Qt.Checked else 0))
        p_lay.addLayout(self._row("Shuffle by Default", "Start music playback in random order.", self.shuffle_toggle))

        self.repeat_combo = self._combo(["Off", "Repeat One", "Repeat All"])
        self.repeat_combo.currentTextChanged.connect(lambda v: settings_manager.update_setting("repeat_mode", v))
        p_lay.addLayout(self._row("Repeat Mode", "Loop a single track or the entire queue.", self.repeat_combo))
        
        pb_panel.layout().addLayout(p_lay)
        lay.addWidget(pb_panel)

        # NOTIFICATIONS
        lay.addWidget(self._section_title("NOTIFICATIONS"))
        n_panel = self._panel()
        n_lay = QVBoxLayout()
        n_lay.setSpacing(20)

        self.master_notif = self._toggle(True)
        self.master_notif.stateChanged.connect(lambda s: settings_manager.update_setting("notifications_enabled", 1 if s == Qt.Checked else 0))
        n_lay.addLayout(self._row("Enable Notifications", "Master switch for all alerts.", self.master_notif))

        self.toast_toggle = self._toggle(True)
        self.toast_toggle.stateChanged.connect(lambda s: settings_manager.update_setting("toast_notifications", 1 if s == Qt.Checked else 0))
        n_lay.addLayout(self._row("Toast Notifications", "Show popups for actions and updates.", self.toast_toggle))

        self.new_content_toggle = self._toggle(True)
        self.new_content_toggle.stateChanged.connect(lambda s: settings_manager.update_setting("new_content", 1 if s == Qt.Checked else 0))
        n_lay.addLayout(self._row("New Content Alerts", "Notify when new movies or music is added.", self.new_content_toggle))

        self.playback_toggle = self._toggle(False)
        self.playback_toggle.stateChanged.connect(lambda s: settings_manager.update_setting("playback_notif", 1 if s == Qt.Checked else 0))
        n_lay.addLayout(self._row("Playback Notifications", "Show alerts when media starts or stops.", self.playback_toggle))
        
        n_panel.layout().addLayout(n_lay)
        lay.addWidget(n_panel)

        # DANGER ZONE
        lay.addWidget(self._section_title("DANGER ZONE"))
        d_panel = self._panel()
        d_panel.setObjectName("danger")
        d_lay = QVBoxLayout()
        d_lay.setSpacing(20)

        clear_hist_btn = self._danger_button("  Clear History", "system/trash-2")
        clear_hist_btn.clicked.connect(self._clear_history)
        d_lay.addLayout(self._row("Clear Viewing & Music History", "Remove all recorded watch and listen history.", clear_hist_btn))

        clear_cache_btn = self._danger_button("  Clear Cache", "system/refresh-cw")
        clear_cache_btn.clicked.connect(self._clear_cache)
        d_lay.addLayout(self._row("Clear Cache", "Free up storage by removing temporary files and images.", clear_cache_btn))

        reset_btn = self._danger_button("  Reset Settings", "system/alert-triangle")
        reset_btn.clicked.connect(self._reset_settings)
        d_lay.addLayout(self._row("Reset Settings", "Restore all preferences to their default values.", reset_btn))

        delete_acc_btn = self._delete_button("  Delete Account", "system/x")
        delete_acc_btn.clicked.connect(self._delete_account)
        d_lay.addLayout(self._row("Delete Account", "Permanently delete your profile and all associated data.", delete_acc_btn))

        d_panel.layout().addLayout(d_lay)
        lay.addWidget(d_panel)
        lay.addStretch(1)

        scroll.setWidget(content)
        root.addWidget(scroll)
        
        # Apply theme now
        self.refresh_theme()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def refresh_theme(self) -> None:
        text_color = theme_state.text()
        text_dim = theme_state.text_dim()
        surface = theme_state.surface()
        border = theme_state.border()
        bg = theme_state.bg()
        accent = theme_state.accent_hex

        self.header_lbl.setStyleSheet(f"color: {text_color}; font-size: 24px; font-weight: 700; background: transparent; border: none;")
        
        # Section titles
        for lbl in self._section_labels:
            lbl.setStyleSheet(f"color: {text_dim}; font-size: 12px; font-weight: 900; letter-spacing: 1px; background: transparent; border: none; margin-top: 10px;")
            
        # Panels
        for panel in self._panels:
            if panel.objectName() == "danger":
                panel.setStyleSheet(f"background-color: rgba(239, 68, 68, 0.05); border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.3);")
            else:
                panel.setStyleSheet(f"background-color: {surface}; border-radius: 12px; border: 1px solid {border};")

        # Row labels
        for t in self._row_titles:
            t.setStyleSheet(f"color: {text_color}; font-size: 15px; font-weight: 700; background: transparent; border: none;")
        for d in self._row_descs:
            d.setStyleSheet(f"color: {text_dim}; font-size: 13px; background: transparent; border: none;")

        # Combo boxes
        combo_qss = f"""
            QComboBox {{ background-color: {bg}; color: {text_color}; border: 1px solid {border}; border-radius: 8px; padding: 0 12px; outline: none; font-weight: 600; }}
            QComboBox:hover {{ border-color: {accent}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{ background-color: {surface}; color: {text_color}; border: 1px solid {accent}; selection-background-color: {accent}; selection-color: white; outline: none; }}
        """
        for cb in self._combos:
            cb.setStyleSheet(combo_qss)

        # Checkboxes
        check_qss = f"""
            QCheckBox {{ background: transparent; border: none; }}
            QCheckBox::indicator {{ width: 22px; height: 22px; border-radius: 6px; border: 1px solid {text_dim}; background: transparent; }}
            QCheckBox::indicator:checked {{ background: {accent}; border-color: {accent}; image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiI+PC9wb2x5bGluZT48L3N2Zz4=); }}
        """
        for cb in self._toggles:
            cb.setStyleSheet(check_qss)

    # ------------------------------------------------------------------
    # Settings load / save
    # ------------------------------------------------------------------
    def load_user_settings(self, user_id: int):
        self._user_id = user_id
        settings_manager.load_for_user(user_id)

    def _sync_ui(self, settings: dict):
        if not settings:
            return
        
        all_widgets = [
            self.theme_combo, self.accent_combo, self.font_combo, self.sidebar_combo,
            self.quality_combo, self.subs_combo, self.repeat_combo,
            self.anim_toggle, self.autoplay_ep, self.remember_toggle,
            self.autoplay_track, self.shuffle_toggle, self.master_notif,
            self.toast_toggle, self.new_content_toggle, self.playback_toggle,
        ]
        for w in all_widgets:
            w.blockSignals(True)

        self.theme_combo.setCurrentText(settings.get("theme", "Dark Mode"))
        self.accent_combo.setCurrentText(settings.get("accent_color", "Purple"))
        self.font_combo.setCurrentText(settings.get("font_size", "Medium"))
        self.sidebar_combo.setCurrentText(settings.get("sidebar", "Expanded"))
        self.quality_combo.setCurrentText(settings.get("video_quality", "Auto"))
        self.subs_combo.setCurrentText(settings.get("subtitles", "English"))
        self.repeat_combo.setCurrentText(settings.get("repeat_mode", "Off"))
        
        self.anim_toggle.setChecked(bool(settings.get("animations", 1)))
        self.autoplay_ep.setChecked(bool(settings.get("autoplay_episode", 1)))
        self.remember_toggle.setChecked(bool(settings.get("remember_position", 1)))
        self.autoplay_track.setChecked(bool(settings.get("autoplay_track", 1)))
        self.shuffle_toggle.setChecked(bool(settings.get("shuffle", 0)))
        self.master_notif.setChecked(bool(settings.get("notifications_enabled", 1)))
        self.toast_toggle.setChecked(bool(settings.get("toast_notifications", 1)))
        self.new_content_toggle.setChecked(bool(settings.get("new_content", 1)))
        self.playback_toggle.setChecked(bool(settings.get("playback_notif", 0)))

        for w in all_widgets:
            w.blockSignals(False)

    # ------------------------------------------------------------------
    # Widget factories (now theme-aware)
    # ------------------------------------------------------------------
    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 12px; font-weight: 900; letter-spacing: 1px; background: transparent; border: none; margin-top: 10px;")
        self._section_labels.append(lbl)
        return lbl

    def _panel(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {theme_state.surface()}; border-radius: 12px; border: 1px solid {theme_state.border()};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        self._panels.append(panel)
        return panel

    def _row(self, title: str, desc: str, widget: QWidget) -> QHBoxLayout:
        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet(f"color: {theme_state.text()}; font-size: 15px; font-weight: 700; background: transparent; border: none;")
        d = QLabel(desc)
        d.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 13px; background: transparent; border: none;")
        self._row_titles.append(t)
        self._row_descs.append(d)
        col.addWidget(t)
        col.addWidget(d)
        row.addLayout(col, 1)
        row.addWidget(widget)
        return row

    def _toggle(self, checked: bool) -> QCheckBox:
        cb = QCheckBox()
        cb.setChecked(checked)
        cb.setStyleSheet(f"""
            QCheckBox {{ background: transparent; border: none; }}
            QCheckBox::indicator {{ width: 22px; height: 22px; border-radius: 6px; border: 1px solid {theme_state.text_dim()}; background: transparent; }}
            QCheckBox::indicator:checked {{ background: {theme_state.accent_hex}; border-color: {theme_state.accent_hex}; image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiI+PC9wb2x5bGluZT48L3N2Zz4=); }}
        """)
        self._toggles.append(cb)
        return cb

    def _combo(self, items: list[str]) -> QComboBox:
        cb = QComboBox()
        cb.addItems(items)
        cb.setFixedWidth(160)
        cb.setFixedHeight(36)
        cb.setStyleSheet(f"""
            QComboBox {{ background-color: {theme_state.bg()}; color: {theme_state.text()}; border: 1px solid {theme_state.border()}; border-radius: 8px; padding: 0 12px; outline: none; font-weight: 600; }}
            QComboBox:hover {{ border-color: {theme_state.accent_hex}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{ background-color: {theme_state.surface()}; color: {theme_state.text()}; border: 1px solid {theme_state.accent_hex}; selection-background-color: {theme_state.accent_hex}; selection-color: white; outline: none; }}
        """)
        self._combos.append(cb)
        return cb

    def _danger_button(self, text: str, icon_name: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setIcon(get_icon(icon_name, "#F87171", 16))
        btn.setIconSize(QSize(16, 16))
        btn.setFixedSize(160, 36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("QPushButton { background-color: rgba(239, 68, 68, 0.1); color: #F87171; border: 1px solid #F87171; border-radius: 8px; font-weight: 700; padding-left: 10px; } QPushButton:hover { background-color: #F87171; color: white; }")
        self._danger_buttons.append(btn)
        return btn

    def _delete_button(self, text: str, icon_name: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setIcon(get_icon(icon_name, "#FFFFFF", 16))
        btn.setIconSize(QSize(16, 16))
        btn.setFixedSize(160, 36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("QPushButton { background-color: #EF4444; color: white; border: none; border-radius: 8px; font-weight: 700; padding-left: 10px; } QPushButton:hover { background-color: #DC2626; }")
        self._danger_buttons.append(btn)
        return btn

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _clear_history(self):
        if user_repository.clear_user_history(self._user_id):
            Toast(self.window(), "Clear History", "Your history has been cleared.", "success").show_toast()
        else:
            Toast(self.window(), "Error", "Could not clear history.", "error").show_toast()

    def _clear_cache(self):
        freed = user_repository.clear_cache_files()
        Toast(self.window(), "Cache Cleared", f"Removed {freed} of temporary files.", "success").show_toast()

    def _reset_settings(self):
        if user_repository.reset_user_settings(self._user_id):
            settings_manager.load_for_user(self._user_id)
            Toast(self.window(), "Settings Reset", "All preferences restored to default.", "success").show_toast()

    def _delete_account(self):
        if user_repository.delete_user_account(self._user_id):
            Toast(self.window(), "Account Deleted", "Your account has been removed permanently.", "error").show_toast()
            self.account_deleted.emit()
        else:
            Toast(self.window(), "Error", "Could not delete account.", "error").show_toast()