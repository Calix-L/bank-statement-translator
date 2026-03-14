"""Progress tracking utilities."""

from __future__ import annotations

from enum import Enum
from typing import Callable, Optional


class Stage(str, Enum):
    """Processing stages."""
    VALIDATE = "validate"
    EXTRACT = "extract"
    PARSE = "parse"
    TRANSLATE = "translate"
    GENERATE = "generate"
    COMPLETE = "complete"


class Progress:
    """Progress tracker with callbacks."""
    
    def __init__(self, total: int = 100, callback: Optional[Callable[[int, str], None]] = None):
        self.total = total
        self.current = 0
        self.callback = callback
        self.stage = "idle"
        self.message = ""
    
    def set_stage(self, stage: str, message: str = "") -> None:
        """Set current processing stage."""
        self.stage = stage
        self.message = message
        self._notify()
    
    def update(self, delta: int = 1, message: str = "") -> None:
        """Update progress by delta."""
        self.current = min(self.current + delta, self.total)
        if message:
            self.message = message
        self._notify()
    
    def set_progress(self, value: int, message: str = "") -> None:
        """Set absolute progress value."""
        self.current = min(max(value, 0), self.total)
        if message:
            self.message = message
        self._notify()
    
    def _notify(self) -> None:
        """Notify callback of progress change."""
        if self.callback:
            self.callback(self.current, self.stage, self.message)
    
    @property
    def percentage(self) -> int:
        """Get progress as percentage."""
        return int(self.current / self.total * 100) if self.total > 0 else 0


class ProgressBar:
    """Console progress bar."""
    
    def __init__(self, total: int = 100, width: int = 40):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, value: int) -> None:
        """Update progress bar."""
        self.current = min(max(value, 0), self.total)
        self._render()
    
    def _render(self) -> None:
        """Render progress bar to console."""
        filled = int(self.width * self.current / self.total) if self.total > 0 else 0
        bar = "█" * filled + "░" * (self.width - filled)
        percentage = int(100 * self.current / self.total) if self.total > 0 else 0
        print(f"\r[{bar}] {percentage}%", end="", flush=True)
    
    def finish(self) -> None:
        """Finish and clear progress bar."""
        self.update(self.total)
        print()  # New line