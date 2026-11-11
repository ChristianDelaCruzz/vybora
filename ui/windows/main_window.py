"""Single application window with dynamic global theming."""
import traceback
from PySide6.QtCore import QThreadPool, QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QApplication

from config.settings import COLOR_PURPLE, COLOR_BG, PROJECT_ROOT
from PySide6.QtGui import QIcon

from ui.components.sidebar import Sidebar
from ui.components.header import Header
from ui.components.toast import Toast
from ui.components.animation_manager import fade_in
from modules.settings.settings_manager import settings_manager
from ui.app_state import theme_state
from database import user_repository


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VyBora")
        self.resize(1280, 800)
        self.setMinimumSize(800, 600)

        icon_path = PROJECT_ROOT / "assets" / "icons" / "navigation" / "app.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.current_role: str = "User"

        # ---------------- SAFE IMPORTS ----------------
        try:
            from ui.pages.login_page import LoginPage
            from ui.pages.register_page import RegisterPage
            from ui.pages.home_page import HomePage
            from ui.pages.movies_tv_page import MoviesTvPage
            from ui.pages.media_details_page import MediaDetailsPage
            from ui.pages.search_page import SearchPage
            from ui.pages.profile_page import ProfilePage
            from ui.pages.settings_page import SettingsPage
        except Exception:
            print("\n=== PAGE IMPORT FAILED ===")
            traceback.print_exc()
            print("===========================\n")
            raise

        try:
            from ui.pages.favorites_page import FavoritesPage
            from ui.pages.playlists_page import PlaylistsPage
            from ui.pages.history_page import HistoryPage
        except Exception:
            print("\n=== OPTIONAL PAGE IMPORT FAILED (using placeholders) ===")
            traceback.print_exc()
            print("====================================================\n")
            FavoritesPage = PlaylistsPage = HistoryPage = lambda: QWidget()

        try:
            from ui.pages.game_library_page import GameLibraryPage
            from ui.pages.popular_games_page import PopularGamesPage
            from ui.pages.music_audio_page import MusicAudioPage
        except Exception:
            print("\n=== GAME/MUSIC PAGE IMPORT FAILED ===")
            traceback.print_exc()
            print("=====================================\n")
            GameLibraryPage = PopularGamesPage = MusicAudioPage = lambda: QWidget()

        try:
            from ui.pages.admin_dashboard import AdminDashboard
        except Exception:
            AdminDashboard = lambda: QWidget()

        try:
            from ui.pages.admin_management_pages import (
                AdminGamesPage, AdminMoviesPage, AdminUsersPage, AdminApiPage, AdminLogsPage
            )
        except Exception:
            AdminGamesPage = AdminMoviesPage = AdminUsersPage = AdminApiPage = AdminLogsPage = lambda: QWidget()

        # ---------------- BUILD UI ----------------
        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)

        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.app_container = QWidget()
        self.app_container.setObjectName("app_container")
        self.app_layout = QHBoxLayout(self.app_container)
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.app_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigate.connect(self._on_navigate)
        self.sidebar.logout_requested.connect(self._logout)
        self.app_layout.addWidget(self.sidebar)

        self.sidebar.set_items([
            ("Discover", [
                ("home",          "Home",          "navigation/home"),
                ("game_library",  "Game Library",  "navigation/gamepad-2"),
                ("popular_games", "Popular Games", "dashboard/trending-up"),
                ("movies_tv",     "Movies & TV",   "navigation/clapperboard"),
                ("music_library", "Music & Audio", "navigation/music-2"),
            ]),
            ("My VyBora", [
                ("favorites", "Favorites", "navigation/heart"),
                ("playlists", "Playlists", "navigation/list-music"),
                ("history",   "History",   "system/clock"),
            ]),
            ("Account", [
                ("profile",  "Profile",  "navigation/user-round"),
                ("settings", "Settings", "navigation/settings"),
            ]),
        ])

        for key, label, icon in [
            ("admin",        "Dashboard",     "admin/layout-dashboard"),
            ("admin_games",  "Manage Games",  "navigation/gamepad-2"),
            ("admin_movies", "Manage Movies", "navigation/clapperboard"),
            ("admin_users",  "Manage Users",  "navigation/user-round"),
            ("admin_api",    "Manage APIs",   "navigation/settings"),
            ("admin_logs",   "Activity Logs", "system/clipboard-list"),
        ]:
            self.sidebar.add_admin_item(key, label, icon)

        right_container = QWidget()
        right_container.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.header = Header()
        self.header.search_submitted.connect(self._on_search_requested)
        self.header.toggle_sidebar.connect(self._toggle_sidebar)
        self.header.logout_requested.connect(self._logout)
        self.header.profile_requested.connect(lambda: self._on_navigate("profile"))
        self.header.settings_requested.connect(lambda: self._on_navigate("settings"))

        right_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        right_layout.addWidget(self.stack, 1)
        self.app_layout.addWidget(right_container, 1)

        # ---------------- INIT PAGES ----------------
        try:
            self.home_page = HomePage()
            self.movies_tv = MoviesTvPage()
            self.search_page = SearchPage()
            self.details = MediaDetailsPage()
            self.favorites_page = FavoritesPage()
            self.playlists_page = PlaylistsPage()
            self.history_page = HistoryPage()
            self.profile_page = ProfilePage()
            self.settings_page = SettingsPage()

            self.game_library_page = GameLibraryPage()
            self.popular_games_page = PopularGamesPage()
            self.music_audio_page = MusicAudioPage()

            self.admin_dashboard = AdminDashboard()
            self.admin_games = AdminGamesPage()
            self.admin_movies = AdminMoviesPage()
            self.admin_users = AdminUsersPage()
            self.admin_api = AdminApiPage()
            self.admin_logs = AdminLogsPage()
        except Exception:
            print("\n=== PAGE INSTANTIATION FAILED ===")
            traceback.print_exc()
            print("==================================\n")
            raise

        # Add to stack in order
        self.stack.addWidget(self.home_page)            # 0
        self.stack.addWidget(self.movies_tv)            # 1
        self.stack.addWidget(self.search_page)          # 2
        self.stack.addWidget(self.details)              # 3
        self.stack.addWidget(self.favorites_page)       # 4
        self.stack.addWidget(self.playlists_page)       # 5
        self.stack.addWidget(self.history_page)         # 6
        self.stack.addWidget(self.profile_page)         # 7
        self.stack.addWidget(self.settings_page)        # 8
        self.stack.addWidget(self.admin_dashboard)      # 9
        self.stack.addWidget(self.admin_games)          # 10
        self.stack.addWidget(self.admin_movies)         # 11
        self.stack.addWidget(self.admin_users)          # 12
        self.stack.addWidget(self.admin_api)            # 13
        self.stack.addWidget(self.admin_logs)           # 14
        self.stack.addWidget(self.game_library_page)    # 15
        self.stack.addWidget(self.popular_games_page)   # 16
        self.stack.addWidget(self.music_audio_page)     # 17

        # ---------------- AUTH ----------------
        self.login_page = LoginPage()
        self.register_page = RegisterPage()

        self.login_page.login_successful.connect(self._show_app_ui)
        self.login_page.go_to_register.connect(self._show_register)
        self.register_page.register_successful.connect(self._show_login)
        self.register_page.go_to_login.connect(self._show_login)

        self.main_layout.addWidget(self.login_page)
        self.main_layout.addWidget(self.register_page)
        self.main_layout.addWidget(self.app_container)

        # ---------------- SIGNALS ----------------
        try:
            self.home_page.open_details.connect(self._open_details)
            self.movies_tv.open_details.connect(self._open_details)
            self.search_page.open_details.connect(self._open_details)
            self.details.back_requested.connect(self._on_back)
        except Exception:
            pass

        try:
            self.favorites_page.explore_clicked.connect(lambda: self._on_navigate("movies_tv"))
        except Exception:
            pass

        try:
            self.profile_page.username_changed.connect(self._on_username_changed)
        except Exception:
            pass

        try:
            self.settings_page.account_deleted.connect(self._logout)
        except Exception:
            pass

        try:
            settings_manager.appearance_changed.connect(self._apply_global_appearance)
        except Exception:
            pass

        self._is_sidebar_collapsed = False
        self._previous_tab = "home"

        QTimer.singleShot(0, self._show_login)

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    def _show_login(self) -> None:
        try:
            self._force_dark_theme()
        except Exception:
            pass
        self.login_page.show()
        self.register_page.hide()
        self.app_container.hide()

    def _force_dark_theme(self):
        app_ss = f"""
            QMainWindow {{ background-color: {COLOR_BG}; }}
            QWidget {{ background-color: transparent; color: #F5F3FF; }}
            QLabel {{ background: transparent; color: #F5F3FF; }}
            QPushButton {{ background-color: #29263B; color: #F5F3FF; border-radius: 8px; padding: 8px; }}
            QLineEdit {{ background-color: #1B1929; color: #F5F3FF; border: 1px solid rgba(255,255,255,20); border-radius: 8px; padding: 8px; }}
        """
        QApplication.instance().setStyleSheet(app_ss)

    def _show_register(self) -> None:
        try:
            self._force_dark_theme()
        except Exception:
            pass
        self.login_page.hide()
        self.register_page.show()
        self.app_container.hide()

    def _show_app_ui(self, role: str, username: str) -> None:
        self.current_role = role
        self.header.set_user(username, role)
        self.sidebar.set_user(username, role)

        try:
            user_data = user_repository.get_user_profile(username)
            user_id = user_data.get("user_id", 1) if user_data else 1
            self.profile_page.load_user_data(username)
            self.settings_page.load_user_settings(user_id)
        except Exception:
            traceback.print_exc()

        if role == "Admin":
            self.sidebar.show_admin_nav()
            self._on_navigate("admin")
        else:
            self.sidebar.hide_admin_nav()
            self._on_navigate("home")

        self.login_page.hide()
        self.register_page.hide()
        self.app_container.show()

        if role != "Admin" and hasattr(self.home_page, "reload"):
            QTimer.singleShot(50, self.home_page.reload)

        Toast(self, f"Welcome, {username}!", "You have successfully signed in.", "success").show_toast()

    def _on_username_changed(self, new_username: str):
        role = getattr(self, "current_role", "User")
        self.header.set_user(new_username, role)
        self.sidebar.set_user(new_username, role)

    def _logout(self) -> None:
        try:
            settings_manager.clear()
        except Exception:
            pass

        self.sidebar.clear_user()
        self.header.clear_user()
        self.sidebar.hide_admin_nav()

        if hasattr(self.login_page, "clear_fields"):
            self.login_page.clear_fields()
        if hasattr(self.register_page, "clear_fields"):
            self.register_page.clear_fields()

        self._previous_tab = "home"
        self._show_login()
        Toast(self, "Signed out", "See you soon!", "info").show_toast()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def _apply_global_appearance(self, settings: dict):
        if not settings:
            return

        theme = settings.get("theme", "Dark Mode")
        theme_state.is_light = (theme == "Light Mode")

        font_size = settings.get("font_size", "Medium")
        app_font = QApplication.instance().font()
        if font_size == "Small":
            app_font.setPointSize(9)
        elif font_size == "Large":
            app_font.setPointSize(13)
        else:
            app_font.setPointSize(11)
        QApplication.instance().setFont(app_font)

        sidebar_behavior = settings.get("sidebar", "Expanded")
        if sidebar_behavior == "Collapsed":
            self.sidebar.collapse()
        elif sidebar_behavior == "Expanded":
            self.sidebar.expand()

        if theme_state.is_light:
            app_ss = f"""
                QMainWindow, QWidget#root, QWidget#app_container {{ background-color: {theme_state.bg()}; color: {theme_state.text()}; }}
                QLabel {{ background: transparent; color: {theme_state.text()}; border: none; }}
                QPushButton {{ background-color: #E0D8FF; color: #100E1B; border-radius: 8px; font-weight: 700; border: none; padding: 8px; }}
                QPushButton:hover {{ background-color: #D0C4FF; }}
                QLineEdit {{ background-color: #FFFFFF; color: #100E1B; border: 1px solid {theme_state.border()}; border-radius: 8px; padding: 8px; }}
                QScrollArea {{ border: none; background: transparent; }}
                QScrollArea > QWidget > QWidget {{ background: transparent; }}
                QScrollBar:vertical {{ border: none; background: transparent; width: 10px; margin: 0px; }}
                QScrollBar::handle:vertical {{ background: #D1CCE0; min-height: 30px; border-radius: 5px; }}
                QScrollBar::handle:vertical:hover {{ background: {COLOR_PURPLE}; }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
            """
        else:
            app_ss = f"""
                QMainWindow {{ background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(118, 85, 239, 60), stop:0.3 rgba(57, 133, 255, 30), stop:0.7 rgba(16, 14, 27, 255), stop:1 rgba(16, 14, 27, 255)); }}
                QWidget#root, QWidget#app_container {{ background-color: transparent; color: {theme_state.text()}; }}
                QLabel {{ background: transparent; color: {theme_state.text()}; border: none; }}
                QPushButton {{ background-color: #29263B; color: #F5F3FF; border-radius: 8px; font-weight: 700; border: none; padding: 8px; }}
                QPushButton:hover {{ background-color: #3B2C59; }}
                QLineEdit {{ background-color: #100E1B; color: #F5F3FF; border: 1px solid rgba(255,255,255,20); border-radius: 8px; padding: 8px; }}
                QScrollArea {{ border: none; background: transparent; }}
                QScrollArea > QWidget > QWidget {{ background: transparent; }}
                QScrollBar:vertical {{ border: none; background: transparent; width: 10px; margin: 0px; }}
                QScrollBar::handle:vertical {{ background: #3B2C59; min-height: 30px; border-radius: 5px; }}
                QScrollBar::handle:vertical:hover {{ background: {COLOR_PURPLE}; }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
            """

        app = QApplication.instance()
        app.setStyleSheet(app_ss)

        # Refresh custom widgets
        for widget in (
            self.sidebar,
            self.header,
            self.settings_page,
            self.profile_page,
            self.favorites_page,
            self.playlists_page,
            self.history_page,
            self.game_library_page,
            self.popular_games_page,
            self.music_audio_page,
            self.movies_tv,
            self.details,
            self.search_page,
        ):
            try:
                if hasattr(widget, "refresh_theme"):
                    widget.refresh_theme()
            except Exception:
                traceback.print_exc()

        app.processEvents()

        for widget in app.allWidgets():
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    # ------------------------------------------------------------------
    # Layout / Navigation
    # ------------------------------------------------------------------
    def _toggle_sidebar(self) -> None:
        if self._is_sidebar_collapsed:
            self._is_sidebar_collapsed = False
            self.sidebar.expand()
        else:
            self._is_sidebar_collapsed = True
            self.sidebar.collapse()

    def _on_navigate(self, page_id: str) -> None:
        self._previous_tab = page_id
        self.sidebar.set_active(page_id)

        routes = {
            "home":          (0,  self.home_page),
            "movies_tv":     (1,  self.movies_tv),
            "search":        (2,  self.search_page),
            "favorites":     (4,  self.favorites_page),
            "playlists":     (5,  self.playlists_page),
            "history":       (6,  self.history_page),
            "profile":       (7,  self.profile_page),
            "settings":      (8,  self.settings_page),
            "admin":         (9,  self.admin_dashboard),
            "admin_games":   (10, self.admin_games),
            "admin_movies":  (11, self.admin_movies),
            "admin_users":   (12, self.admin_users),
            "admin_api":     (13, self.admin_api),
            "admin_logs":    (14, self.admin_logs),
            "game_library":  (15, self.game_library_page),
            "popular_games": (16, self.popular_games_page),
            "music_library": (17, self.music_audio_page),
        }

        if page_id in routes:
            idx, widget = routes[page_id]
            self.stack.setCurrentIndex(idx)
            if page_id == "home" and hasattr(self.home_page, "reload"):
                self.home_page.reload()
            fade_in(widget, 220)
        else:
            Toast(self, "Coming Soon", f"The {page_id.replace('_', ' ').title()} page is under construction.", "info").show_toast()
            self.stack.setCurrentIndex(0)
            self.sidebar.set_active("home")
            fade_in(self.home_page, 220)

    def _on_search_requested(self, query: str) -> None:
        if not query.strip():
            return
        self._previous_tab = "search"
        self.sidebar.set_active("search")
        self.search_page.load_query(query)
        self.stack.setCurrentIndex(2)
        fade_in(self.search_page, 220)

    def _open_details(self, tmdb_id: int, media_type: str) -> None:
        self.sidebar.set_active("")
        self.details.load(media_type, tmdb_id)
        self.stack.setCurrentIndex(3)
        fade_in(self.details, 220)

    def _on_back(self) -> None:
        if self._previous_tab == "search":
            self.sidebar.set_active("search")
            self.stack.setCurrentIndex(2)
            fade_in(self.search_page, 220)
        else:
            self._on_navigate(self._previous_tab)

    def closeEvent(self, event) -> None:
        try:
            if hasattr(self.home_page, "hero") and hasattr(self.home_page.hero, "timer"):
                self.home_page.hero.timer.stop()
        except Exception:
            pass
        try:
            QThreadPool.globalInstance().waitForDone(1000)
        except Exception:
            pass
        super().closeEvent(event)