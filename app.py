"""Entry point: python app.py --mode demo|production --zona_config <path>

`--mode` is a safety confirmation, not the source of truth: it must match
`StationConfig.mode` in the loaded config file, and everything the pipeline
actually instantiates (camera/detector/alert) comes from the config, never
from a CLI flag or hardcoded branch (Reglas No Negociables #4 en
CLAUDE.md — "Config es la única fuente de variación entre estaciones").
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

from src.config.loader import ConfigError, load_station_config
from src.core.pipeline import (
    Pipeline,
    build_alert_output,
    build_camera_source,
    build_detector,
    resolve_clip_output_root,
)
from src.recorder.clip_writer import ClipWriter
from src.recorder.ring_buffer import RingBuffer

logger = logging.getLogger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Taller Seguro Vision — pipeline de detección de near-miss"
    )
    parser.add_argument(
        "--mode",
        choices=["demo", "production"],
        required=True,
        help="demo: laptop/webcam/mock. production: Raspberry Pi/Picamera2/GPIO.",
    )
    parser.add_argument(
        "--zona_config",
        required=True,
        help="Ruta al JSON de configuración de la estación (ej. config/torno_01.json)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    args = build_arg_parser().parse_args(argv)
    config_path = os.environ.get("STATION_CONFIG_PATH", args.zona_config)

    try:
        config = load_station_config(config_path)
    except ConfigError as exc:
        logger.error("%s", exc)
        return 1

    if config.mode != args.mode:
        logger.error(
            "--mode=%s no coincide con mode=%r en %s — corrígelo antes de continuar "
            "(el modo de la config es la fuente de verdad de qué adapters se usan).",
            args.mode,
            config.mode,
            config_path,
        )
        return 1

    logger.info(
        "Arrancando %s (mode=%s, inference_backend=%s, camera_source=%s, alert_output=%s)",
        config.station_id,
        config.mode,
        config.inference_backend,
        config.camera_source,
        config.alert_output,
    )

    camera = build_camera_source(config)
    detector = build_detector(config)
    alert = build_alert_output(config)
    clip_writer = ClipWriter(output_root=resolve_clip_output_root(config))
    ring_buffer = RingBuffer(max_seconds=config.buffer_pre_seconds)

    pipeline = Pipeline(
        config=config,
        camera=camera,
        detector=detector,
        alert=alert,
        clip_writer=clip_writer,
        ring_buffer=ring_buffer,
    )
    pipeline.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
