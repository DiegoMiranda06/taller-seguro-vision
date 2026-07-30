"""Console alert output — used in `mode: demo` (`alert_output: "mock"`).

No hardware dependency at all; this is what makes the demo runnable on any
laptop for the fondeo campaign.
"""

from __future__ import annotations

import logging

from src.alert.base import AlertOutput

logger = logging.getLogger(__name__)


class MockAlertOutput(AlertOutput):
    """Prints the alert state to the console/log instead of driving a relay."""

    def trigger(self, event_type: str) -> None:
        logger.warning("\U0001f534 ALERTA: %s", event_type)

    def clear(self) -> None:
        logger.info("\U0001f7e2 Zona segura")

    def fail_safe(self) -> None:
        logger.critical("\U0001f6a8 FALLA DEL SISTEMA - revisar de inmediato")
