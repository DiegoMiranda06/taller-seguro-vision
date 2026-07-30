"""GPIO relay + Andon light tower alert — `mode: production` only, used
when `StationConfig.alert_output == "gpio"`.

`gpiozero` is imported ONLY inside this module (regla "Imports de hardware
son locales al adapter" en CLAUDE.md): this file is never imported by
`pipeline.py` unless a config actually selects the `gpio` alert output, so
the demo/laptop install never needs it. Not runnable or testable in this
sandbox — no Raspberry Pi, relay, or Andon tower available here; verify
on-device per blueprint Step 10.

`pin` comes straight from `StationConfig.gpio_pin` — never hardcoded
(Reglas No Negociables #4 en CLAUDE.md).
"""

from __future__ import annotations

from src.alert.base import AlertOutput


class GpioAlertOutput(AlertOutput):
    """Drives a relay (-> Andon light tower) through a `gpiozero.LED`."""

    def __init__(self, pin: int) -> None:
        from gpiozero import LED  # local import: Pi-only dependency

        self._led = LED(pin)

    def trigger(self, event_type: str) -> None:
        self._led.on()

    def clear(self) -> None:
        self._led.off()

    def fail_safe(self) -> None:
        # Blink forever (non-blocking, background=True is gpiozero's
        # default) so a crashed process still leaves a visible signal
        # instead of silently going dark/green.
        self._led.blink(on_time=0.5, off_time=0.5)
