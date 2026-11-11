"""Centralized Real-Time Settings Manager."""
from PySide6.QtCore import QObject, Signal
from database import user_repository

class SettingsManager(QObject):
    # Signals for the rest of the app to listen to
    appearance_changed = Signal(dict)
    playback_changed = Signal(dict)
    notifications_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.current_user_id = None
        self.current_settings = {}

    def load_for_user(self, user_id: int):
        """Called immediately after login."""
        self.current_user_id = user_id
        self.current_settings = user_repository.get_settings(user_id)
        
        # Broadcast the initial load to force the app to update
        self.appearance_changed.emit(self.current_settings)
        self.playback_changed.emit(self.current_settings)
        self.notifications_changed.emit(self.current_settings)

    def clear(self):
        """Called on logout to prevent data leaking to the next user."""
        self.current_user_id = None
        self.current_settings = {}

    def update_setting(self, key: str, value):
        """Called by the Settings Page when a user clicks a toggle."""
        if not self.current_user_id:
            return
            
        # 1. Save to DB
        user_repository.save_setting(self.current_user_id, key, value)
        
        # 2. Update local state
        self.current_settings[key] = value
        
        # 3. Broadcast to the app
        if key in ["theme", "accent_color", "font_size", "animations", "sidebar", "background_effects"]:
            self.appearance_changed.emit(self.current_settings)
        elif key in ["autoplay_episode", "video_quality", "remember_position", "subtitles", "autoplay_track", "shuffle", "repeat_mode"]:
            self.playback_changed.emit(self.current_settings)
        elif key in ["notifications_enabled", "toast_notifications", "new_content", "playback_notif"]:
            self.notifications_changed.emit(self.current_settings)

# Global Instance
settings_manager = SettingsManager()