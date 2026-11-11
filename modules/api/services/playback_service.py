"""Playback service - resolves how to play content based on its type."""
import subprocess
import os

class PlaybackService:
    @staticmethod
    def validate_local_executable(path: str) -> bool:
        """Validate that a local game executable exists and is a file."""
        if not path or not os.path.isfile(path):
            return False
        # Optional: restrict extensions
        allowed = (".exe",)
        return path.lower().endswith(allowed)

    @staticmethod
    def launch_local_game(path: str, args: list = None) -> bool:
        """Launch a local game safely using subprocess with argument list."""
        if not PlaybackService.validate_local_executable(path):
            return False
        try:
            cmd = [path] + (args or [])
            subprocess.Popen(cmd, shell=False)  # shell=False is critical for security
            return True
        except Exception:
            return False