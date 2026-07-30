"""Abstract interface every alert output implements.

`pipeline.py` only ever talks to this interface — it decides which concrete
alert output to instantiate based on `StationConfig.alert_output`.

`fail_safe()` exists specifically for Reglas No Negociables #4/#5 (CLAUDE.md
/ blueprint Section 16): if the main loop crashes with an uncaught
exception, `pipeline.py` calls `fail_safe()` before re-raising, so the
relay/light tower is left in a visibly-failing state (on/blinking red)
rather than silently green.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AlertOutput(ABC):
    """Signals risk events to whoever is watching the station."""

    @abstractmethod
    def trigger(self, event_type: str) -> None:
        """Turn the alert on for the given risk event_type (e.g. light
        the red tower / print the console alert)."""

    @abstractmethod
    def clear(self) -> None:
        """Turn the alert off — back to the normal/safe state."""

    @abstractmethod
    def fail_safe(self) -> None:
        """Force a visibly-failing state (e.g. blink or stay red) after an
        uncaught pipeline exception. Must never silently leave the output
        looking "safe"/green."""
